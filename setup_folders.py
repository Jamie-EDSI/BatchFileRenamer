#!/usr/bin/env python3
"""
Automatic Setup Script
Creates all necessary folders and files for the File Renamer app
"""

import os
import shutil

def create_folder_structure():
    """Create the required folder structure"""
    
    print("Creating folder structure...")
    
    # Create folders
    folders = [
        'static',
        'static/css',
        'static/js',
        'templates',
        'uploads',
        'temp'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✓ Created {folder}/")
    
    print("\nFolder structure created successfully!")
    print("\nNow you need to:")
    print("1. Download styles.css and save it to: static/css/styles.css")
    print("2. Download app.js and save it to: static/js/app.js")
    print("3. Download index.html and save it to: templates/index.html")
    print("4. Make sure app.py is in the root directory")
    print("\nThen run: python app.py")

if __name__ == "__main__":
    create_folder_structure()
