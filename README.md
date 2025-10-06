# Di## Features

- 📁 Scans root directory and all subdirectories recursively
- 📄 Generates structured JSON representation of directory tree
- 📋 **Captures file contents** (text files as UTF-8, binary files as base64)
- 🔄 **Extracts projects from JSON** (complete reverse process)
- ⚙️ Configurable ignore patterns for files and folders
- 🗂️ Configurable content capture options (file size limits, file type filters)
- 🖥️ Command-line interface for easy usage
- 📊 Statistics reporting (files, directories, ignored items)
- 🔍 Verbose mode for detailed scanning output
- 🗃️ **Automatic outputs and extracted folder organization**
- ✉️ **Perfect for sharing complete projects via email as JSON**kager

A Python console application that generates packaged JSON files from directory structures with configurable ignore patterns.

## Features

- 📁 Scans root directory and all subdirectories recursively
- 📄 Generates structured JSON representation of directory tree
- 📋 **Captures file contents** (text files as UTF-8, binary files as base64)
- ⚙️ Configurable ignore patterns for files and folders
- �️ Configurable content capture options (file size limits, file type filters)
- �🖥️ Command-line interface for easy usage
- 📊 Statistics reporting (files, directories, ignored items)
- 🔍 Verbose mode for detailed scanning output
- ✉️ **Perfect for sharing complete projects via email as JSON**

## Installation

1. Clone or download this repository
2. Ensure Python 3.6+ is installed
3. No additional dependencies required (uses only standard library)

## Usage

### Basic Usage

```bash
python main.py /path/to/directory
```

This will scan the specified directory and generate a JSON file with an automatic name like `outputs/foldername_20251006_143052.json`.

### Advanced Usage

```bash
python main.py /path/to/directory -o output.json -c custom_config.json -v
```

### Command Line Options

- `root_directory` (required): Root directory to scan and package
- `-o, --output`: Output JSON file path (default: auto-generated based on folder name + timestamp)
- `-c, --config`: Configuration file path (default: `config.json`)
- `-v, --verbose`: Enable verbose output

**Note:** Output files are automatically stored in the `outputs/` folder with descriptive names unless you specify a custom name or full path.

### Automatic Filename Generation

The application automatically generates descriptive filenames using the pattern:
`<foldername>_<YYYYMMDD_HHMMSS>.json`

Examples:
- Scanning `MyProject/` → `outputs/MyProject_20251006_143052.json`
- Scanning current directory → `outputs/packaged_json_20251006_143052.json`
- Custom name → `outputs/custom_name.json` (if you specify `-o custom_name.json`)

### Examples

```bash
# Scan current directory (auto-generated: outputs/foldername_timestamp.json)
python main.py .

# Scan specific directory (auto-generated: outputs/MyProject_timestamp.json)
python main.py C:\MyProject

# Use custom filename (output: outputs/project_structure.json)
python main.py C:\MyProject -o project_structure.json

# Use custom config and verbose mode with auto-generated name
python main.py /home/user/documents -c my_config.json -v

# Save to specific location outside outputs folder
python main.py "C:\Program Files\MyApp" -o "C:\Backups\app_structure.json"
```

## Extraction (Reverse Process)

The `extractor.py` tool allows you to reconstruct directory structures from packaged JSON files.

### Basic Extraction

```bash
python extractor.py outputs/project_20251006_143052.json
```

This will extract the project to `extracted/project_extracted_<timestamp>/`.

### Advanced Extraction

```bash
python extractor.py outputs/project.json -o my_extracted_project -v --overwrite
```

### Extraction Options

- `json_file` (required): Packaged JSON file to extract
- `-o, --output`: Output directory path (default: auto-generated in `extracted/` folder)
- `-v, --verbose`: Enable verbose output showing extraction progress
- `--overwrite`: Overwrite existing files and directories

### Extraction Examples

```bash
# Auto-generated extraction path
python extractor.py outputs/MyProject_20251006_143052.json
# → extracted/MyProject_extracted_20251006_144215/

# Custom extraction path
python extractor.py outputs/client_app.json -o restored_client_app

# Verbose extraction with overwrite
python extractor.py outputs/backup.json -v --overwrite -o /path/to/restore

# Extract and examine structure
python extractor.py outputs/project.json -v
```

### Complete Workflow Example

```bash
# 1. Package a project
python main.py /path/to/my_project
# → outputs/my_project_20251006_143052.json

# 2. Share via email (attach the JSON file)

# 3. Recipient extracts the project
python extractor.py my_project_20251006_143052.json
# → extracted/my_project_extracted_20251006_144215/

# 4. Original project structure is perfectly recreated!
```

## Validation

The `validator.py` tool allows you to verify that an extracted directory matches the original directory perfectly.

### Basic Validation

```bash
python validator.py "C:\MyProject" "extracted\MyProject_extracted_20251006_144215"
```

### Advanced Validation

```bash
python validator.py "original_path" "extracted_path" -v --save-report validation_report.json
```

### Validation Options

- `original` (required): Path to original directory
- `extracted` (required): Path to extracted directory  
- `-v, --verbose`: Enable verbose output showing detailed comparison
- `--save-report`: Save detailed validation report to JSON file

### Quick Validation (Windows)

```bash
# Using the convenience batch script
validate.bat "C:\MyProject" "extracted\MyProject_extracted_20251006_144215"

# With verbose output
validate.bat "C:\MyProject" "extracted\MyProject_extracted_20251006_144215" verbose
```

### Validation Features

- ✅ **File Count Verification**: Ensures all files are present
- ✅ **Directory Structure Validation**: Verifies folder hierarchy matches
- ✅ **File Size Comparison**: Checks file sizes (with tolerance for binary files)
- ✅ **Content Integrity**: MD5 hash comparison for text files
- ✅ **Binary File Support**: Smart handling of base64-encoded binary files
- ✅ **Ignore Pattern Awareness**: Respects the same ignore patterns as packaging
- ✅ **Detailed Reporting**: Comprehensive validation reports with statistics

