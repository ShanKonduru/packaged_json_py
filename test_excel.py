#!/usr/bin/env python3
import json
import base64
import hashlib

def get_file_hash(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def find_file(data, filename):
    """Recursively find a file in the JSON structure."""
    if isinstance(data, list):
        for item in data:
            result = find_file(item, filename)
            if result:
                return result
    elif isinstance(data, dict):
        if data.get('type') == 'file' and filename in data.get('name', ''):
            return data
        if 'contents' in data:
            return find_file(data['contents'], filename)
    return None

# Load the JSON
with open('outputs/cross_db_validator_20251007_055637.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find the Excel file
result = find_file(data['contents'], 'test_suite.xlsx')
if result:
    print(f'File: {result.get("name")}')
    contents = result.get('contents', {})
    print(f'Type: {contents.get("type")}')
    print(f'Encoding: {contents.get("encoding")}')
    print(f'Data length: {len(contents.get("data", ""))}')
    
    # Test the base64 decoding
    if contents.get('encoding') == 'base64':
        try:
            decoded_data = base64.b64decode(contents.get('data', ''))
            print(f'Decoded size: {len(decoded_data)}')
            
            # Get original file size
            import os
            orig_size = os.path.getsize('C:/MyProjects/cross_db_validator/inputs/test_suite.xlsx')
            print(f'Original size: {orig_size}')
            print(f'Size match: {len(decoded_data) == orig_size}')
            
            # Test if decoded data matches original
            orig_hash = get_file_hash('C:/MyProjects/cross_db_validator/inputs/test_suite.xlsx')
            decoded_hash = hashlib.md5(decoded_data).hexdigest()
            print(f'Original hash: {orig_hash}')
            print(f'Decoded hash: {decoded_hash}')
            print(f'Hash match: {orig_hash == decoded_hash}')
            
        except Exception as e:
            print(f'Base64 decode error: {e}')
else:
    print('File not found')