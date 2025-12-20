# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based tool for bulk downloading feedback metadata and attachments from the EU Better Regulation Portal (https://ec.europa.eu/info/law/better-regulation/have-your-say/). The tool scrapes public consultation feedback for legislative initiatives using the Better Regulation Portal API.

**New Feature**: The tool now includes document-to-markdown conversion capabilities using Pandoc, a universal document converter that handles PDF, Office documents, and many other formats natively.

## Core Architecture

### Main Script: `download_initiative_feedback.py`

The codebase centers around the `EUFeedbackDownloader` class, which handles the complete download workflow:

1. **Initiative Metadata Fetching** (`get_initiative_data`): Retrieves top-level initiative information from `/brpapi/groupInitiatives/{id}` endpoint
2. **Feedback Pagination** (`get_all_feedback`): Iterates through paginated feedback using `/api/allFeedback?publicationId={pub_id}&page={page}&size={size}`, handling 100 items per page
3. **URL Injection**: Automatically adds `downloadUrl` fields to all attachment metadata, enabling selective downloading without re-querying the API
4. **Attachment Downloads** (`download_attachment`): Downloads individual files from `/api/download/{documentId}` with rate limiting (0.3-0.5 second delays)
5. **Publication Processing** (`process_publication`): Orchestrates the above steps for each publication in an initiative

### Key Design Decisions

- **Two-Phase Operation**: Metadata is always downloaded; attachments are optional via `--download-attachments` flag
- **Download URL Preservation**: All attachment metadata includes constructed `downloadUrl` fields, even in metadata-only mode, enabling post-processing workflows (see `example_download_from_metadata.py`)
- **Rate Limiting**: Built-in delays between requests to avoid overwhelming EU servers
- **Collision Prevention**: Attachment filenames are prefixed with `feedback_{id}_` to prevent conflicts when multiple submissions use identical filenames
- **Pagination Handling**: Automatically handles large datasets by iterating through pages until `totalPages` is reached

### Document Conversion Architecture

The tool includes three additional modules for document conversion:

1. **`document_converter.py`**: Core conversion module with `DocumentConverter` class
   - Uses Pandoc for universal document conversion
   - Supports PDF, DOCX, XLSX, PPTX, EPUB, HTML, and many more formats
   - Native conversion without intermediate steps
   - Optional media extraction

2. **`convert_attachments_to_markdown.py`**: Batch conversion script
   - Processes entire initiative directories
   - Selective publication processing
   - Skip already-converted files
   - Comprehensive statistics reporting

3. **Integration in `download_initiative_feedback.py`**:
   - `--convert-to-markdown` flag for automatic conversion during download
   - `--extract-media` flag to extract images and embedded media
   - Optional converter initialization only when needed

### Data Flow

```
Initiative ID → Initiative Metadata (JSON) → Publications List
                                                    ↓
                            For each publication: Feedback Items (paginated)
                                                    ↓
                            Feedback Metadata + Injected Download URLs
                                                    ↓
                            (Optional) Download Attachments using documentId
                                                    ↓
                            (Optional) Convert to Markdown using Pandoc
                                - Direct conversion for all supported formats
                                - Optional media extraction
```

### Output Structure

```
initiative_{id}_feedback/
├── initiative_metadata.json          # Top-level initiative details
├── consolidated_feedback.json        # All feedback from all publications
├── publication_{pub_id}/
│   ├── feedback_metadata.json        # Array of all feedback with downloadUrl fields
│   ├── summary.json                  # Statistics (total feedback, attachments)
│   └── attachments/
│       ├── feedback_{id}_{filename}      # Downloaded files (if --download-attachments used)
│       └── feedback_{id}_{filename}.md   # Markdown conversions (if --convert-to-markdown used)
```

## Common Commands

### Running the Downloader

**Metadata only (no file downloads):**
```bash
python3 download_initiative_feedback.py <initiative_id>
```

**Metadata + all attachments:**
```bash
python3 download_initiative_feedback.py <initiative_id> --download-attachments
```

**Custom output directory:**
```bash
python3 download_initiative_feedback.py <initiative_id> -o <output_dir> [--download-attachments]
```

**Metadata + attachments + markdown conversion:**
```bash
python3 download_initiative_feedback.py <initiative_id> --download-attachments --convert-to-markdown
```

**Extract images and media when converting documents:**
```bash
python3 download_initiative_feedback.py <initiative_id> --download-attachments --convert-to-markdown --extract-media
```

### Document Conversion Commands

**Convert a single document:**
```bash
python3 document_converter.py document.pdf
python3 document_converter.py report.docx -o output.md
```

**Batch convert existing attachments:**
```bash
# Convert all attachments in an initiative
python3 convert_attachments_to_markdown.py initiative_14855_feedback

# Convert specific publication
python3 convert_attachments_to_markdown.py initiative_14855_feedback -p 20401

# Convert all initiative directories
python3 convert_attachments_to_markdown.py --all
```

### Dependencies

Install required libraries:
```bash
# Basic requirements
pip install requests

# Optional: Document conversion (requires Pandoc)
# Ubuntu/Debian: sudo apt-get install pandoc
# macOS: brew install pandoc
# Windows: https://pandoc.org/installing.html

# Verify installation
pandoc --version
```

**Requirements**:
- Basic: Python 3.6+ and the `requests` library
- Conversion: Pandoc (system-wide installation)

## API Endpoints

The script interacts with these EU Better Regulation Portal endpoints:

- `GET /brpapi/groupInitiatives/{id}` - Initiative metadata
- `GET /api/allFeedback?publicationId={pub_id}&page={page}&size={size}` - Feedback items (paginated)
- `GET /api/download/{documentId}` - Binary attachment downloads

All endpoints use base URL: `https://ec.europa.eu/info/law/better-regulation`

## Important Implementation Details

### Finding Initiative IDs

Extract the numeric ID from Better Regulation Portal URLs:
```
https://ec.europa.eu/info/law/better-regulation/have-your-say/initiatives/14855-Simplification-digital-package-and-omnibus_en
                                                                              ^^^^^
```

### Session Management

The `EUFeedbackDownloader` uses `requests.Session()` with a Mozilla User-Agent to maintain consistent headers across all requests.

### Metadata-Driven Workflows

The `downloadUrl` field injected into attachment metadata enables selective post-processing. See `example_download_from_metadata.py` for filtering patterns:
- Download by organization name
- Filter by file size or type
- Select based on country or user type
- Process attachments days/weeks after initial metadata collection

### Error Handling

The script uses `raise_for_status()` for HTTP errors and includes try/except blocks around individual attachment downloads to continue processing even if individual files fail.
