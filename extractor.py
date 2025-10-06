#!/usr/bin/env python3
"""
Directory Extractor - Console Application
Extracts and reconstructs directory structures from packaged JSON files.
"""

import argparse
import json
import sys
import base64
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def main():
    """Main entry point for the directory extractor application."""
    parser = argparse.ArgumentParser(
        description="Extract and reconstruct directory structure from a packaged JSON file"
    )
    parser.add_argument(
        "json_file",
        type=str,
        help="Packaged JSON file to extract"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output directory path (default: extracted/<original_name>_extracted_<timestamp>)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files and directories"
    )

    args = parser.parse_args()

    try:
        # Validate JSON file
        json_path = Path(args.json_file)
        if not json_path.exists():
            print(f"Error: JSON file '{args.json_file}' does not exist.")
            sys.exit(1)
        
        if not json_path.is_file():
            print(f"Error: '{args.json_file}' is not a file.")
            sys.exit(1)

        # Load JSON data
        if args.verbose:
            print(f"Loading JSON file: {json_path.absolute()}")

        with open(json_path, 'r', encoding='utf-8') as f:
            directory_data = json.load(f)

        # Validate JSON structure
        if not isinstance(directory_data, dict) or directory_data.get('type') != 'directory':
            print("Error: Invalid JSON file format. Expected a directory structure.")
            sys.exit(1)

        # Create extractor and extract
        extractor = DirectoryExtractor(verbose=args.verbose, overwrite=args.overwrite)
        
        # Determine output directory
        if args.output is None:
            extracted_dir = Path("extracted")
            extracted_dir.mkdir(exist_ok=True)
            
            # Generate output directory name
            original_name = directory_data.get('name', 'directory')
            # Clean name for directory use
            original_name = "".join(c for c in original_name if c.isalnum() or c in ('-', '_', '.')).strip()
            if not original_name:
                original_name = "directory"
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = extracted_dir / f"{original_name}_extracted_{timestamp}"
        else:
            output_dir = Path(args.output)

        # Extract directory structure
        extractor.extract_directory(directory_data, output_dir)

        print(f"Successfully extracted directory structure to: {output_dir.absolute()}")
        
        if args.verbose:
            stats = extractor.get_stats()
            print(f"Statistics:")
            print(f"  - Total directories created: {stats['directories']}")
            print(f"  - Total files created: {stats['files']}")
            print(f"  - Errors encountered: {stats['errors']}")

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


class DirectoryExtractor:
    """Handles extraction of directory structures from JSON data."""
    
    def __init__(self, verbose: bool = False, overwrite: bool = False):
        """
        Initialize the DirectoryExtractor.
        
        Args:
            verbose: Enable verbose output
            overwrite: Allow overwriting existing files/directories
        """
        self.verbose = verbose
        self.overwrite = overwrite
        self.stats = {
            'directories': 0,
            'files': 0,
            'errors': 0
        }
    
    def extract_directory(self, directory_data: Dict[str, Any], output_path: Path) -> None:
        """
        Extract a directory structure from JSON data.
        
        Args:
            directory_data: Directory data dictionary
            output_path: Path where to extract the directory
        """
        if self.verbose:
            print(f"Extracting to: {output_path}")
        
        # Reset stats
        self.stats = {'directories': 0, 'files': 0, 'errors': 0}
        
        # Create the root directory
        self._create_directory(output_path)
        
        # Process contents
        contents = directory_data.get('contents', [])
        for item in contents:
            try:
                item_path = output_path / item['name']
                
                if item['type'] == 'directory':
                    self._extract_subdirectory(item, item_path)
                elif item['type'] == 'file':
                    self._extract_file(item, item_path)
                else:
                    if self.verbose:
                        print(f"Warning: Unknown item type '{item['type']}' for {item['name']}")
                    
            except Exception as e:
                self.stats['errors'] += 1
                if self.verbose:
                    print(f"Error processing {item.get('name', 'unknown')}: {e}")
    
    def _extract_subdirectory(self, directory_data: Dict[str, Any], directory_path: Path) -> None:
        """
        Extract a subdirectory recursively.
        
        Args:
            directory_data: Directory data dictionary
            directory_path: Path where to create the directory
        """
        if self.verbose:
            print(f"  Creating directory: {directory_path}")
        
        # Create the directory
        self._create_directory(directory_path)
        
        # Process contents
        contents = directory_data.get('contents', [])
        for item in contents:
            try:
                item_path = directory_path / item['name']
                
                if item['type'] == 'directory':
                    self._extract_subdirectory(item, item_path)
                elif item['type'] == 'file':
                    self._extract_file(item, item_path)
                    
            except Exception as e:
                self.stats['errors'] += 1
                if self.verbose:
                    print(f"Error processing {item.get('name', 'unknown')}: {e}")
    
    def _create_directory(self, directory_path: Path) -> None:
        """
        Create a directory.
        
        Args:
            directory_path: Path of the directory to create
        """
        try:
            if directory_path.exists() and not self.overwrite:
                if self.verbose:
                    print(f"Directory already exists: {directory_path}")
            else:
                directory_path.mkdir(parents=True, exist_ok=True)
                self.stats['directories'] += 1
                
        except Exception as e:
            self.stats['errors'] += 1
            if self.verbose:
                print(f"Error creating directory {directory_path}: {e}")
    
    def _extract_file(self, file_data: Dict[str, Any], file_path: Path) -> None:
        """
        Extract a file from JSON data.
        
        Args:
            file_data: File data dictionary
            file_path: Path where to create the file
        """
        if self.verbose:
            print(f"  Creating file: {file_path}")
        
        try:
            # Check if file exists and overwrite is disabled
            if file_path.exists() and not self.overwrite:
                if self.verbose:
                    print(f"File already exists, skipping: {file_path}")
                return
            
            # Check if file has contents
            if 'contents' not in file_data:
                # Create empty file if no contents
                file_path.touch()
                self.stats['files'] += 1
                return
            
            contents = file_data['contents']
            
            # Handle different content types
            if contents.get('type') == 'text':
                # Text file
                data = contents.get('data', '')
                encoding = contents.get('encoding', 'utf-8')
                
                with open(file_path, 'w', encoding=encoding) as f:
                    f.write(data)
                    
            elif contents.get('type') == 'binary':
                # Binary file
                data = contents.get('data', '')
                if contents.get('encoding') == 'base64':
                    binary_data = base64.b64decode(data)
                    with open(file_path, 'wb') as f:
                        f.write(binary_data)
                else:
                    raise ValueError(f"Unsupported binary encoding: {contents.get('encoding')}")
                    
            elif contents.get('type') == 'error':
                # File had read error, create empty file
                if self.verbose:
                    print(f"Original file had read error, creating empty file: {file_path}")
                file_path.touch()
                
            else:
                raise ValueError(f"Unsupported content type: {contents.get('type')}")
            
            self.stats['files'] += 1
            
            # Set file modification time if available
            if 'modified' in file_data:
                try:
                    import os
                    modified_time = datetime.fromisoformat(file_data['modified']).timestamp()
                    os.utime(file_path, (modified_time, modified_time))
                except (ValueError, OSError):
                    pass  # Ignore timestamp errors
                    
        except Exception as e:
            self.stats['errors'] += 1
            if self.verbose:
                print(f"Error creating file {file_path}: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics from the last extraction operation.
        
        Returns:
            Dictionary containing extraction statistics
        """
        return self.stats.copy()


if __name__ == "__main__":
    main()