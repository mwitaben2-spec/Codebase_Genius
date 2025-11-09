import os
import shutil
import stat
from git import Repo, GitCommandError

IGNORE_DIRS = ['.git', 'node_modules', '.venv', 'venv', '__pycache__', '.vscode']
IGNORE_FILES = ['.DS_Store']

def _remove_readonly(func, path, exc_info):
    """
    Error handler for shutil.rmtree.
    If the error is due to a read-only file, it changes the permissions
    and tries to remove it again. This is crucial for Windows.
    """
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    else:
        raise

class RepoMapper:
    def __init__(self, github_url, doc_genie=None):
        self.github_url = github_url
        self.repo_name = github_url.split('/')[-1].replace('.git', '')
        self.local_repo_path = f"./temp_repo_{self.repo_name}"
        self.file_tree = ""
        self.doc_genie = doc_genie 
        self.readme_content = "" 

    def clone_repo(self):
        """
        Clones the public GitHub repository to a local path.
        Returns True on success, False on failure.
        """
        try:
            if os.path.exists(self.local_repo_path):
                print(f"Removing old repo at {self.local_repo_path}...")
                shutil.rmtree(self.local_repo_path, onerror=_remove_readonly)
                print("Old repo removed successfully.")
                
            print(f"Cloning {self.github_url} into {self.local_repo_path}...")
            Repo.clone_from(self.github_url, self.local_repo_path)
            print("Clone successful.")
            
            readme_path = os.path.join(self.local_repo_path, 'README.md')
            if os.path.exists(readme_path):
                with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                    self.readme_content = f.read()
            else:
                self.readme_content = "No README.md file found."

            
            return True
        except GitCommandError as e:
            print(f"Error cloning repo: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred during cloning or cleanup: {e}")
            return False

    def build_file_tree(self):
        """
        Builds a file-tree representation of the cloned repo.
        Ignores specified directories and files.
        """
        tree_str = f"{self.repo_name}/\n"
        
        for root, dirs, files in os.walk(self.local_repo_path, topdown=True):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            files = [f for f in files if f not in IGNORE_FILES]

            relative_path = os.path.relpath(root, self.local_repo_path)
            if relative_path == ".":
                level = 0
            else:
                level = relative_path.count(os.sep) + 1
            
            indent = "    " * level + "|-- "

            for d in dirs:
                tree_str += f"{indent}{d}/\n"
            
            for f in files:
                tree_str += f"{indent}{f}\n"

        self.file_tree = tree_str
        return tree_str

    def get_readme_summary(self):
        """
        Summarizes the README using the DocGenie agent.
        """
        if self.doc_genie:
           
            return self.doc_genie.summarize_readme(self.readme_content)
        else:
  
            print("Warning: DocGenie not provided. Using placeholder summary.")
            return "This is a placeholder summary (DocGenie not active)."