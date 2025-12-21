# EU Better Regulation Portal Tools - Complete Feature Summary

## Overview

This toolkit provides comprehensive access to the EU Better Regulation Portal's public consultation data. You can list all initiatives, download feedback metadata, download attachments, and convert documents to markdown.

## 🎯 Core Tools

### 1. `list_all_initiatives.py` - NEW!
**Bulk initiative metadata fetcher with optional feedback download**

```bash
# Basic usage - list all initiatives
python3 list_all_initiatives.py

# Export to CSV for spreadsheet analysis
python3 list_all_initiatives.py --csv initiatives.csv

# Download all feedback metadata (slow but comprehensive)
python3 list_all_initiatives.py --max 10 --download-feedback
```

**What it does:**
- Downloads metadata for all ~3,800+ initiatives from the portal
- Exports to JSON and/or CSV formats
- Optionally downloads all feedback metadata in bulk
- Filters by topic, status, etc.
- Generates statistics automatically

### 2. `download_initiative_feedback.py`
**Individual initiative feedback and attachment downloader**

```bash
# Download metadata only
python3 download_initiative_feedback.py 14855

# Download with attachments
python3 download_initiative_feedback.py 14855 --download-attachments

# Download and convert to markdown
python3 download_initiative_feedback.py 14855 --download-attachments --convert-to-markdown
```

**What it does:**
- Downloads all feedback for a specific initiative
- Downloads PDF, DOCX, and other file attachments
- Organizes by publication ID
- Preserves download URLs for post-processing

### 3. `document_converter.py`
**Universal document to markdown converter**

```bash
# Convert single document
python3 document_converter.py document.pdf

# With media extraction
python3 document_converter.py report.docx --extract-media
```

### 4. `convert_attachments_to_markdown.py`
**Batch converter for existing downloads**

```bash
# Convert all attachments in an initiative
python3 convert_attachments_to_markdown.py initiative_14855_feedback

# Convert specific publication
python3 convert_attachments_to_markdown.py initiative_14855_feedback -p 20401
```

## 📊 Complete Feature Matrix

| Feature | list_all_initiatives.py | download_initiative_feedback.py |
|---------|------------------------|--------------------------------|
| List all initiatives | ✅ | ❌ |
| Export to CSV | ✅ | ❌ |
| Download feedback metadata | ✅ (with --download-feedback) | ✅ |
| Download attachments | ❌ | ✅ (with --download-attachments) |
| Convert to markdown | ❌ | ✅ (with --convert-to-markdown) |
| Filter by topic/status | ✅ | ❌ |
| Generate statistics | ✅ | ❌ |
| Bulk processing | ✅ | ❌ (one at a time) |

## 🚀 Common Workflows

### Workflow 1: Discovery & Selective Download
```bash
# 1. Export all initiatives to CSV
python3 list_all_initiatives.py --csv all_initiatives.csv

# 2. Open in Excel/Google Sheets, filter by topic/status

# 3. Download specific initiatives with attachments
python3 download_initiative_feedback.py 14855 --download-attachments
```

### Workflow 2: Bulk Feedback Analysis
```bash
# Download all climate initiative feedback in one go
python3 list_all_initiatives.py --topic CLIMA --download-feedback -o climate_feedback.json

# Analyze feedback patterns, organizations, countries
python3 analyze_feedback.py climate_feedback.json
```

### Workflow 3: Topic Research with Documents
```bash
# 1. List all climate initiatives
python3 list_all_initiatives.py --topic CLIMA -o climate.json

# 2. Download specific ones with attachments and markdown conversion
python3 download_initiative_feedback.py 15772 --download-attachments --convert-to-markdown
```

### Workflow 4: Complete Archive
```bash
# WARNING: This will take many hours and use significant disk space

# Download all initiatives with all feedback
python3 list_all_initiatives.py --download-feedback -o complete_archive.json

# Then download attachments for specific high-value initiatives
# (Based on analysis of the complete_archive.json)
```

## 📈 Performance Characteristics

