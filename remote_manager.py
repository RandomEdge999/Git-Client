import os
import urllib.request
import hashlib
import struct
import zlib
from object_store import compute_hash, store_object
from index_manager import read_index
from commit_manager import get_latest_commit, find_commit_objects


def http_request(url, username, password, data=None):
    """
    Makes an authenticated HTTP request to the given URL.

    Args:
        url (str): The URL for the HTTP request.
        username (str): The username for authentication.
        password (str): The password for authentication.
        data (bytes): The data to be sent (for POST requests).

    Returns:
        bytes: The response data.
    """
    password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, url, username, password)
    auth_handler = urllib.request.HTTPBasicAuthHandler(password_manager)
    opener = urllib.request.build_opener(auth_handler)

    with opener.open(url, data=data) as response:
        return response.read()

def get_remote_master_hash(git_url, username, password):
    """
    Retrieves the commit hash of the remote master branch.

    Args:
        git_url (str): The remote Git repository URL.
        username (str): The username for authentication.
        password (str): The password for authentication.

    Returns:
        str: The SHA-1 hash of the remote master commit, or None if no commits exist.
    """
    url = f"{git_url}/info/refs?service=git-receive-pack"
    response = http_request(url, username, password)

    lines = response.split(b'\n')
    for line in lines:
        if line.startswith(b"00"):
            continue
        if b"refs/heads/master" in line:
            remote_hash = line.split()[0].decode()
            return remote_hash
    return None

def find_missing_objects(local_sha1, remote_sha1, repo_path):
    """
    Finds the set of objects that are present in the local commit but missing in the remote.

    Args:
        local_sha1 (str): The SHA-1 hash of the local commit.
        remote_sha1 (str): The SHA-1 hash of the remote commit.
        repo_path (str): Path to the repository.

    Returns:
        set: A set of SHA-1 hashes of the missing objects.
    """
    local_objects = find_commit_objects(local_sha1, repo_path)
    if remote_sha1:
        remote_objects = find_commit_objects(remote_sha1, repo_path)
        return local_objects - remote_objects
    return local_objects

def create_pack(objects, repo_path):
    """
    Creates a pack file containing all the specified objects.

    Args:
        objects (set): A set of SHA-1 hashes of objects to include in the pack.
        repo_path (str): Path to the repository.

    Returns:
        bytes: The packed data ready to be sent to the remote server.
    """
    header = struct.pack('!4sLL', b'PACK', 2, len(objects))
    body = b''

    for sha1 in sorted(objects):
        obj_type, data = retrieve_object(sha1, repo_path)
        packed_obj = pack_object(obj_type, data)
        body += packed_obj

    full_data = header + body
    sha1_digest = hashlib.sha1(full_data).digest()

    return full_data + sha1_digest

def retrieve_object(sha1_hash, repo_path):
    """
    Retrieves an object from the repository by its SHA-1 hash.

    Args:
        sha1_hash (str): The SHA-1 hash of the object to retrieve.
        repo_path (str): Path to the repository.

    Returns:
        tuple: A tuple containing the object type and its data.
    """
    object_path = os.path.join(repo_path, '.git', 'objects', sha1_hash[:2], sha1_hash[2:])
    with open(object_path, 'rb') as f:
        compressed_data = f.read()

    decompressed_data = zlib.decompress(compressed_data)
    header, data = decompressed_data.split(b'\x00', 1)
    obj_type = header.decode().split()[0]

    return obj_type, data

def pack_object(obj_type, data):
    """
    Packs an object into the pack file format.

    Args:
        obj_type (str): The type of the object (e.g., 'blob', 'tree', 'commit').
        data (bytes): The content of the object.

    Returns:
        bytes: The packed object data.
    """
    type_num = {'commit': 1, 'tree': 2, 'blob': 3}[obj_type]
    size = len(data)

    header = []
    header.append((type_num << 4) | (size & 0x0f))
    size >>= 4

    while size:
        header.append(size & 0x7f | 0x80)
        size >>= 7

    return bytes(header) + zlib.compress(data)

def push(git_url, username, password, repo_path):
    """
    Pushes the local master branch to the remote Git repository.

    Args:
        git_url (str): The remote Git repository URL.
        username (str): The username for authentication.
        password (str): The password for authentication.
        repo_path (str): Path to the repository.

    Returns:
        None
    """
    local_sha1 = get_latest_commit(repo_path)
    remote_sha1 = get_remote_master_hash(git_url, username, password)
    missing_objects = find_missing_objects(local_sha1, remote_sha1, repo_path)

    pack_data = create_pack(missing_objects, repo_path)
    lines = [
        f"{remote_sha1 or '0' * 40} {local_sha1} refs/heads/master\x00report-status",
    ]
    data = build_pkt_line_data(lines) + pack_data

    url = f"{git_url}/git-receive-pack"
    response = http_request(url, username, password, data=data)

    if b'unpack ok' in response:
        print("Push successful")
    else:
        print("Push failed")

def build_pkt_line_data(lines):
    """
    Builds pkt-line data format from given lines.

    Args:
        lines (list): A list of lines to convert into pkt-line format.

    Returns:
        bytes: The pkt-line formatted data.
    """
    pkt_lines = []
    for line in lines:
        pkt_lines.append(f'{len(line) + 4:04x}'.encode() + line.encode())
    pkt_lines.append(b'0000')
    return b''.join(pkt_lines)

if __name__ == "__main__":
    repo_path = "." 
    git_url = "https://your_git_repo_url"
    username = "your_username"
    password = "your_password"

    push(git_url, username, password, repo_path)
