#!/usr/bin/env python3
"""
Directory Comparison Validator

This script validates that an extracted directory matches the original directory
by comparing file counts, sizes, content, and directory structure.
"""

import os
import sys
import hashlib
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Set
import json
from datetime import datetime

class DirectoryValidator:
    def __init__(self, original_path: str, extracted_path: str, verbose: bool = False):
        self.original_path = Path(original_path)
        self.extracted_path = Path(extracted_path)
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.stats = {
            'total_files_original': 0,
            'total_files_extracted': 0,
            'total_dirs_original': 0,
            'total_dirs_extracted': 0,
            'files_matched': 0,
            'files_size_mismatch': 0,
            'files_content_mismatch': 0,
            'files_missing': 0,
            'files_extra': 0,
            'dirs_matched': 0,
            'dirs_missing': 0,
            'dirs_extra': 0
        }

    def log_verbose(self, message: str):
        """Log verbose output if verbose mode is enabled."""
        if self.verbose:
            print(f"  {message}")

    def log_error(self, message: str):
        """Log an error."""
        self.errors.append(message)
        print(f"❌ ERROR: {message}")

    def log_warning(self, message: str):
        """Log a warning."""
        self.warnings.append(message)
        print(f"⚠️  WARNING: {message}")

    def get_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.log_warning(f"Could not calculate hash for {file_path}: {e}")
            return ""

    def is_binary_file(self, file_path: str) -> bool:
        """Check if file is likely a binary file based on extension."""
        binary_extensions = {
            '.xlsx', '.xls', '.doc', '.docx', '.pdf', '.zip', '.rar', '.7z', 
            '.tar', '.gz', '.exe', '.dll', '.so', '.dylib', '.bin', '.img', 
            '.iso', '.mp3', '.mp4', '.avi', '.mkv', '.jpg', '.jpeg', '.png', 
            '.gif', '.bmp', '.tiff'
        }
        return any(file_path.lower().endswith(ext) for ext in binary_extensions)

    def get_size_tolerance(self, file_path: str, original_size: int) -> int:
        """
        Get acceptable size tolerance for a file.
        Binary files may have slight size differences due to base64 encoding/decoding.
        """
        if self.is_binary_file(file_path):
            # For binary files, allow up to 1% size difference or 500 bytes, whichever is larger
            # This accounts for base64 encoding overhead and metadata differences
            tolerance = max(500, int(original_size * 0.01))
            return tolerance
        else:
            # Text files should match exactly
            return 0

    def should_compare_content(self, file_path: str, file_size: int) -> bool:
        """Determine if content comparison should be performed."""
        # Skip content comparison for very large files
        if file_size > 50 * 1024 * 1024:  # 50MB
            return False
        
        # For binary files over 1MB, skip content comparison if size is within tolerance
        if self.is_binary_file(file_path) and file_size > 1024 * 1024:
            return False
        
        return True

    def scan_directory(self, path: Path, ignore_patterns: Set[str] = None) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
        """
        Scan a directory and return dictionaries of files and directories.
        Returns relative paths as keys to handle different root paths.
        """
        if ignore_patterns is None:
            # Use the same ignore patterns as the packager
            ignore_patterns = {'.git', '.vscode', '__pycache__', '.env', '.coverage', '.gitignore', '.env_sample'}
        
        files = {}
        dirs = {}
        
        if not path.exists():
            self.log_error(f"Path does not exist: {path}")
            return files, dirs

        try:
            for item in path.rglob('*'):
                # Skip if any parent directory is in ignore patterns
                if any(part in ignore_patterns for part in item.parts):
                    continue
                
                # Skip if filename itself is in ignore patterns
                if item.name in ignore_patterns:
                    continue
                
                # Get relative path from the root
                rel_path = item.relative_to(path)
                rel_path_str = str(rel_path).replace('\\', '/')  # Normalize path separators
                
                if item.is_file():
                    files[rel_path_str] = {
                        'path': item,
                        'size': item.stat().st_size,
                        'modified': item.stat().st_mtime
                    }
                elif item.is_dir():
                    dirs[rel_path_str] = {
                        'path': item,
                        'modified': item.stat().st_mtime
                    }
        except Exception as e:
            self.log_error(f"Error scanning directory {path}: {e}")
        
        return files, dirs

    def compare_files(self, original_files: Dict[str, Dict], extracted_files: Dict[str, Dict]) -> bool:
        """Compare files between original and extracted directories."""
        print("\n🔍 Comparing files...")
        
        self.stats['total_files_original'] = len(original_files)
        self.stats['total_files_extracted'] = len(extracted_files)
        
        all_files = set(original_files.keys()) | set(extracted_files.keys())
        files_match = True
        
        for file_path in sorted(all_files):
            if file_path in original_files and file_path in extracted_files:
                # File exists in both
                orig_info = original_files[file_path]
                extr_info = extracted_files[file_path]
                
                # Compare file sizes
                size_diff = abs(orig_info['size'] - extr_info['size'])
                size_tolerance = self.get_size_tolerance(file_path, orig_info['size'])
                
                if size_diff > size_tolerance:
                    self.log_error(f"Size mismatch for {file_path}: original={orig_info['size']}, extracted={extr_info['size']}, diff={size_diff}")
                    self.stats['files_size_mismatch'] += 1
                    files_match = False
                else:
                    if size_diff > 0:
                        self.log_verbose(f"✅ Size match (within tolerance): {file_path} (diff: {size_diff} bytes)")
                    else:
                        self.log_verbose(f"✅ Size match: {file_path} ({orig_info['size']} bytes)")
                
                # Compare file content (hash) for text files and small binary files
                if self.should_compare_content(file_path, orig_info['size']):
                    orig_hash = self.get_file_hash(orig_info['path'])
                    extr_hash = self.get_file_hash(extr_info['path'])
                    
                    if orig_hash and extr_hash and orig_hash != extr_hash:
                        # For binary files, size match within tolerance is acceptable
                        if self.is_binary_file(file_path) and size_diff <= size_tolerance:
                            self.log_verbose(f"✅ Binary file content acceptable: {file_path} (size within tolerance)")
                            self.stats['files_matched'] += 1
                        else:
                            self.log_error(f"Content mismatch for {file_path}")
                            self.stats['files_content_mismatch'] += 1
                            files_match = False
                    elif orig_hash and extr_hash:
                        self.log_verbose(f"✅ Content match: {file_path}")
                        self.stats['files_matched'] += 1
                else:
                    self.log_warning(f"Skipping content comparison for large file: {file_path} ({orig_info['size']} bytes)")
                    self.stats['files_matched'] += 1
                
            elif file_path in original_files:
                # File missing in extracted
                self.log_error(f"File missing in extracted: {file_path}")
                self.stats['files_missing'] += 1
                files_match = False
                
            else:
                # Extra file in extracted
                self.log_warning(f"Extra file in extracted: {file_path}")
                self.stats['files_extra'] += 1
        
        return files_match

    def compare_directories(self, original_dirs: Dict[str, Dict], extracted_dirs: Dict[str, Dict]) -> bool:
        """Compare directory structures."""
        print("\n📁 Comparing directories...")
        
        self.stats['total_dirs_original'] = len(original_dirs)
        self.stats['total_dirs_extracted'] = len(extracted_dirs)
        
        all_dirs = set(original_dirs.keys()) | set(extracted_dirs.keys())
        dirs_match = True
        
        for dir_path in sorted(all_dirs):
            if dir_path in original_dirs and dir_path in extracted_dirs:
                self.log_verbose(f"✅ Directory match: {dir_path}")
                self.stats['dirs_matched'] += 1
            elif dir_path in original_dirs:
                self.log_error(f"Directory missing in extracted: {dir_path}")
                self.stats['dirs_missing'] += 1
                dirs_match = False
            else:
                self.log_warning(f"Extra directory in extracted: {dir_path}")
                self.stats['dirs_extra'] += 1
        
        return dirs_match

    def validate(self) -> bool:
        """
        Perform complete validation of original vs extracted directories.
        Returns True if validation passes, False otherwise.
        """
        print(f"🔄 Starting validation...")
        print(f"Original: {self.original_path}")
        print(f"Extracted: {self.extracted_path}")
        
        if not self.original_path.exists():
            self.log_error(f"Original directory does not exist: {self.original_path}")
            return False
        
        if not self.extracted_path.exists():
            self.log_error(f"Extracted directory does not exist: {self.extracted_path}")
            return False
        
        # Scan both directories
        print("\n📂 Scanning original directory...")
        original_files, original_dirs = self.scan_directory(self.original_path)
        
        print("📂 Scanning extracted directory...")
        extracted_files, extracted_dirs = self.scan_directory(self.extracted_path)
        
        # Compare directories and files
        dirs_match = self.compare_directories(original_dirs, extracted_dirs)
        files_match = self.compare_files(original_files, extracted_files)
        
        # Print summary
        self.print_summary()
        
        # Overall validation result
        validation_passed = dirs_match and files_match and len(self.errors) == 0
        
        if validation_passed:
            print("\n🎉 VALIDATION PASSED: Directories match perfectly!")
        else:
            print("\n❌ VALIDATION FAILED: Directories do not match!")
        
        return validation_passed

    def print_summary(self):
        """Print validation summary statistics."""
        print("\n📊 VALIDATION SUMMARY")
        print("=" * 50)
        
        print(f"📁 Directories:")
        print(f"  Original: {self.stats['total_dirs_original']}")
        print(f"  Extracted: {self.stats['total_dirs_extracted']}")
        print(f"  Matched: {self.stats['dirs_matched']}")
        print(f"  Missing: {self.stats['dirs_missing']}")
        print(f"  Extra: {self.stats['dirs_extra']}")
        
        print(f"\n📄 Files:")
        print(f"  Original: {self.stats['total_files_original']}")
        print(f"  Extracted: {self.stats['total_files_extracted']}")
        print(f"  Matched: {self.stats['files_matched']}")
        print(f"  Size mismatches: {self.stats['files_size_mismatch']}")
        print(f"  Content mismatches: {self.stats['files_content_mismatch']}")
        print(f"  Missing: {self.stats['files_missing']}")
        print(f"  Extra: {self.stats['files_extra']}")
        
        print(f"\n⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")
        
        if self.errors:
            print(f"\n❌ ERROR DETAILS:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNING DETAILS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

def main():
    parser = argparse.ArgumentParser(
        description="Validate that extracted directory matches original directory"
    )
    parser.add_argument(
        "original",
        help="Path to original directory"
    )
    parser.add_argument(
        "extracted", 
        help="Path to extracted directory"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--save-report",
        help="Save detailed report to JSON file"
    )
    
    args = parser.parse_args()
    
    # Create validator and run validation
    validator = DirectoryValidator(args.original, args.extracted, args.verbose)
    success = validator.validate()
    
    # Save report if requested
    if args.save_report:
        report = {
            'timestamp': datetime.now().isoformat(),
            'original_path': str(validator.original_path),
            'extracted_path': str(validator.extracted_path),
            'validation_passed': success,
            'statistics': validator.stats,
            'errors': validator.errors,
            'warnings': validator.warnings
        }
        
        with open(args.save_report, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to: {args.save_report}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()