### Metadata Only
- **All ~3,800 initiatives**: ~2-3 minutes
- **JSON output**: ~20-30 MB
- **CSV output**: ~1-2 MB

### With Feedback Download
- **10 initiatives**: ~30-60 seconds
- **100 initiatives**: ~5-10 minutes
- **All initiatives**: ~3-6 hours
- **Output size**: Highly variable (100+ MB)

### Individual Initiative Downloads
- **Metadata only**: ~5-10 seconds
- **With attachments**: ~30 seconds - 5 minutes (depends on attachment count/size)
- **With markdown conversion**: Add ~50% more time

## 🎛️ Output Formats

### JSON (Full Metadata)
```json
{
  "metadata": { ... },
  "statistics": { ... },
  "initiatives": [
    {
      "id": 16192,
      "initiativeUrl": "...",
      "shortTitle": "...",
      "publications": [...],  // When using --download-feedback
      "feedbackItems": [...]   // Nested under publications
    }
  ]
}
```

### CSV (Spreadsheet Format)
```
id,initiativeUrl,shortTitle,reference,initiativeStatus,foreseenActType,
topicCodes,topicLabels,feedbackStatus,feedbackStartDate,feedbackEndDate,currentStage
16192,https://...,EU aluminium sector...,Ares(2025)11338719,ACTIVE,PROP_REG,...
```

## 🔧 Installation & Requirements

### Basic Requirements
```bash
pip install requests
```

### For Document Conversion
```bash
# Ubuntu/Debian
sudo apt-get install pandoc

# macOS
brew install pandoc

# Verify
pandoc --version
```

## 📚 Documentation

- **[README.md](README.md)** - Main documentation
- **[LISTING_INITIATIVES.md](LISTING_INITIATIVES.md)** - Detailed guide for list_all_initiatives.py
- **[CLAUDE.md](CLAUDE.md)** - Developer guidance and architecture

## 🎯 Key Design Decisions

1. **Two-phase operation**: Metadata can be downloaded separately from attachments
2. **URL preservation**: All attachment metadata includes download URLs for post-processing
3. **CSV export**: Enables analysis in spreadsheet tools without JSON knowledge
4. **Bulk feedback download**: New `--download-feedback` flag enables comprehensive data collection
5. **Rate limiting**: Respectful delays built into all tools
6. **Modular design**: Each tool does one thing well, composable workflows

## 🆕 Recent Additions

### CSV Export (NEW)
- Export initiative lists to spreadsheet-friendly CSV format
- Filter and analyze in Excel/Google Sheets
- 12 key fields including URLs, topics, and feedback status

### Bulk Feedback Download (NEW)
- `--download-feedback` flag on list_all_initiatives.py
- Download all feedback metadata for multiple initiatives in one run
- Much faster than looping through individual downloads
- Ideal for bulk research and analysis

## 💡 Tips & Best Practices

1. **Start small**: Use `--max 10` to test before downloading everything
2. **Use CSV for discovery**: Export to CSV, filter in spreadsheets, then download specific items
3. **Metadata first**: Download metadata before attachments to see what's available
4. **Topic filtering**: Use `--topic` to focus on specific policy areas
5. **Feedback download**: Use `--download-feedback` for bulk analysis, `download_initiative_feedback.py` for individual deep dives

## 🔗 API Endpoints

All tools use the public EU Better Regulation Portal API:

- `GET /brpapi/searchInitiatives` - List all initiatives (paginated)
- `GET /brpapi/groupInitiatives/{id}` - Initiative details
- `GET /api/allFeedback` - Feedback items (paginated)
- `GET /api/download/{documentId}` - File downloads

Base URL: `https://ec.europa.eu/info/law/better-regulation`

## 📝 Notes

- All data is publicly available from the EU Better Regulation Portal
- Rate limiting ensures respectful server usage
- CSV export does NOT include feedback items (JSON only)
- Feedback download includes text and metadata, but not attachment files
- Use `download_initiative_feedback.py` for attachment files
