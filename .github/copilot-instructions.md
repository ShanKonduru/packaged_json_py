<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project: Directory Packager JSON Generator

This is a Python console application that generates packaged JSON files from directory structures with configurable ignore patterns.

### Project Structure
- `main.py` - Main console application entry point (packaging)
- `extractor.py` - Console application for extracting from JSON
- `directory_packager.py` - Core logic for directory scanning and JSON generation  
- `config_manager.py` - Configuration file handling
- `config.json` - Default configuration for ignore patterns
- `requirements.txt` - Python dependencies (none required)
- `README.md` - Project documentation

### Features
- ✅ Scans root directory and all subdirectories recursively
- ✅ Generates structured JSON representation of directory tree
- ✅ Captures complete file contents (text files as UTF-8, binary as base64)
- ✅ Extracts projects from JSON (complete reverse process)
- ✅ Configurable ignore patterns for files and folders
- ✅ Command-line interface for easy usage
- ✅ Statistics reporting and verbose mode
- ✅ Error handling for permissions and file access
- ✅ Automatic outputs folder organization
- ✅ Perfect for sharing complete projects via email

### Usage
```bash
# Package directory to JSON
python main.py <directory> [-o output.json] [-c config.json] [-v]
# Outputs automatically stored in outputs/ folder
# Auto-generated filename: <foldername>_<YYYYMMDD_HHMMSS>.json

# Extract JSON to directory  
python extractor.py <json_file> [-o output_dir] [-v] [--overwrite]
# Outputs automatically stored in extracted/ folder
```

### Development Guidelines
- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Include proper error handling and logging
- Write clear, self-documenting code

### Status: ✅ COMPLETED
Project successfully implemented and tested. All core functionality working as expected.