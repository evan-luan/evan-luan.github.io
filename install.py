import os
import stat
import subprocess

# The content of your pre-commit hook script
PRE_COMMIT_SCRIPT_CONTENT = """#!/usr/bin/env python3

import subprocess
import sys

# Define the only allowed name and email
ALLOWED_NAME = "Evan Luan"
ALLOWED_EMAIL = "evan.luan@example.com"

def get_git_config(key):
    \"\"\"
    Retrieves a Git configuration value.
    \"\"\"
    try:
        return subprocess.check_output(['git', 'config', key]).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        return None

def main():
    \"\"\"
    Main function to check committer's name and email.
    \"\"\"
    committer_name = get_git_config('user.name')
    committer_email = get_git_config('user.email')

    if committer_name == ALLOWED_NAME and committer_email == ALLOWED_EMAIL:
        print("Committer name and email matched. Commit accepted.")
        sys.exit(0) # Exit with 0 for success
    else:
        print("Error: Committer name or email does not match the allowed user.")
        print(f"  Expected Name: '{ALLOWED_NAME}'")
        print(f"  Expected Email: '{ALLOWED_EMAIL}'")
        print(f"  Found Name:    '{committer_name}'")
        print(f"  Found Email:   '{commmitter_email}'")
        sys.exit(1) # Exit with 1 for failure

if __name__ == '__main__':
    main()
"""

def find_git_root():
    """
    Finds the root directory of the current Git repository.
    Returns None if not in a Git repository.
    """
    try:
        # Run git rev-parse --show-toplevel to get the repo root
        repo_root = subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel'],
            stderr=subprocess.PIPE
        ).decode('utf-8').strip()
        return repo_root
    except subprocess.CalledProcessError:
        return None

def install_pre_commit_hook():
    git_root = find_git_root()

    if not git_root:
        print("Error: Not in a Git repository. Please run this script from within a Git repo.")
        return

    hooks_dir = os.path.join(git_root, '.git', 'hooks')
    pre_commit_path = os.path.join(hooks_dir, 'pre-commit')

    # Ensure the .git/hooks directory exists
    os.makedirs(hooks_dir, exist_ok=True)

    if os.path.exists(pre_commit_path):
        print(f"The pre-commit hook already exists at: {pre_commit_path}")
        print("Installation skipped. Please check its content and permissions manually if needed.")
    else:
        try:
            with open(pre_commit_path, 'w') as f:
                f.write(PRE_COMMIT_SCRIPT_CONTENT)
            print(f"Pre-commit hook installed successfully at: {pre_commit_path}")

            # Attempt to set executable permission
            print("\nAttempting to set executable permissions for the pre-commit hook...")
            try:
                # Use os.chmod directly, as subprocess.run(['sudo', 'chmod...'])
                # would require a password prompt from sudo itself.
                # If the user doesn't have write permission to the file, this will fail.
                # In most cases, if they can write the file, they can set its permissions.
                current_permissions = os.stat(pre_commit_path).st_mode
                os.chmod(pre_commit_path, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                print("Executable permissions set.")
            except OSError as e:
                print(f"Warning: Could not automatically set executable permissions: {e}")
                print("Please set executable permissions manually using:")
                print(f"  chmod +x {pre_commit_path}")
                print("  (You might need to use 'sudo chmod +x ...' if permissions are restricted)")

        except IOError as e:
            print(f"Error: Could not write the pre-commit file to {pre_commit_path}. Reason: {e}")
            print("Please check your file permissions for the .git/hooks directory.")

if __name__ == '__main__':
    install_pre_commit_hook()