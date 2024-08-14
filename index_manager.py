import os
import struct
import hashlib
import collections
from object_store import store_object

# Define the IndexEntry namedtuple to store information about each file in the index
IndexEntry = collections.namedtuple('IndexEntry', [
    'ctime_s', 'ctime_n', 'mtime_s', 'mtime_n', 'dev', 'ino', 'mode',
    'uid', 'gid', 'size', 'sha1', 'flags', 'path',
])

def read_index(repo_path):
    """
    Reads the index file (.git/index) and returns a list of IndexEntry objects.

    Args:
        repo_path (str): Path to the repository.

    Returns:
        list: A list of IndexEntry objects.
    """
    index_file_path = os.path.join(repo_path, '.git', 'index')
    if not os.path.exists(index_file_path):
        return []

    with open(index_file_path, 'rb') as f:
        data = f.read()

    signature, version, num_entries = struct.unpack('!4sLL', data[:12])
    if signature != b'DIRC':
        raise ValueError('Invalid index file signature')
    if version != 2:
        raise ValueError('Unsupported index file version')

    entries = []
    entry_data = data[12:]
    i = 0

    while i + 62 <= len(entry_data):
        fields = struct.unpack('!LLLLLLLLLL20sH', entry_data[i:i + 62])
        path_end = entry_data.index(b'\x00', i + 62)
        path = entry_data[i + 62:path_end].decode()
        entry = IndexEntry(*(fields + (path,)))
        entries.append(entry)
        entry_len = ((62 + len(path) + 8) // 8) * 8
        i += entry_len

    return entries

def write_index(entries, repo_path):
    """
    Writes the list of IndexEntry objects to the index file (.git/index).

    Args:
        entries (list): A list of IndexEntry objects.
        repo_path (str): Path to the repository.
    """
    index_file_path = os.path.join(repo_path, '.git', 'index')
    data = struct.pack('!4sLL', b'DIRC', 2, len(entries))

    for entry in entries:
        path_bytes = entry.path.encode()
        entry_data = struct.pack(
            '!LLLLLLLLLL20sH',
            entry.ctime_s & 0xFFFFFFFF, entry.ctime_n & 0xFFFFFFFF,
            entry.mtime_s & 0xFFFFFFFF, entry.mtime_n & 0xFFFFFFFF,
            entry.dev & 0xFFFFFFFF, entry.ino & 0xFFFFFFFF,
            entry.mode & 0xFFFFFFFF, entry.uid & 0xFFFFFFFF, entry.gid & 0xFFFFFFFF,
            entry.size & 0xFFFFFFFF, entry.sha1, entry.flags
        ) + path_bytes + b'\x00'
        # Pad to multiple of 8 bytes
        data += entry_data + b'\x00' * ((62 + len(path_bytes) + 8) // 8 * 8 - len(entry_data))

    # Add the SHA-1 checksum
    sha1_checksum = hashlib.sha1(data).digest()
    data += sha1_checksum

    with open(index_file_path, 'wb') as f:
        f.write(data)

def add_to_index(paths, repo_path):
    """
    Adds files to the index (staging area).

    Args:
        paths (list): List of file paths to add to the index.
        repo_path (str): Path to the repository.
    """
    entries = {entry.path: entry for entry in read_index(repo_path)}

    for path in paths:
        with open(path, 'rb') as f:
            data = f.read()
        sha1_hash = store_object(data, 'blob', repo_path)
        stat_info = os.stat(path)
        entry = IndexEntry(
            int(stat_info.st_ctime) & 0xFFFFFFFF, 0,
            int(stat_info.st_mtime) & 0xFFFFFFFF, 0,
            stat_info.st_dev & 0xFFFFFFFF, stat_info.st_ino & 0xFFFFFFFF,
            stat_info.st_mode & 0xFFFFFFFF, stat_info.st_uid & 0xFFFFFFFF, stat_info.st_gid & 0xFFFFFFFF,
            stat_info.st_size & 0xFFFFFFFF, sha1_hash.encode(), 0,
            path
        )
        entries[path] = entry

    write_index(list(entries.values()), repo_path)
    print(f"Added {len(paths)} file(s) to the index.")

def list_index(repo_path):
    """
    Lists the files currently staged in the index.

    Args:
        repo_path (str): Path to the repository.
    """
    entries = read_index(repo_path)
    for entry in entries:
        print(f"{entry.mode:o} {entry.sha1.hex()} {entry.path}")

if __name__ == "__main__":
    repo_path = "."  
    add_to_index(["example.txt"], repo_path)
    list_index(repo_path)
