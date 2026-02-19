# File Renamer - Web Application

A modern, user-friendly web application for batch renaming files based on Excel spreadsheet mappings. Upload your Excel file and files directly through your browser - no command line needed!

![File Renamer Web Interface](screenshot.png)

## Features

✨ **Modern Web Interface**
- Beautiful, responsive design that works on all devices
- Drag-and-drop file uploads
- Real-time preview of rename operations
- Interactive status indicators with color-coding

🔒 **Safe & Secure**
- Session-based file isolation
- Comprehensive error detection
- Preview before execute
- Automatic backup logs
- No data stored permanently

⚡ **Powerful Functionality**
- Upload Excel mapping (Column A → Column B)
- Upload multiple files to rename
- Instant validation and error checking
- Download renamed files as ZIP
- Export detailed reports

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

### 3. Open in Browser

Navigate to: `http://localhost:5000`

That's it! 🎉

## How to Use

### Step 1: Prepare Your Excel File

Create an Excel spreadsheet with two columns:

| Column A (Current) | Column B (New) |
|-------------------|----------------|
| old_file_1.pdf    | new_file_1.pdf |
| old_file_2.jpg    | new_file_2.jpg |
| old_file_3.docx   | new_file_3.docx |

**Important:**
- Column A: Current file names (exactly as they are)
- Column B: Desired new file names
- Include file extensions (e.g., `.pdf`, `.jpg`)
- File names are case-sensitive

### Step 2: Upload Excel File

1. Click the Excel upload area or drag your `.xlsx` file
2. Wait for confirmation (shows mapping count)
3. The system validates your Excel structure

### Step 3: Upload Files to Rename

1. Click the files upload area or drag multiple files
2. Upload all files mentioned in your Excel mapping
3. Confirmation shows how many files were uploaded

### Step 4: Preview & Execute

1. Click **"Preview Renames"** to analyze operations
2. Review the status table:
   - **READY** (Green): File ready to rename
   - **WARNING** (Yellow): Skipped items (same name)
   - **ERROR** (Red): Problems that must be fixed
3. If everything looks good, click **"Execute Renames"**
4. Download your renamed files as a ZIP archive

## Error Handling

The application detects and clearly reports:

### ❌ Source File Not Found
**Problem**: Current file name in Excel doesn't match uploaded file
**Solution**: Check spelling, case, and file extension

### ❌ Duplicate New Names
**Problem**: Multiple files mapping to the same new name
**Solution**: Each new name must be unique in Column B

### ❌ Target Name Already Exists
**Problem**: A file with the new name already exists
**Solution**: Choose a different new name or remove the existing file

### ⚠️ Same Name Warning
**Info**: Current and new names are identical
**Impact**: File will be skipped (no error)

## API Endpoints

The application provides these REST API endpoints:

### POST `/upload_excel`
Upload Excel mapping file
- **Input**: Excel file (.xlsx, .xls)
- **Returns**: Validation status and mapping count

### POST `/upload_files`
Upload files to be renamed
- **Input**: Multiple files
- **Returns**: Upload status and file count

### POST `/preview`
Preview rename operations
- **Returns**: Analysis of all rename operations with status

### POST `/execute`
Execute rename operations
- **Returns**: Results of rename operations

### GET `/download`
Download renamed files as ZIP
- **Returns**: ZIP archive of renamed files

### POST `/download_report`
Download detailed text report
- **Input**: Results data
- **Returns**: Text file with full report

### POST `/reset`
Reset session and cleanup
- **Returns**: Success status

## Architecture

### Backend (Flask)
- **app.py** - Main Flask application with all routes
- Session-based file management
- Secure file handling with `werkzeug`
- Pandas for Excel processing

### Frontend
- **templates/index.html** - Single-page application layout
- **static/css/styles.css** - Modern, distinctive styling
- **static/js/app.js** - Interactive functionality
- Drag-and-drop file uploads
- Real-time status updates
- Responsive design

### File Structure
```
.
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── static/
│   ├── css/
│   │   └── styles.css    # Styling
│   └── js/
│       └── app.js        # Frontend logic
├── uploads/              # Temporary upload storage
└── temp/                 # Session-based processing
```

