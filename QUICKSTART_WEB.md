# Quick Start - Web Version

Get your web-based file renamer running in 2 minutes!

## Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python app.py

# 3. Open in browser
# Navigate to: http://localhost:5000
```

That's it! 🎉

## First Rename in 60 Seconds

### 1. Prepare Excel File (10 seconds)
Open Excel and create:

| Column A        | Column B        |
|----------------|-----------------|
| document.pdf   | report.pdf      |
| image.jpg      | photo.jpg       |

Save as `mapping.xlsx`

### 2. Upload to Web App (20 seconds)

**Step 1:** Upload Excel file
- Drag `mapping.xlsx` to the first upload area
- Wait for ✓ confirmation

**Step 2:** Upload Files
- Drag `document.pdf` and `image.jpg` to second area
- Wait for ✓ confirmation

### 3. Rename! (30 seconds)

- Click **"Preview Renames"**
- Review the table (should show 2 READY items)
- Click **"Execute Renames"**
- Click **"Download Renamed Files"**

Done! Your files are renamed in a ZIP file.

## Web Interface Overview

```
┌─────────────────────────────────────┐
│       📁 File Renamer               │
│   Batch rename files using Excel   │
└─────────────────────────────────────┘

┌─ 01 Upload Excel Mapping ──────────┐
│  📊 Drop Excel file here...         │
│  Column A: Current • Column B: New  │
└─────────────────────────────────────┘

┌─ 02 Upload Files to Rename ────────┐
│  📄 Drop files here...              │
│  Select multiple files              │
└─────────────────────────────────────┘

┌─ 03 Preview & Execute ─────────────┐
│  [👁️ Preview] [⚡ Execute]          │
│                                     │
│  Status Table:                      │
│  ✓ READY    | old.pdf → new.pdf    │
│  ✓ READY    | img.jpg → pic.jpg    │
│                                     │
│  [📥 Download] [📄 Report] [🔄]     │
└─────────────────────────────────────┘
```

## Common Scenarios

### Organizing Photos
```
Upload mapping.xlsx:
  IMG_001.jpg → Vacation_Paris_001.jpg
  IMG_002.jpg → Vacation_Paris_002.jpg
  IMG_003.jpg → Vacation_Paris_003.jpg

Upload 3 photos → Preview → Execute → Download
```

### Standardizing Documents
```
Upload mapping.xlsx:
  draft_v1.docx    → Final_Report.docx
  notes_temp.txt   → Meeting_Notes.txt
  data_old.xlsx    → Sales_Data.xlsx

Upload 3 documents → Preview → Execute → Download
```

### Adding Date Stamps
```
Excel formula in B2:
  =TEXT(TODAY(),"yyyy-mm-dd") & "_" & A2

Result:
  report.pdf → 2025-02-12_report.pdf
  data.xlsx  → 2025-02-12_data.xlsx
```

## Status Indicators

**🟢 READY** - File ready to rename
- Source file found
- No conflicts
- No duplicates

**🟡 WARNING** - Will skip
- Same name (no change needed)
- Non-critical issues

**🔴 ERROR** - Must fix
- Source file not found
- Duplicate new names
- Target file exists

## Tips & Tricks

### 1. Excel Formulas for Bulk Renaming

**Add Prefix:**
```excel
="ProjectA_" & A2
```

**Sequential Numbers:**
```excel
="File_" & TEXT(ROW()-1,"000") & ".pdf"
```

**Replace Text:**
```excel
=SUBSTITUTE(A2,"draft","final")
```

### 2. Processing Large Batches

- Break into groups of 100-200 files
- Upload → Rename → Download
- Repeat for next batch

### 3. Double-Check Before Execute

✓ Review ALL status indicators
✓ Check new names are correct
✓ Verify no red ERROR items
✓ Confirm ready count is expected

### 4. Keep Your Excel File

Save your mapping Excel for:
- Reference of what was renamed
- Reversing renames if needed
- Similar future renaming tasks

## Troubleshooting Quick Fixes

**Excel won't upload?**
- ✓ Save as `.xlsx` format
- ✓ Check file has 2 columns
- ✓ Close Excel before uploading

**Files won't upload?**
- ✓ Total size under 100MB
- ✓ Valid filenames (no special chars)
- ✓ Browser allows uploads

**Preview shows errors?**
- ✓ File names match exactly
- ✓ No duplicate new names
- ✓ Include file extensions

**Download doesn't work?**
- ✓ Check popup blockers
- ✓ Try different browser
- ✓ Check Downloads folder

## Pro Workflows

### Workflow 1: Test First
```bash
1. Upload mapping with 2-3 files only
2. Preview and test
3. If good, upload all files
4. Execute full batch
```

### Workflow 2: Multiple Operations
```bash
1. First rename: old → intermediate
2. Download ZIP
3. Extract files
4. Second rename: intermediate → final
5. Download final ZIP
```

### Workflow 3: Version Control
```bash
1. Before renaming, copy original files
2. Upload and rename via web app
3. Compare renamed vs originals
4. Keep backup of Excel mapping
```

## Access from Other Devices

### Same Network
```
1. Find your computer's IP: ifconfig or ipconfig
2. Run: python app.py
3. On other device, open: http://YOUR_IP:5000
```

### Localhost Only (default)
```
http://localhost:5000
or
http://127.0.0.1:5000
```

## Next Steps

✓ **Read full documentation**: README_WEB.md
✓ **Try test setup**: Create sample files
✓ **Explore Excel formulas**: For advanced renaming
✓ **Bookmark the app**: For easy access

## Need Help?

1. Check error message in web interface
2. Review preview table carefully
3. Export report for detailed analysis
4. Read README_WEB.md for full docs

---

**Happy Renaming! Upload, preview, execute - it's that easy! 🚀**
