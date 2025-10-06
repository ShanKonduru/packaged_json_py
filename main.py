#!/usr/bin/env python3
"""
Directory Packager - Console Application
Generates packaged JSON files from directory structures with configurable ignore patterns.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from directory_packager import DirectoryPackager
from config_manager import ConfigManager


def main():
    """Main entry point for the directory packager application."""
    parser = argparse.ArgumentParser(
        description="Generate a packaged JSON file from a directory structure"
    )
    parser.add_argument(
        "root_directory",
        type=str,
        help="Root directory to scan and package"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output JSON file path (default: outputs/<foldername>_<datetime>.json)"
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        default="config.json",
        help="Configuration file path (default: config.json)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    try:
        # Validate root directory
        root_path = Path(args.root_directory)
        if not root_path.exists():
            print(f"Error: Root directory '{args.root_directory}' does not exist.")
            sys.exit(1)
        
        if not root_path.is_dir():
            print(f"Error: '{args.root_directory}' is not a directory.")
            sys.exit(1)

        # Load configuration
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        
        if args.verbose:
            print(f"Using configuration: {args.config}")
            print(f"Scanning directory: {root_path.absolute()}")

        # Create packager and generate JSON
        packager = DirectoryPackager(config, verbose=args.verbose)
        directory_data = packager.scan_directory(root_path)

        # Save to output file in outputs directory
        outputs_dir = Path("outputs")
        outputs_dir.mkdir(exist_ok=True)
        
        # Generate filename if not provided
        if args.output is None:
            # Get folder name and clean it for filename use
            if root_path.name:
                folder_name = root_path.name
            else:
                # For current directory, get the actual folder name
                folder_name = root_path.resolve().name
            
            # Replace invalid filename characters
            folder_name = "".join(c for c in folder_name if c.isalnum() or c in ('-', '_', '.')).strip()
            if not folder_name:
                folder_name = "directory"
            
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{folder_name}_{timestamp}.json"
            output_path = outputs_dir / filename
        else:
            # If user provided just a filename, put it in outputs folder
            # If user provided a full path, respect their choice
            output_path = Path(args.output)
            if not output_path.is_absolute() and len(output_path.parts) == 1:
                output_path = outputs_dir / output_path
        
        packager.save_to_json(directory_data, output_path)

        print(f"Successfully generated packaged JSON: {output_path.absolute()}")
        
        if args.verbose:
            stats = packager.get_stats()
            print(f"Statistics:")
            print(f"  - Total directories: {stats['directories']}")
            print(f"  - Total files: {stats['files']}")
            print(f"  - Ignored items: {stats['ignored']}")

    except FileNotFoundError as e:
        print(f"Error: Configuration file not found - {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()