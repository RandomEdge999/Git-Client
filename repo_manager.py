import os
import sys

def create_repo(repo_path):
    """
    Initializes a new repository by creating the necessary .git directory
    and its subdirectories.

    Args:
        repo_path (str): Path to the new repository.

    Returns:
        None
    """
    try:
        os.makedirs(os.path.join(repo_path, '.git', 'objects'))
        os.makedirs(os.path.join(repo_path, '.git', 'refs', 'heads'))

        with open(os.path.join(repo_path, '.git', 'HEAD'), 'wb') as head_file:
            head_file.write(b'ref: refs/heads/master')

        print(f'Repository initialized at {repo_path}')
    except Exception as e:
        print(f"Error initializing repository: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: git_clone.py <repo_path>", file=sys.stderr)
        sys.exit(1)

    repo_path = sys.argv[1]
    create_repo(repo_path)
