#!/usr/bin/env python3
"""
Setup Verification Script
Checks if all required files and folders are in place
"""

import os
import sys

def check_setup():
    """Verify Flask app file structure"""
    
    print("=" * 60)
    print("File Renamer - Setup Verification")
    print("=" * 60)
    print()
    
    errors = []
    warnings = []
    
    # Check for app.py
    if os.path.exists('app.py'):
        print("✓ app.py found")
    else:
        errors.append("✗ app.py not found in current directory")
    
    # Check for templates folder
    if os.path.exists('templates'):
        print("✓ templates/ folder found")
        if os.path.exists('templates/index.html'):
            print("  ✓ index.html found")
        else:
            errors.append("  ✗ templates/index.html not found")
    else:
        errors.append("✗ templates/ folder not found")
    
    # Check for static folder
    if os.path.exists('static'):
        print("✓ static/ folder found")
        
        if os.path.exists('static/css'):
            print("  ✓ static/css/ folder found")
            if os.path.exists('static/css/styles.css'):
                print("    ✓ styles.css found")
            else:
                errors.append("    ✗ static/css/styles.css not found")
        else:
            errors.append("  ✗ static/css/ folder not found")
        
        if os.path.exists('static/js'):
            print("  ✓ static/js/ folder found")
            if os.path.exists('static/js/app.js'):
                print("    ✓ app.js found")
            else:
                errors.append("    ✗ static/js/app.js not found")
        else:
            errors.append("  ✗ static/js/ folder not found")
    else:
        errors.append("✗ static/ folder not found")
    
    # Check for requirements.txt
    if os.path.exists('requirements.txt'):
        print("✓ requirements.txt found")
    else:
        warnings.append("⚠ requirements.txt not found (optional)")
    
    print()
    print("=" * 60)
    
    if errors:
        print("ERRORS FOUND:")
        for error in errors:
            print(error)
        print()
        print("SOLUTION:")
        print("Make sure you're running from the correct directory.")
        print("The folder structure should be:")
        print("""
your-project-folder/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── styles.css
    └── js/
        └── app.js
        """)
        return False
    else:
        print("✓ All required files found!")
        if warnings:
            print()
            for warning in warnings:
                print(warning)
        print()
        print("You're ready to run: python app.py")
        return True

if __name__ == "__main__":
    success = check_setup()
    sys.exit(0 if success else 1)
