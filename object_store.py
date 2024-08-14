import os
import hashlib
import zlib

def compute_hash(data, obj_type):
    """
    Computes the SHA-1 hash of the given data and returns the hash.

    Args:
        data (bytes): The content to be hashed.
        obj_type (str): The type of the object (e.g., 'blob', 'tree', 'commit').

    Returns:
        str: The SHA-1 hash as a hexadecimal string.
    """
    header = f'{obj_type} {len(data)}'.encode()
    full_data = header + b'\x00' + data
    sha1_hash = hashlib.sha1(full_data).hexdigest()
    return sha1_hash, full_data

def store_object(data, obj_type, repo_path):
    """
    Compresses and stores an object in the .git/objects directory.

    Args:
        data (bytes): The content of the object.
        obj_type (str): The type of the object.
        repo_path (str): Path to the repository.

    Returns:
        str: The SHA-1 hash of the stored object.
    """
    sha1_hash, full_data = compute_hash(data, obj_type)
    object_dir = os.path.join(repo_path, '.git', 'objects', sha1_hash[:2])
    object_path = os.path.join(object_dir, sha1_hash[2:])

    if not os.path.exists(object_path):
        os.makedirs(object_dir, exist_ok=True)
        with open(object_path, 'wb') as obj_file:
            obj_file.write(zlib.compress(full_data))

    return sha1_hash

def retrieve_object(sha1_hash, repo_path):
    """
    Retrieves and decompresses an object from the .git/objects directory.

    Args:
        sha1_hash (str): The SHA-1 hash of the object to retrieve.
        repo_path (str): Path to the repository.

    Returns:
        tuple: A tuple containing the object type and data.
    """
    object_path = os.path.join(repo_path, '.git', 'objects', sha1_hash[:2], sha1_hash[2:])
    if not os.path.exists(object_path):
        raise FileNotFoundError(f"Object {sha1_hash} not found")

    with open(object_path, 'rb') as obj_file:
        compressed_data = obj_file.read()

    full_data = zlib.decompress(compressed_data)
    header, data = full_data.split(b'\x00', 1)
    obj_type, _ = header.decode().split()

    return obj_type, data

if __name__ == "__main__":
    repo_path = "."  
    data = b"Example data for testing."
    obj_type = "blob"

    sha1_hash = store_object(data, obj_type, repo_path)
    print(f"Object stored with SHA-1: {sha1_hash}")

    retrieved_type, retrieved_data = retrieve_object(sha1_hash, repo_path)
    print(f"Retrieved object type: {retrieved_type}")
    print(f"Retrieved object data: {retrieved_data.decode()}")
