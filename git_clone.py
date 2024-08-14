import argparse
import sys
from repo_manager import create_repo
from index_manager import add_to_index, list_index
from commit_manager import create_commit
from remote_manager import push

def init(args):
    """
    Handle the 'init' command to initialize a new repository.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    create_repo(args.repo)

def add(args):
    """
    Handle the 'add' command to add files to the index (staging area).

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    add_to_index(args.files, args.repo)

def commit(args):
    """
    Handle the 'commit' command to create a new commit.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    create_commit(args.message, args.author, args.repo)

def status(args):
    """
    Handle the 'status' command to list files in the index.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    list_index(args.repo)

def push_command(args):
    """
    Handle the 'push' command to push commits to a remote repository.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    push(args.url, args.username, args.password, args.repo)

def main():
    parser = argparse.ArgumentParser(description='A simplified Git-like system.')
    subparsers = parser.add_subparsers(title='Commands', dest='command')

    # Init command
    parser_init = subparsers.add_parser('init', help='Initialize a new repository.')
    parser_init.add_argument('repo', help='The path to the repository.')
    parser_init.set_defaults(func=init)

    # Add command
    parser_add = subparsers.add_parser('add', help='Add files to the staging area.')
    parser_add.add_argument('files', nargs='+', help='List of files to add.')
    parser_add.add_argument('--repo', default='.', help='The path to the repository.')
    parser_add.set_defaults(func=add)

    # Commit command
    parser_commit = subparsers.add_parser('commit', help='Commit changes.')
    parser_commit.add_argument('-m', '--message', required=True, help='The commit message.')
    parser_commit.add_argument('--author', required=True, help='The author of the commit.')
    parser_commit.add_argument('--repo', default='.', help='The path to the repository.')
    parser_commit.set_defaults(func=commit)

    # Status command
    parser_status = subparsers.add_parser('status', help='Show the status of the repository.')
    parser_status.add_argument('--repo', default='.', help='The path to the repository.')
    parser_status.set_defaults(func=status)

    # Push command
    parser_push = subparsers.add_parser('push', help='Push commits to a remote repository.')
    parser_push.add_argument('url', help='The remote repository URL.')
    parser_push.add_argument('--username', required=True, help='Username for authentication.')
    parser_push.add_argument('--password', required=True, help='Password for authentication.')
    parser_push.add_argument('--repo', default='.', help='The path to the repository.')
    parser_push.set_defaults(func=push_command)

    # Parse arguments and call appropriate function
    args = parser.parse_args()
    if args.command:
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
