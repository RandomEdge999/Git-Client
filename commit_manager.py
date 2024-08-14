import os
import time
import struct
from object_store import store_object, retrieve_object
from index_manager import read_index

def write_tree(repo_path):
    """
    Creates a tree object from the current index entries and stores it.

    Args:
        repo_path (str): Path to the repository.

    Returns:
        str: The SHA-1 hash of the tree object.
    """
    entries = read_index(repo_path)
    tree_entries = []

    for entry in entries:
        # Git expects the mode to be in octal, and the format is 'mode path\0 sha1'
        mode_path = f'{entry.mode:o} {entry.path}'.encode()
        tree_entry = mode_path + b'\x00' + entry.sha1
        tree_entries.append(tree_entry)

    tree_data = b''.join(tree_entries)
    tree_hash = store_object(tree_data, 'tree', repo_path)
    return tree_hash

def create_commit(message, author, repo_path):
    """
    Creates a commit object from the current index state.

    Args:
        message (str): The commit message.
        author (str): The author of the commit.
        repo_path (str): Path to the repository.

    Returns:
        str: The SHA-1 hash of the commit object.
    """
    tree_hash = write_tree(repo_path)
    parent_commit = get_latest_commit(repo_path)

    timestamp = int(time.mktime(time.localtime()))
    utc_offset = -time.timezone
    author_time = '{} {}{:02}{:02}'.format(
        timestamp,
        '+' if utc_offset > 0 else '-',
        abs(utc_offset) // 3600,
        (abs(utc_offset) // 60) % 60
    )

    commit_lines = [
        f'tree {tree_hash}',
        f'parent {parent_commit}' if parent_commit else '',
        f'author {author} {author_time}',
        f'committer {author} {author_time}',
        '',
        message,
        ''
    ]

    commit_data = '\n'.join(commit_lines).encode()
    commit_hash = store_object(commit_data, 'commit', repo_path)

    update_ref(commit_hash, repo_path)
    print(f"Committed to master: {commit_hash[:7]}")
    return commit_hash

def get_latest_commit(repo_path):
    """
    Retrieves the latest commit hash from the master branch.

    Args:
        repo_path (str): Path to the repository.

    Returns:
        str: The SHA-1 hash of the latest commit, or None if no commits exist.
    """
    master_ref_path = os.path.join(repo_path, '.git', 'refs', 'heads', 'master')
    if not os.path.exists(master_ref_path):
        return None

    with open(master_ref_path, 'r') as f:
        commit_hash = f.read().strip()

    return commit_hash

def update_ref(commit_hash, repo_path):
    """
    Updates the HEAD reference to point to the latest commit.

    Args:
        commit_hash (str): The SHA-1 hash of the latest commit.
        repo_path (str): Path to the repository.
    """
    master_ref_path = os.path.join(repo_path, '.git', 'refs', 'heads', 'master')
    with open(master_ref_path, 'w') as f:
        f.write(commit_hash + '\n')

def find_tree_objects(tree_sha1, repo_path):
    """
    Return a set of SHA-1 hashes for all objects in the given tree.

    Args:
        tree_sha1 (str): The SHA-1 hash of the tree.
        repo_path (str): The path to the repository.

    Returns:
        set: A set of SHA-1 hashes of all objects referenced by the tree.
    """
    objects = {tree_sha1}
    _, tree_data = retrieve_object(tree_sha1, repo_path)
    
    i = 0
    while i < len(tree_data):
        mode_end = tree_data.find(b' ', i)
        sha_start = tree_data.find(b'\x00', mode_end) + 1
        sha1 = tree_data[sha_start:sha_start + 20]
        sha1_hex = sha1.hex()
        objects.add(sha1_hex)
        
        i = sha_start + 20
        
        # Recursively find objects in trees (subdirectories)
        obj_type, _ = retrieve_object(sha1_hex, repo_path)
        if obj_type == 'tree':
            objects.update(find_tree_objects(sha1_hex, repo_path))
    
    return objects

def find_commit_objects(commit_sha1, repo_path):
    """
    Return a set of SHA-1 hashes for all objects in this commit, its tree, its parents,
    and the hash of the commit itself.
    
    Args:
        commit_sha1 (str): The SHA-1 hash of the commit.
        repo_path (str): The path to the repository.
    
    Returns:
        set: A set of SHA-1 hashes of all objects referenced by the commit.
    """
    objects = {commit_sha1}
    obj_type, commit_data = retrieve_object(commit_sha1, repo_path)
    assert obj_type == 'commit', 'Expected a commit object'
    
    lines = commit_data.decode().splitlines()
    tree_hash = next(line[5:45] for line in lines if line.startswith('tree '))
    objects.update(find_tree_objects(tree_hash, repo_path))
    
    parent_hashes = [line[7:47] for line in lines if line.startswith('parent ')]
    for parent_hash in parent_hashes:
        objects.update(find_commit_objects(parent_hash, repo_path))
    
    return objects

if __name__ == "__main__":
    repo_path = "."  
    message = "Initial commit"
    author = "Author Name <author@example.com>"

    commit_hash = create_commit(message, author, repo_path)
    print(f"Created commit {commit_hash}")
