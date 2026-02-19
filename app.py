#!/usr/bin/env python3
"""
File Renamer Web Application - Backend
Flask server with file upload and rename functionality
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import pandas as pd
import os
import zipfile
import io
from datetime import datetime
from collections import Counter
import secrets
import shutil
from pathlib import Path

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TEMP_FOLDER'] = 'temp'

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

ALLOWED_EXCEL = {'xlsx', 'xls'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_session_folder():
    """Get or create a unique folder for this session"""
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)
    
    session_folder = os.path.join(app.config['TEMP_FOLDER'], session['session_id'])
    os.makedirs(session_folder, exist_ok=True)
    return session_folder

def cleanup_session():
    """Clean up session folder"""
    if 'session_id' in session:
        session_folder = os.path.join(app.config['TEMP_FOLDER'], session['session_id'])
        if os.path.exists(session_folder):
            shutil.rmtree(session_folder)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_excel', methods=['POST'])
def upload_excel():
    """Handle Excel file upload"""
    try:
        if 'excel' not in request.files:
            return jsonify({'success': False, 'error': 'No Excel file provided'})
        
        file = request.files['excel']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not allowed_file(file.filename, ALLOWED_EXCEL):
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload .xlsx or .xls file'})
        
        # Save Excel file
        session_folder = get_session_folder()
        excel_path = os.path.join(session_folder, 'mapping.xlsx')
        file.save(excel_path)
        
        # Read and validate Excel
        df = pd.read_excel(excel_path, engine='openpyxl')
        
        if df.shape[1] < 2:
            return jsonify({
                'success': False,
                'error': 'Excel file must have at least 2 columns (Current names → New names)'
            })
        
        # Use first three columns if available
        if df.shape[1] >= 3:
            df = df.iloc[:, :3]
            df.columns = ['current', 'new', 'category']
        else:
            df = df.iloc[:, :2]
            df.columns = ['current', 'new']
            df['category'] = ''  # Add empty category column
        
        # Clean data
        df = df.dropna(how='all')
        df['current'] = df['current'].astype(str).str.strip()
        df['new'] = df['new'].astype(str).str.strip()
        df['category'] = df['category'].astype(str).str.strip().str.upper()
        
        df = df[(df['current'] != '') & (df['current'] != 'nan') & 
                (df['new'] != '') & (df['new'] != 'nan')]
        
        if df.empty:
            return jsonify({
                'success': False,
                'error': 'No valid rename mappings found in Excel file'
            })
        
        # Count categories
        active_count = len(df[df['category'] == 'A'])
        terminated_count = len(df[df['category'] == 'T'])
        uncategorized_count = len(df[(df['category'] != 'A') & (df['category'] != 'T')])
        
        # Save cleaned mapping
        session['mapping_count'] = len(df)
        df.to_json(os.path.join(session_folder, 'mapping.json'), orient='records')
        
        message = f'Excel file loaded: {len(df)} rename mappings found'
        if active_count > 0 or terminated_count > 0:
            message += f' (Active: {active_count}, Terminated: {terminated_count}'
            if uncategorized_count > 0:
                message += f', Uncategorized: {uncategorized_count}'
            message += ')'
        
        return jsonify({
            'success': True,
            'count': len(df),
            'message': message
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error processing Excel file: {str(e)}'})

@app.route('/upload_files', methods=['POST'])
def upload_files():
    """Handle multiple file uploads"""
    try:
        if 'files[]' not in request.files:
            return jsonify({'success': False, 'error': 'No files provided'})
        
        files = request.files.getlist('files[]')
        if not files or files[0].filename == '':
            return jsonify({'success': False, 'error': 'No files selected'})
        
        # Save files
        session_folder = get_session_folder()
        files_folder = os.path.join(session_folder, 'files')
        os.makedirs(files_folder, exist_ok=True)
        
        uploaded_files = []
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(files_folder, filename)
                file.save(filepath)
                uploaded_files.append(filename)
        
        session['uploaded_files'] = uploaded_files
        
        return jsonify({
            'success': True,
            'count': len(uploaded_files),
            'files': uploaded_files,
            'message': f'{len(uploaded_files)} file(s) uploaded successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error uploading files: {str(e)}'})

@app.route('/preview', methods=['POST'])
def preview():
    """Preview rename operations"""
    try:
        session_folder = get_session_folder()
        
        # Load mapping
        mapping_path = os.path.join(session_folder, 'mapping.json')
        if not os.path.exists(mapping_path):
            return jsonify({'success': False, 'error': 'Please upload Excel file first'})
        
        df = pd.read_json(mapping_path, orient='records')
        
        # Get uploaded files
        files_folder = os.path.join(session_folder, 'files')
        if not os.path.exists(files_folder):
            return jsonify({'success': False, 'error': 'Please upload files first'})
        
        uploaded_files = set(os.listdir(files_folder))
        
        # Create a map of base filenames (without extension) to actual filenames
        file_base_map = {}
        for filename in uploaded_files:
            # Get base name without extension
            base_name = os.path.splitext(filename)[0]
            file_base_map[base_name.lower()] = filename
        
        # Handle duplicate new names by appending (1), (2), etc.
        new_name_counts = {}
        final_new_names = []
        
        for new_name in df['new']:
            if new_name in new_name_counts:
                # Duplicate found - add counter
                new_name_counts[new_name] += 1
                counter = new_name_counts[new_name]
                
                # Split filename and extension
                name_without_ext = os.path.splitext(new_name)[0]
                extension = os.path.splitext(new_name)[1]
                
                # Create new name with counter
                unique_name = f"{name_without_ext} ({counter}){extension}"
                final_new_names.append(unique_name)
            else:
                new_name_counts[new_name] = 0
                final_new_names.append(new_name)
        
        # Update dataframe with unique names
        df['original_new'] = df['new']  # Keep track of original
        df['new'] = final_new_names
        
        # Check for conflicts
        existing_conflicts = {}
        for new_name in df['new'].unique():
            if new_name in uploaded_files and new_name not in df['current'].values:
                existing_conflicts[new_name] = new_name
        
        # Process each rename
        results = []
        ready_count = 0
        warning_count = 0
        error_count = 0
        active_count = 0
        terminated_count = 0
        renamed_count = 0  # Count of names that were auto-renamed due to duplicates
        
        for idx, row in df.iterrows():
            current_name = row['current']
            new_name = row['new']
            original_new = row['original_new']
            category = row.get('category', '').upper().strip() if 'category' in row else ''
            
            # Check if name was modified due to duplicate
            was_renamed = (new_name != original_new)
            if was_renamed:
                renamed_count += 1
            
            # Validate category
            if category and category not in ['A', 'T']:
                category = ''  # Invalid category, treat as uncategorized
            
            status = 'ready'
            notes = []
            matched_file = None
            
            # Try exact match first
            if current_name in uploaded_files:
                matched_file = current_name
            else:
                # Try matching base filename (ignore extension)
                current_base = os.path.splitext(current_name)[0]
                matched_file = file_base_map.get(current_base.lower())
            
            # Check if current file exists
            if not matched_file:
                status = 'error'
                notes.append('Source file not found in uploads')
                error_count += 1
            elif current_name == new_name:
                status = 'warning'
                notes.append('Same name - no change needed')
                warning_count += 1
            elif new_name in existing_conflicts:
                status = 'error'
                notes.append('Target name already exists (not in mapping)')
                error_count += 1
            else:
                if was_renamed:
                    notes.append(f'Auto-renamed to avoid duplicate (was: {original_new})')
                
                if category == 'A':
                    if not was_renamed:
                        notes.append('Ready to rename → Active folder')
                    else:
                        notes.append('→ Active folder')
                    active_count += 1
                elif category == 'T':
                    if not was_renamed:
                        notes.append('Ready to rename → Terminated folder')
                    else:
                        notes.append('→ Terminated folder')
                    terminated_count += 1
                else:
                    if not was_renamed:
                        notes.append('Ready to rename')
                ready_count += 1
            
            results.append({
                'status': status,
                'current': current_name,
                'new': new_name,
                'category': category,
                'notes': '; '.join(notes) if notes else 'OK',
                'matched_file': matched_file
            })
        
        # Save updated mapping with unique names
        df.to_json(mapping_path, orient='records')
        
        return jsonify({
            'success': True,
            'results': results,
            'summary': {
                'ready': ready_count,
                'warning': warning_count,
                'error': error_count,
                'total': len(results),
                'active': active_count,
                'terminated': terminated_count,
                'auto_renamed': renamed_count
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error during preview: {str(e)}'})

@app.route('/execute', methods=['POST'])
def execute_renames():
    """Execute rename operations"""
    try:
        session_folder = get_session_folder()
        files_folder = os.path.join(session_folder, 'files')
        
        # Create Active and Terminated folders
        active_folder = os.path.join(session_folder, 'Active')
        terminated_folder = os.path.join(session_folder, 'Terminated')
        uncategorized_folder = files_folder  # Keep uncategorized in original location
        
        os.makedirs(active_folder, exist_ok=True)
        os.makedirs(terminated_folder, exist_ok=True)
        
        # Load mapping
        mapping_path = os.path.join(session_folder, 'mapping.json')
        df = pd.read_json(mapping_path, orient='records')
        
        uploaded_files = set(os.listdir(files_folder))
        
        # Create a map of base filenames to actual filenames
        file_base_map = {}
        for filename in uploaded_files:
            base_name = os.path.splitext(filename)[0]
            file_base_map[base_name.lower()] = filename
        
        # Filter to only ready items
        results = []
        success_count = 0
        fail_count = 0
        active_count = 0
        terminated_count = 0
        uncategorized_count = 0
        
        # Create backup log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_log = []
        backup_log.append(f"Rename Backup Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        backup_log.append("=" * 80 + "\n\n")
        
        for _, row in df.iterrows():
            current_name = row['current']
            new_name = row['new']
            category = row.get('category', '').upper().strip() if 'category' in row else ''
            
            # Find matched file (exact or by base name)
            matched_file = None
            if current_name in uploaded_files:
                matched_file = current_name
            else:
                current_base = os.path.splitext(current_name)[0]
                matched_file = file_base_map.get(current_base.lower())
            
            # Skip if not ready
            if not matched_file or current_name == new_name:
                continue
            
            try:
                current_path = os.path.join(files_folder, matched_file)
                
                # Determine destination folder based on category
                if category == 'A':
                    dest_folder = active_folder
                    folder_name = 'Active'
                    active_count += 1
                elif category == 'T':
                    dest_folder = terminated_folder
                    folder_name = 'Terminated'
                    terminated_count += 1
                else:
                    dest_folder = uncategorized_folder
                    folder_name = 'Root'
                    uncategorized_count += 1
                
                new_path = os.path.join(dest_folder, new_name)
                
                # Rename and move file
                shutil.move(current_path, new_path)
                
                backup_log.append(f"{matched_file} -> {folder_name}/{new_name}\n")
                
                results.append({
                    'status': 'success',
                    'current': current_name,
                    'new': new_name,
                    'category': category,
                    'folder': folder_name,
                    'notes': f'Renamed successfully → {folder_name} folder (was: {matched_file})'
                })
                success_count += 1
                
            except Exception as e:
                results.append({
                    'status': 'failed',
                    'current': current_name,
                    'new': new_name,
                    'category': category,
                    'folder': '',
                    'notes': f'Error: {str(e)}'
                })
                fail_count += 1
        
        # Save backup log
        backup_path = os.path.join(session_folder, f'rename_backup_{timestamp}.txt')
        with open(backup_path, 'w') as f:
            f.writelines(backup_log)
        
        return jsonify({
            'success': True,
            'results': results,
            'summary': {
                'success': success_count,
                'failed': fail_count,
                'total': success_count + fail_count,
                'active': active_count,
                'terminated': terminated_count,
                'uncategorized': uncategorized_count
            },
            'backup_log': f'rename_backup_{timestamp}.txt'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error during rename: {str(e)}'})

@app.route('/download', methods=['GET'])
def download():
    """Download renamed files as zip with folder structure"""
    try:
        session_folder = get_session_folder()
        
        # Create zip file in memory
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add files from Active folder
            active_folder = os.path.join(session_folder, 'Active')
            if os.path.exists(active_folder):
                for filename in os.listdir(active_folder):
                    filepath = os.path.join(active_folder, filename)
                    zf.write(filepath, f'Active/{filename}')
            
            # Add files from Terminated folder
            terminated_folder = os.path.join(session_folder, 'Terminated')
            if os.path.exists(terminated_folder):
                for filename in os.listdir(terminated_folder):
                    filepath = os.path.join(terminated_folder, filename)
                    zf.write(filepath, f'Terminated/{filename}')
            
            # Add backup log if exists
            for file in os.listdir(session_folder):
                if file.startswith('rename_backup_'):
                    backup_path = os.path.join(session_folder, file)
                    zf.write(backup_path, file)
        
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'renamed_files_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error creating download: {str(e)}'})

@app.route('/download_report', methods=['POST'])
def download_report():
    """Download detailed report"""
    try:
        data = request.get_json()
        results = data.get('results', [])
        
        # Separate successful and failed/error results
        successful = [r for r in results if r.get('status', '').lower() in ['success', 'ready']]
        warnings = [r for r in results if r.get('status', '').lower() == 'warning']
        errors = [r for r in results if r.get('status', '').lower() in ['error', 'failed']]
        
        # Create report
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = []
        report.append("=" * 80 + "\n")
        report.append("FILE RENAME REPORT\n")
        report.append("=" * 80 + "\n\n")
        report.append(f"Generated: {timestamp}\n\n")
        
        # Summary section
        report.append("SUMMARY\n")
        report.append("-" * 80 + "\n")
        report.append(f"Total Files: {len(results)}\n")
        report.append(f"✓ Successful: {len(successful)}\n")
        report.append(f"⚠ Warnings: {len(warnings)}\n")
        report.append(f"✗ Errors: {len(errors)}\n")
        report.append("\n\n")
        
        # Successful renames mapping table
        if successful:
            report.append("=" * 80 + "\n")
            report.append("SUCCESSFUL RENAMES - MAPPING TABLE\n")
            report.append("=" * 80 + "\n\n")
            
            # Calculate column widths
            max_old = max([len(r.get('current', '')) for r in successful] + [20])
            max_new = max([len(r.get('new', '')) for r in successful] + [20])
            
            # Table header
            report.append(f"{'ORIGINAL NAME':<{max_old}}  →  {'NEW NAME':<{max_new}}  FOLDER\n")
            report.append(f"{'-' * max_old}     {'-' * max_new}  {'-' * 15}\n")
            
            # Table rows
            for item in successful:
                current = item.get('current', '')
                new = item.get('new', '')
                
                # Determine folder
                folder = item.get('folder', '')
                if not folder and 'category' in item:
                    cat = item.get('category', '')
                    if cat == 'A':
                        folder = 'Active'
                    elif cat == 'T':
                        folder = 'Terminated'
                    else:
                        folder = 'Root'
                elif not folder:
                    folder = 'Root'
                
                report.append(f"{current:<{max_old}}  →  {new:<{max_new}}  {folder}\n")
            
            report.append("\n")
        
        # Warnings section
        if warnings:
            report.append("=" * 80 + "\n")
            report.append("WARNINGS\n")
            report.append("=" * 80 + "\n\n")
            
            for idx, item in enumerate(warnings, 1):
                report.append(f"{idx}. {item.get('current', 'N/A')}\n")
                report.append(f"   Reason: {item.get('notes', 'No details')}\n")
                report.append("\n")
        
        # Errors section
        if errors:
            report.append("=" * 80 + "\n")
            report.append("ERRORS (Files Not Renamed)\n")
            report.append("=" * 80 + "\n\n")
            
            for idx, item in enumerate(errors, 1):
                report.append(f"{idx}. {item.get('current', 'N/A')} → {item.get('new', 'N/A')}\n")
                report.append(f"   Issue: {item.get('notes', 'No details')}\n")
                report.append("\n")
        
        # Footer
        report.append("\n")
        report.append("=" * 80 + "\n")
        report.append("End of Report\n")
        report.append("=" * 80 + "\n")
        
        # Create file in memory
        memory_file = io.BytesIO()
        memory_file.write(''.join(report).encode('utf-8'))
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            mimetype='text/plain',
            as_attachment=True,
            download_name=f'rename_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error creating report: {str(e)}'})

@app.route('/reset', methods=['POST'])
def reset():
    """Reset session and cleanup files"""
    try:
        cleanup_session()
        session.clear()
        return jsonify({'success': True, 'message': 'Session reset successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error resetting session: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