### Complete Workflow with Validation

```bash
# 1. Package a project
python main.py "C:\MyProject"
# → outputs/MyProject_20251006_143052.json

# 2. Extract the project
python extractor.py "outputs\MyProject_20251006_143052.json"
# → extracted/MyProject_extracted_20251006_144215/

# 3. Validate the extraction
python validator.py "C:\MyProject" "extracted\MyProject_extracted_20251006_144215" -v
# → 🎉 VALIDATION PASSED: Directories match perfectly!

# 4. Original project structure is perfectly recreated!

## Configuration

The application uses a JSON configuration file to define ignore patterns. If no configuration file exists, a default one will be created automatically.

### Configuration Structure

```json
{
  "capture_contents": true,
  "max_content_size": 10485760,
  "capture_extensions": [],
  "no_capture_extensions": [".exe", ".dll", ".zip", ".jpg", ".mp4"],
  "ignore_extensions": [".pyc", ".log", ".tmp", ".bak"],
  "ignore_file_patterns": ["*.tmp", "*.cache", ".*"],
  "ignore_folder_patterns": ["__pycache__", ".git", "node_modules", "venv"],
  "ignore_paths": [".gitignore", "README.md", "LICENSE"]
}
```

### Configuration Options

**Content Capture Options:**
- **capture_contents**: Enable/disable file content capture (default: true)
- **max_content_size**: Maximum file size to capture contents (default: 10MB)
- **capture_extensions**: If specified, only capture contents for these extensions (empty = all)
- **no_capture_extensions**: File extensions to exclude from content capture (binary files, etc.)

**Ignore Options:**
- **ignore_extensions**: File extensions to ignore completely (e.g., `.pyc`, `.log`)
- **ignore_file_patterns**: File name patterns using wildcards (e.g., `*.tmp`)
- **ignore_folder_patterns**: Folder name patterns to ignore (e.g., `__pycache__`)
- **ignore_paths**: Specific file or folder names to ignore (e.g., `.git`)

## Output Format

The generated JSON file contains a hierarchical representation of the directory structure **including file contents**:

```json
{
  "name": "project_root",
  "type": "directory",
  "path": "/absolute/path/to/project_root",
  "generated_at": "2025-10-06T15:30:45.123456",
  "contents": [
    {
      "name": "script.py",
      "type": "file",
      "size": 1024,
      "modified": "2025-10-06T10:15:30.000000",
      "extension": ".py",
      "contents": {
        "type": "text",
        "encoding": "utf-8",
        "data": "#!/usr/bin/env python3\nprint('Hello World')\n"
      }
    },
    {
      "name": "image.jpg",
      "type": "file", 
      "size": 2048,
      "modified": "2025-10-06T10:16:00.000000",
      "extension": ".jpg",
      "contents": {
        "type": "binary",
        "encoding": "base64",
        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
      }
    },
    {
      "name": "subdirectory",
      "type": "directory",
      "contents": [...]
    }
  ]
}
```

### JSON Structure Details

- **name**: Item name
- **type**: Either "file" or "directory"
- **path**: Full absolute path (root directory only)
- **generated_at**: ISO timestamp when JSON was generated
- **size**: File size in bytes (files only)
- **modified**: Last modification time (files only)
- **extension**: File extension (files only)
- **contents**: Array of contained items (directories only) OR file content object (files only)
- **error**: Error message if item couldn't be accessed

### File Content Object Structure

- **type**: "text", "binary", or "error"
- **encoding**: For text files: detected encoding (utf-8, latin-1, etc.); For binary: "base64"
- **data**: Actual file contents (text string or base64 encoded binary)
- **error**: Error message if content couldn't be read

## Default Ignore Patterns

The application comes with sensible defaults for common development environments:

### File Extensions
- Compiled files: `.pyc`, `.pyo`, `.so`, `.dll`, `.exe`
- Temporary files: `.tmp`, `.temp`, `.log`, `.cache`, `.bak`
- System files: `.DS_Store`, `Thumbs.db`

### Folder Patterns
- Version control: `.git`, `.svn`, `.hg`
- IDE folders: `.vscode`, `.idea`
- Build/dependency folders: `node_modules`, `__pycache__`, `build`, `dist`
- Virtual environments: `venv`, `.env`, `virtualenv`

### File Patterns
- Hidden files: `.*`
- Temporary files: `*.tmp`, `*.cache`, `*.bak`
- Editor backups: `*~`, `#*#`

## Error Handling

The application gracefully handles common errors:

- **Permission denied**: Continues scanning accessible parts
- **File not found**: Reports missing configuration files
- **Invalid JSON**: Validates configuration file format
- **Invalid paths**: Validates input directory existence

## Performance Considerations

- Large directory trees may take time to scan
- Use ignore patterns to exclude unnecessary files/folders
- Verbose mode adds overhead but provides useful feedback
- JSON output size depends on directory structure complexity

## Project Structure

```
directory-packager/
├── main.py                 # Main application entry point (packaging)
├── extractor.py            # Console application for extracting from JSON
├── directory_packager.py   # Core scanning and JSON generation logic
├── config_manager.py       # Configuration file handling
├── config.json            # Default configuration file
├── requirements.txt       # Python dependencies (none required)
├── README.md              # This documentation
├── outputs/               # Generated JSON files stored here
│   └── (auto-generated files)
├── extracted/             # Extracted projects stored here (created when needed)
│   └── (auto-generated folders)
└── .github/
    └── copilot-instructions.md
```

## License

This project is provided as-is for educational and practical use.