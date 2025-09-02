#!/usr/bin/env python3
"""
Script to fix import issues in the HR System codebase.
This script replaces 'from app.' imports with relative imports when running from the app directory.
"""

import os
import re

def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace 'from app.' with relative imports
        original_content = content
        content = re.sub(r'from app\.', 'from ', content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed imports in: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def fix_imports_in_directory(directory):
    """Fix imports in all Python files in a directory"""
    fixed_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_imports_in_file(file_path):
                    fixed_count += 1
    return fixed_count

if __name__ == "__main__":
    app_directory = "app"
    if os.path.exists(app_directory):
        print(f"Fixing imports in {app_directory} directory...")
        fixed_count = fix_imports_in_directory(app_directory)
        print(f"Fixed imports in {fixed_count} files.")
    else:
        print(f"Directory {app_directory} not found.")
