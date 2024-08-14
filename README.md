# Git Client Project

This project implements a simplified version of Git, providing basic functionality such as initializing a repository, adding files to the staging area, committing changes, and pushing to a remote repository. The project is written in Python and mimics core Git functionalities with a focus on simplicity and educational purposes.

## Features

- **Initialize a Repository**: Create a new Git-like repository with the necessary directory structure.
- **Add Files to Staging**: Stage files in the repository to prepare them for committing.
- **Commit Changes**: Save the current state of the repository by creating a commit.
- **Push to Remote**: Push commits to a remote repository (e.g., GitHub).

## Project Structure

- **`git_clone.py`**: The main script that handles command-line interface (CLI) commands.
- **`repo_manager.py`**: Manages repository initialization and basic repository structure.
- **`object_store.py`**: Handles object creation, hashing, and storage within the `.git` directory.
- **`index_manager.py`**: Manages the staging area (index), including adding files and writing the index file.
- **`commit_manager.py`**: Handles the creation of commit objects and manages commit history.
- **`remote_manager.py`**: Manages the process of pushing commits to a remote Git repository.

## Installation

### Prerequisites

- **Python**: Make sure Python 3.6 or higher is installed on your system.

### Clone the Repository

To clone the repository to your local machine, use:

```bash
git clone https://github.com/RandomEdge999/Git-Client.git
```
### Setup
Navigate to the Project Directory:

```bash
cd "/c/Users/aleem/final_project/Git Client"
```

## Usage
 ### 1. Initialize a Repository
 
 ```bash
 python git_clone.py init <repo_path>
```
Example:
 ```bash
 python git_clone.py init myrepo
```
### 2. Add Files to the Staging Area 

To add files to the staging area:
```bash
python git_clone.py add <file1> <file2> ... --repo <repo_path>
```
Example:
 ```bash
python git_clone.py add test_file.txt --repo myrepo
```
### 3. Check the Status of the Repository
To check the current status of the repository:
```bash
python git_clone.py status --repo <repo_path>
```
Example:
```bash
python git_clone.py status --repo myrepo
```
### 4. Commit Changes
To commit changes with a message and author:
```bash
    python git_clone.py commit -m "<message>" --author "<Author Name <email>>" --repo <repo_path>
```
Example:
```bash
python git_clone.py commit -m "Initial commit" --author "John Doe <john@example.com>" --repo myrepo
```
### 5. Push to a Remote Repository
To push commits to a remote repository:
```bash
python git_clone.py push <remote_repo_url> --username <username> --password <password> --repo <repo_path>
```
Example:
```bash
python git_clone.py push https://github.com/yourusername/my_project.git --username yourusername --password yourpassword --repo myrepo
```
## Contributing
Contributions are welcome! Please follow these steps:

    1. Fork the repository.
    2. Create a new branch (git checkout -b feature/your-feature-name).
    3. Make your changes and commit them (git commit -m 'Add some feature').
    4. Push to the branch (git push origin feature/your-feature-name).
    5. Open a pull request.


## License

 This project is licensed under the [MIT](https://github.com/RandomEdge999/Git-Client/blob/3beff57c2ea8bb90b6480f8efd227f760e9b7b83/LICENSE) License. 

 ## Acknowledgments
This project is inspired by the core functionalities of Git, aiming to provide a simple educational tool to understand how Git works under the hood.





 
