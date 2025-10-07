"""
Directory Packager - Core functionality for scanning directories and generating JSON.
"""

import json
import os
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import fnmatch
from datetime import datetime
import re


class DirectoryPackager:
    """Handles directory scanning and JSON generation with configurable ignore patterns."""
    
    def __init__(self, config: Dict[str, Any], verbose: bool = False):
        """
        Initialize the DirectoryPackager.
        
        Args:
            config: Configuration dictionary with ignore patterns
            verbose: Enable verbose output
        """
        self.config = config
        self.verbose = verbose
        self.stats = {
            'directories': 0,
            'files': 0,
            'ignored': 0
        }
        self.gitignore_patterns = []
        self.use_gitignore = False
        self.source_root = None
    
    def load_gitignore(self, source_directory: Path) -> bool:
        """
        Load .gitignore file from the source directory if it exists.
        
        Args:
            source_directory: The directory being packaged
            
        Returns:
            True if .gitignore was found and loaded, False otherwise
        """
        self.source_root = source_directory
        gitignore_path = source_directory / '.gitignore'
        
        if gitignore_path.exists() and gitignore_path.is_file():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                self.gitignore_patterns = []
                for line in lines:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        self.gitignore_patterns.append(line)
                
                self.use_gitignore = True
                if self.verbose:
                    print(f"Loaded .gitignore with {len(self.gitignore_patterns)} patterns from: {gitignore_path}")
                return True
                
            except Exception as e:
                if self.verbose:
                    print(f"Warning: Could not read .gitignore file {gitignore_path}: {e}")
                self.use_gitignore = False
                return False
        else:
            self.use_gitignore = False
            if self.verbose:
                print(f"No .gitignore found in source directory, using config.json patterns")
            return False
    
    def matches_gitignore_pattern(self, path: Path) -> bool:
        """
        Check if a path matches any .gitignore pattern.
        
        Args:
            path: Path to check (relative to source root)
            
        Returns:
            True if the path should be ignored according to .gitignore
        """
        if not self.use_gitignore or not self.source_root:
            return False
        
        try:
            # Get relative path from source root
            rel_path = path.relative_to(self.source_root)
            path_str = str(rel_path).replace('\\', '/')
            name = path.name
            
            for pattern in self.gitignore_patterns:
                # Handle negation patterns (starting with !)
                if pattern.startswith('!'):
                    continue  # Skip negation patterns for now (complex logic)
                
                # Handle directory patterns (ending with /)
                if pattern.endswith('/'):
                    if path.is_dir():
                        dir_pattern = pattern[:-1]
                        if fnmatch.fnmatch(name, dir_pattern) or fnmatch.fnmatch(path_str, dir_pattern):
                            return True
                else:
                    # Handle file and directory patterns
                    if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(path_str, pattern):
                        return True
                    
                    # Handle patterns with path separators
                    if '/' in pattern:
                        if fnmatch.fnmatch(path_str, pattern):
                            return True
        
        except ValueError:
            # Path is not relative to source_root
            pass
        
        return False
    
    def should_ignore(self, path: Path) -> bool:
        """
        Check if a path should be ignored based on .gitignore patterns or configuration patterns.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path should be ignored, False otherwise
        """
        # First check .gitignore patterns if available
        if self.use_gitignore and self.matches_gitignore_pattern(path):
            if self.verbose:
                print(f"Ignoring (gitignore pattern): {path}")
            return True
        
        # If using .gitignore, don't apply config patterns (except for essential ones)
        if self.use_gitignore:
            # Only apply essential ignores when using .gitignore
            name = path.name
            essential_patterns = ['.git', '__pycache__']
            if name in essential_patterns or (path.is_dir() and name in essential_patterns):
                if self.verbose:
                    print(f"Ignoring (essential pattern): {path}")
                return True
            return False
        
        # Fall back to config.json patterns when no .gitignore
        name = path.name
        
        # Check ignored file extensions
        if path.is_file():
            for ext in self.config.get('ignore_extensions', []):
                if name.lower().endswith(ext.lower()):
                    if self.verbose:
                        print(f"Ignoring file (extension): {path}")
                    return True
        
        # Check ignored file patterns
        for pattern in self.config.get('ignore_file_patterns', []):
            if fnmatch.fnmatch(name, pattern):
                if self.verbose:
                    print(f"Ignoring (file pattern): {path}")
                return True
        
        # Check ignored folder patterns
        if path.is_dir():
            for pattern in self.config.get('ignore_folder_patterns', []):
                if fnmatch.fnmatch(name, pattern):
                    if self.verbose:
                        print(f"Ignoring folder: {path}")
                    return True
        
        # Check ignored paths (exact matches)
        for ignored_path in self.config.get('ignore_paths', []):
            if str(path).endswith(ignored_path) or name == ignored_path:
                if self.verbose:
                    print(f"Ignoring path: {path}")
                return True
        
        return False
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Get information about a file including its contents.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file information and contents
        """
        try:
            stat = file_path.stat()
            file_info = {
                'name': file_path.name,
                'type': 'file',
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'extension': file_path.suffix.lower() if file_path.suffix else None
            }
            
            # Check if we should capture contents based on config
            if self._should_capture_contents(file_path):
                file_info['contents'] = self._get_file_contents(file_path)
            
            return file_info
            
        except (OSError, IOError) as e:
            if self.verbose:
                print(f"Warning: Could not get info for file {file_path}: {e}")
            return {
                'name': file_path.name,
                'type': 'file',
                'error': str(e)
            }
    
    def scan_directory(self, root_path: Path) -> Dict[str, Any]:
        """
        Scan a directory and return its structure as a dictionary.
        
        Args:
            root_path: Root directory to scan
            
        Returns:
            Dictionary representing the directory structure
        """
        if self.verbose:
            print(f"Scanning: {root_path}")
        
        # Load .gitignore from source directory first
        self.load_gitignore(root_path)
        
        # Reset stats
        self.stats = {'directories': 0, 'files': 0, 'ignored': 0}
        
        result = {
            'name': root_path.name if root_path.name else str(root_path),
            'type': 'directory',
            'path': str(root_path.absolute()),
            'generated_at': datetime.now().isoformat(),
            'contents': []
        }
        
        try:
            # Get all items in the directory
            items = list(root_path.iterdir())
            items.sort(key=lambda x: (x.is_file(), x.name.lower()))
            
            for item in items:
                if self.should_ignore(item):
                    self.stats['ignored'] += 1
                    continue
                
                if item.is_file():
                    self.stats['files'] += 1
                    file_info = self.get_file_info(item)
                    result['contents'].append(file_info)
                
                elif item.is_dir():
                    self.stats['directories'] += 1
                    # Recursively scan subdirectory
                    subdir_data = self._scan_subdirectory(item)
                    result['contents'].append(subdir_data)
        
        except PermissionError as e:
            if self.verbose:
                print(f"Warning: Permission denied accessing {root_path}: {e}")
            result['error'] = f"Permission denied: {e}"
        except Exception as e:
            if self.verbose:
                print(f"Warning: Error scanning {root_path}: {e}")
            result['error'] = str(e)
        
        return result
    
    def _scan_subdirectory(self, dir_path: Path) -> Dict[str, Any]:
        """
        Scan a subdirectory recursively.
        
        Args:
            dir_path: Directory path to scan
            
        Returns:
            Dictionary representing the subdirectory structure
        """
        if self.verbose:
            print(f"  Scanning subdirectory: {dir_path}")
        
        result = {
            'name': dir_path.name,
            'type': 'directory',
            'contents': []
        }
        
        try:
            items = list(dir_path.iterdir())
            items.sort(key=lambda x: (x.is_file(), x.name.lower()))
            
            for item in items:
                if self.should_ignore(item):
                    self.stats['ignored'] += 1
                    continue
                
                if item.is_file():
                    self.stats['files'] += 1
                    file_info = self.get_file_info(item)
                    result['contents'].append(file_info)
                
                elif item.is_dir():
                    self.stats['directories'] += 1
                    # Recursively scan subdirectory
                    subdir_data = self._scan_subdirectory(item)
                    result['contents'].append(subdir_data)
        
        except PermissionError as e:
            if self.verbose:
                print(f"Warning: Permission denied accessing {dir_path}: {e}")
            result['error'] = f"Permission denied: {e}"
        except Exception as e:
            if self.verbose:
                print(f"Warning: Error scanning {dir_path}: {e}")
            result['error'] = str(e)
        
        return result
    
    def save_to_json(self, data: Dict[str, Any], output_path: Path) -> None:
        """
        Save the directory data to a JSON file.
        
        Args:
            data: Directory data dictionary
            output_path: Path to save the JSON file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Failed to save JSON file: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics from the last scan operation.
        
        Returns:
            Dictionary containing scan statistics
        """
        return self.stats.copy()
    
    def _should_capture_contents(self, file_path: Path) -> bool:
        """
        Check if file contents should be captured based on configuration.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if contents should be captured, False otherwise
        """
        # Check if content capture is enabled
        if not self.config.get('capture_contents', True):
            return False
        
        # Check file size limit
        max_size = self.config.get('max_content_size', 10 * 1024 * 1024)  # 10MB default
        try:
            if file_path.stat().st_size > max_size:
                if self.verbose:
                    print(f"Skipping contents for large file: {file_path} ({file_path.stat().st_size} bytes)")
                return False
        except (OSError, IOError):
            return False
        
        # Check if extension is in capture list (if specified)
        capture_extensions = self.config.get('capture_extensions', [])
        if capture_extensions:
            extension = file_path.suffix.lower()
            if extension not in capture_extensions:
                return False
        
        # Check if extension is in no-capture list
        no_capture_extensions = self.config.get('no_capture_extensions', [])
        if no_capture_extensions:
            extension = file_path.suffix.lower()
            if extension in no_capture_extensions:
                return False
        
        return True
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """
        Determine if a file should be treated as binary based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file should be treated as binary
        """
        binary_extensions = {
            # Office documents
            '.xlsx', '.xls', '.docx', '.doc', '.pptx', '.ppt',
            # Archives
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.tiff', '.svg',
            # Audio/Video
            '.mp3', '.mp4', '.avi', '.mkv', '.wav', '.ogg',
            # Executables
            '.exe', '.dll', '.so', '.dylib',
            # Other binary formats
            '.pdf', '.bin', '.dat', '.db', '.sqlite'
        }
        
        return file_path.suffix.lower() in binary_extensions

    def _get_file_contents(self, file_path: Path) -> Dict[str, Any]:
        """
        Get file contents, handling both text and binary files.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing content data
        """
        try:
            # Check if file should be treated as binary first
            if self._is_binary_file(file_path):
                with open(file_path, 'rb') as f:
                    binary_content = f.read()
                encoded_content = base64.b64encode(binary_content).decode('ascii')
                return {
                    'type': 'binary',
                    'encoding': 'base64',
                    'data': encoded_content
                }
            
            # Try to read as text first
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {
                    'type': 'text',
                    'encoding': 'utf-8',
                    'data': content
                }
            except UnicodeDecodeError:
                # Try other common encodings
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        return {
                            'type': 'text',
                            'encoding': encoding,
                            'data': content
                        }
                    except UnicodeDecodeError:
                        continue
                
                # If all text encodings fail, treat as binary
                with open(file_path, 'rb') as f:
                    binary_content = f.read()
                encoded_content = base64.b64encode(binary_content).decode('ascii')
                return {
                    'type': 'binary',
                    'encoding': 'base64',
                    'data': encoded_content
                }
                
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not read contents of {file_path}: {e}")
            return {
                'type': 'error',
                'error': str(e)
            }