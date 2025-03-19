import requests
import zipfile
import io
import re
from typing import Optional
import os
import base64

class GitHubManager:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.api_base = "https://api.github.com"
        
    def _clean_code_content(self, content: str, file_extension: str) -> str:
        """Clean sensitive data from code content in-memory"""
        sensitive_var = "authKey"
        replacements = {
            '.kt': 'System.getenv("REPLACEMENT_KEY")',
            '.java': 'System.getenv("REPLACEMENT_KEY")',
            '.py': 'os.getenv("REPLACEMENT_KEY")',
            '.js': 'process.env.REPLACEMENT_KEY',
            '.ts': 'process.env.REPLACEMENT_KEY'
        }

        pattern = re.compile(rf'({sensitive_var}\s*=\s*)(["\'].*?["\']|\S+)')
        if replacement := replacements.get(file_extension):
            return pattern.sub(rf'\1{replacement}', content)
        return content

    def create_repository(self, repo_name: str, private: bool = False) -> Optional[str]:
        """Create a new GitHub repository"""
        url = f"{self.api_base}/user/repos"
        print(url)
        data = {"name": repo_name, "private": private}
        print(data)
        
        
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()['html_url']
        except requests.exceptions.RequestException as e:
            print(f"Repository creation failed: {str(e)}")
            return None

    def create_file(self, repo_owner: str, repo_name: str, 
               file_path: str, content: str, 
               message: str = "Initial commit") -> bool:
        """Create a file in a GitHub repository"""
        
        
        url = f"{self.api_base}/repos/{repo_owner}/{repo_name}/contents/{file_path}"
        data = {
            "message": message,
            "content": base64.b64encode(content.encode('utf-8')).decode('ascii'),
            "encoding": "base64"
        }

        try:
            response = requests.put(url, json=data, headers=self.headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"File creation failed for {file_path}: {str(e)}")
            return False
    
    def _is_binary(self, content: bytes) -> bool:
        """Check if content is likely binary by looking for null bytes or high concentration of non-ASCII chars"""
        # Check for null bytes which indicate binary content
        if b'\x00' in content:
            return True
        
        # Check text/binary ratio
        text_chars = len([b for b in content if 32 <= b <= 127 or b in (9, 10, 13)])
        return text_chars / len(content) < 0.7 if content else False

    def create_file_with_encoding(self, repo_owner: str, repo_name: str, 
                    file_path: str, content: str, encoding: str,
                    message: str = "Initial commit") -> bool:
        """Create a file in a GitHub repository with specified encoding"""
        url = f"{self.api_base}/repos/{repo_owner}/{repo_name}/contents/{file_path}"
        data = {
            "message": message,
            "content": content,
            "encoding": encoding
        }

        try:
            response = requests.put(url, json=data, headers=self.headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"File creation failed for {file_path}: {str(e)}")
            return False

    def push_zip_to_repo(self, repo_owner: str, repo_name: str, 
                        zip_content: bytes, commit_message: str = "Initial commit") -> bool:
        """Push zip content directly to GitHub repository"""
        # Create repository first
        if not self.create_repository(repo_name, private=False):
            return False  # Only return False if repo creation fails

        # Process zip file in memory
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_ref:
                skipped_files = []  # Track skipped files
                
                for file_info in zip_ref.infolist():
                    if file_info.is_dir():
                        continue  # Skip directories

                    # Fix path issue - remove project root folder if it's duplicated
                    file_path = file_info.filename
                    parts = file_path.split('/')
                    if parts and parts[0] == repo_name:
                        # Remove the duplicated root folder
                        file_path = '/'.join(parts[1:])
                    
                    # Skip empty paths after correction
                    if not file_path:
                        continue

                    # Read file content as bytes (don't decode binary files)
                    content = zip_ref.read(file_info)
                    
                    # Handle text vs binary files differently
                    is_binary = self._is_binary(content)
                    
                    if is_binary:
                        # For binary files, use base64 encoding for GitHub API
                        import base64
                        encoded_content = base64.b64encode(content).decode('ascii')
                        encoding = "base64"
                    else:
                        # For text files, try to decode and clean
                        try:
                            decoded_content = content.decode('utf-8')
                            file_ext = os.path.splitext(file_info.filename)[1]
                            cleaned_content = self._clean_code_content(decoded_content, file_ext)
                            
                            # For text files, use regular encoding
                            import base64
                            encoded_content = base64.b64encode(cleaned_content.encode('utf-8')).decode('ascii')
                            encoding = "base64"
                        except UnicodeDecodeError:
                            # If decoding fails, treat as binary
                            import base64
                            encoded_content = base64.b64encode(content).decode('ascii')
                            encoding = "base64"

                    # Try to create file, but continue even if it fails
                    try:
                        success = self.create_file_with_encoding(repo_owner, repo_name, 
                                                file_path, encoded_content, encoding,
                                                commit_message)
                        if not success:
                            skipped_files.append(file_path)
                            print(f"Skipping file: {file_path} - Creation failed")
                    except Exception as e:
                        skipped_files.append(file_path)
                        print(f"Skipping file: {file_path} - Error: {str(e)}")
                
                # Log summary of skipped files
                if skipped_files:
                    print(f"Repository created but {len(skipped_files)} files were skipped")
                
                return True  # Return True as long as the repo was created
                
        except zipfile.BadZipFile:
            print("Invalid ZIP file format")
            return False
        except Exception as e:
            print(f"Error processing ZIP file: {str(e)}")
            return False
            
        