## Security Features

🔐 **Session Isolation**
- Each user gets a unique session folder
- Files are isolated between users
- Automatic cleanup on reset

🛡️ **File Validation**
- Validates Excel file structure
- Secure filename handling
- File type checking
- Size limits (100MB max)

🧹 **Automatic Cleanup**
- Session folders are temporary
- Files cleanup on reset
- No permanent storage

## Configuration

You can customize the application by modifying these settings in `app.py`:

```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Max upload size
app.config['UPLOAD_FOLDER'] = 'uploads'                # Upload directory
app.config['TEMP_FOLDER'] = 'temp'                     # Temporary files
```

## Deployment

### Local Development
```bash
python app.py
# Runs on http://localhost:5000
```

### Production Deployment

**Using Gunicorn:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Using Docker:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

**Environment Variables:**
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
```

## Browser Compatibility

✅ Chrome/Edge (90+)
✅ Firefox (88+)
✅ Safari (14+)
✅ Mobile browsers

## Troubleshooting

### Excel Upload Fails
- Ensure file is `.xlsx` or `.xls` format
- Check file has at least 2 columns
- Verify file isn't corrupted

### Files Upload Fails
- Check total size is under 100MB
- Verify filenames are valid
- Ensure browser allows file uploads

### Preview Shows Errors
- Review error messages in the table
- Check file names match exactly
- Verify no duplicate new names

### Download Doesn't Work
- Try a different browser
- Check popup blockers
- Verify files were successfully renamed

## Performance

- **Small batches** (<50 files): Instant
- **Medium batches** (50-500 files): ~1-2 seconds
- **Large batches** (500+ files): ~3-5 seconds

Upload speeds depend on your internet connection.

## Advanced Tips

### Batch Renaming Patterns

Use Excel formulas for efficient renaming:

```excel
// Add prefix
="ProjectA_" & A2

// Add date stamp
=TEXT(TODAY(),"yyyy-mm-dd") & "_" & A2

// Sequential numbering
="File_" & TEXT(ROW()-1,"000") & ".pdf"

// Replace text
=SUBSTITUTE(A2,"old","new")
```

### Multiple Rename Operations

For complex workflows:
1. Rename files (first operation)
2. Download renamed ZIP
3. Extract files
4. Upload for second rename operation
5. Repeat as needed

### Integration with Other Tools

The web API can be integrated with other tools:

```python
import requests

# Upload Excel
with open('mapping.xlsx', 'rb') as f:
    r = requests.post('http://localhost:5000/upload_excel', 
                     files={'excel': f})

# Upload files
files = [('files[]', open(f, 'rb')) for f in file_list]
r = requests.post('http://localhost:5000/upload_files', 
                 files=files)

# Preview
r = requests.post('http://localhost:5000/preview')

# Execute
r = requests.post('http://localhost:5000/execute')
```

## Development

### Running in Debug Mode
```bash
export FLASK_ENV=development
python app.py
```

### Testing
```bash
# Create test files
python create_test_setup.py

# Upload test_rename_mapping.xlsx and files from test_rename_files/
```

### Extending the Application

Add new features by:
1. Adding routes in `app.py`
2. Adding UI in `templates/index.html`
3. Adding styles in `static/css/styles.css`
4. Adding logic in `static/js/app.js`

## Support

- **Documentation**: Check this README
- **Issues**: Review error messages in the interface
- **Reports**: Export detailed reports for analysis
- **Reset**: Use "Start Over" button to clear session

## License

Provided as-is for personal and commercial use.

## Credits

Built with:
- **Flask** - Python web framework
- **Pandas** - Excel processing
- **Modern CSS** - Distinctive design
- **Vanilla JavaScript** - No framework dependencies

## Version History

**v2.0** (Current - Web Version)
- Modern web interface
- Drag-and-drop uploads
- Session-based processing
- Real-time preview
- ZIP download
- Responsive design

**v1.0** (Desktop Version)
- GUI and CLI applications
- Local file processing

---

**Ready to rename? Upload your files and get started! 🚀**
