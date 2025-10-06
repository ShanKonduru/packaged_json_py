"""
Configuration Manager - Handles loading and validation of configuration files.
"""

import json
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Manages configuration file loading and validation."""
    
    def __init__(self, config_path: str):
        """
        Initialize the ConfigManager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        self.default_config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "capture_contents": True,
            "max_content_size": 10485760,
            "capture_extensions": [],
            "no_capture_extensions": [
                ".exe",
                ".dll",
                ".so",
                ".dylib",
                ".bin",
                ".img",
                ".iso",
                ".zip",
                ".rar",
                ".7z",
                ".tar",
                ".gz",
                ".bz2",
                ".xz",
                ".pdf",
                ".doc",
                ".docx",
                ".xls",
                ".xlsx",
                ".ppt",
                ".pptx",
                ".mp3",
                ".mp4",
                ".avi",
                ".mkv",
                ".wav",
                ".flac",
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".bmp",
                ".tiff",
                ".webp",
                ".ico"
            ],
            "ignore_extensions": [
                ".pyc",
                ".pyo",
                ".pyd",
                ".so",
                ".dll",
                ".dylib",
                ".o",
                ".obj",
                ".exe",
                ".bin",
                ".log",
                ".tmp",
                ".temp",
                ".cache",
                ".bak",
                ".swp",
                ".swo",
                "~",
                ".DS_Store",
                "Thumbs.db"
            ],
            "ignore_file_patterns": [
                "*.tmp",
                "*.temp",
                "*.log",
                "*.cache",
                "*.bak",
                ".*",
                "#*#",
                "*~"
            ],
            "ignore_folder_patterns": [
                "__pycache__",
                "*.egg-info",
                ".git",
                ".svn",
                ".hg",
                ".bzr",
                "CVS",
                ".vscode",
                ".idea",
                "node_modules",
                "venv",
                "env",
                ".env",
                "virtualenv",
                ".venv",
                "build",
                "dist",
                "target",
                "bin",
                "obj",
                ".pytest_cache",
                ".coverage",
                ".tox",
                ".mypy_cache",
                "outputs"
            ],
            "ignore_paths": [
                ".gitignore",
                ".gitattributes",
                "LICENSE",
                "setup.py",
                "setup.cfg",
                "pyproject.toml",
                "Pipfile",
                "Pipfile.lock"
            ]
        }
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or create default if not exists.
        
        Returns:
            Configuration dictionary
            
        Raises:
            json.JSONDecodeError: If config file contains invalid JSON
            FileNotFoundError: If config file doesn't exist and can't be created
        """
        if not self.config_path.exists():
            # Create default config file
            self._create_default_config()
            return self.default_config.copy()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validate and merge with defaults
            return self._validate_and_merge_config(config)
        
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in config file '{self.config_path}': {e.msg}",
                e.doc,
                e.pos
            )
        except Exception as e:
            raise FileNotFoundError(f"Error reading config file '{self.config_path}': {e}")
    
    def _create_default_config(self) -> None:
        """
        Create a default configuration file.
        
        Raises:
            Exception: If unable to create the config file
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.default_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Failed to create default config file '{self.config_path}': {e}")
    
    def _validate_and_merge_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate loaded configuration and merge with defaults.
        
        Args:
            config: Loaded configuration dictionary
            
        Returns:
            Validated and merged configuration
        """
        # Start with default config
        merged_config = self.default_config.copy()
        
        # Validate and merge boolean options
        for key in ['capture_contents']:
            if key in config:
                if isinstance(config[key], bool):
                    merged_config[key] = config[key]
                else:
                    print(f"Warning: '{key}' in config should be a boolean, using default")
        
        # Validate and merge integer options
        for key in ['max_content_size']:
            if key in config:
                if isinstance(config[key], int) and config[key] > 0:
                    merged_config[key] = config[key]
                else:
                    print(f"Warning: '{key}' in config should be a positive integer, using default")
        
        # Validate and merge list options
        for key in ['ignore_extensions', 'ignore_file_patterns', 
                   'ignore_folder_patterns', 'ignore_paths',
                   'capture_extensions', 'no_capture_extensions']:
            if key in config:
                if isinstance(config[key], list):
                    # If user provided this section, use it (don't merge with defaults)
                    merged_config[key] = config[key]
                else:
                    print(f"Warning: '{key}' in config should be a list, using default")
        
        return merged_config
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
            
        Raises:
            Exception: If unable to save the config file
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Failed to save config file '{self.config_path}': {e}")