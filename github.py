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

    # In GitHubManager class
    def push_zip_to_repo(self, repo_owner: str, repo_name: str, 
                        zip_content: bytes, commit_message: str = "Initial commit",
                        status_container=None) -> bool:
        """Push zip content directly to GitHub repository with detailed status"""
        # Create status columns if container provided
        if status_container:
            col1, col2, col3 = status_container.columns([3, 5, 2])
            col1.markdown("**File**")
            col2.markdown("**Status**")
            col3.markdown("**Progress**")
        
        total_files = 0
        success_count = 0
        error_count = 0
        
        # First pass to count files
        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_ref:
            total_files = sum(1 for f in zip_ref.infolist() if not f.is_dir())
        
        # Create repository first
        if status_container:
            status_container.info(f"📦 Creating repository {repo_name}...")
        if not self.create_repository(repo_name, private=False):
            if status_container:
                status_container.error("Repository creation failed!")
            return False

        # Process zip file in memory
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_ref:
                progress_bar = status_container.progress(0) if status_container else None
                current_file = 0
                
                for file_info in zip_ref.infolist():
                    if file_info.is_dir():
                        continue

                    current_file += 1
                    file_path = self._clean_file_path(file_info.filename, repo_name)
                    if not file_path:
                        continue

                    # Update progress
                    if status_container:
                        progress = current_file / total_files
                        progress_bar.progress(min(progress, 1.0))

                    # Create status row
                    if status_container:
                        file_col, status_col, _ = status_container.columns([3, 5, 2])
                        file_col.markdown(f"`{file_path}`")
                        status_placeholder = status_col.empty()

                    try:
                        # File processing logic...
                        success = self._process_file(repo_owner, repo_name, file_info, 
                                                zip_ref, commit_message, status_placeholder)
                        
                        if success:
                            success_count += 1
                            if status_container:
                                status_placeholder.success("✅ Uploaded")
                        else:
                            error_count += 1
                            if status_container:
                                status_placeholder.warning("⚠️ Skipped")

                    except Exception as e:
                        error_count += 1
                        if status_container:
                            status_placeholder.error(f"❌ Failed: {str(e)}")
                        continue

                # Final status
                if status_container:
                    progress_bar.empty()
                    status_container.success(f"""
                        🚀 Push completed!
                        - Successfully uploaded: {success_count} files
                        - Skipped/Failed: {error_count} files
                        Repository: https://github.com/{repo_owner}/{repo_name}
                    """)
                    
                return True
                
        except zipfile.BadZipFile:
            if status_container:
                status_container.error("❌ Invalid ZIP file format")
            return False
        except Exception as e:
            if status_container:
                status_container.error(f"❌ Error processing ZIP file: {str(e)}")
            return False

    # Helper methods
    def _clean_file_path(self, path: str, repo_name: str) -> str:
        """Clean file paths from ZIP structure"""
        parts = path.split('/')
        if parts and parts[0] == repo_name:
            return '/'.join(parts[1:])
        return path

    def _process_file(self, repo_owner, repo_name, file_info, zip_ref, 
                    commit_message, status_placeholder):
        """Process individual file with status updates"""
        file_path = self._clean_file_path(file_info.filename, repo_name)
        content = zip_ref.read(file_info)
        
        if status_placeholder:
            status_placeholder.info("🔍 Analyzing file...")
        
        # Binary check
        if self._is_binary(content):
            if status_placeholder:
                status_placeholder.info("📦 Detected binary file...")
            encoded_content = base64.b64encode(content).decode('ascii')
            encoding = "base64"
        else:
            if status_placeholder:
                status_placeholder.info("📝 Processing text file...")
            try:
                decoded_content = content.decode('utf-8')
                file_ext = os.path.splitext(file_path)[1]
                cleaned_content = self._clean_code_content(decoded_content, file_ext)
                encoded_content = base64.b64encode(cleaned_content.encode('utf-8')).decode('ascii')
                encoding = "base64"
            except UnicodeDecodeError:
                if status_placeholder:
                    status_placeholder.warning("⚠️ Fallback to binary encoding")
                encoded_content = base64.b64encode(content).decode('ascii')
                encoding = "base64"

        # Create file
        if status_placeholder:
            status_placeholder.info("⬆️ Uploading...")
        return self.create_file_with_encoding(repo_owner, repo_name, 
                                            file_path, encoded_content, encoding,
                                            commit_message)