# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based tool for bulk downloading feedback metadata and attachments from the EU Better Regulation Portal (https://ec.europa.eu/info/law/better-regulation/have-your-say/). The tool scrapes public consultation feedback for legislative initiatives using the Better Regulation Portal API.

**Key Capabilities**:
1. **List all initiatives** - `eu-lobbyscraper-list` CLI command
2. **Download initiative feedback** - `eu-lobbyscraper-download` CLI command
3. **Document conversion** - Convert downloaded attachments to Markdown using Pandoc

**Project Structure**:
- `eu_lobbyscraper/` - Python package with all core modules and CLI entry points
- `examples/` - Example usage scripts
- `docs/` - Documentation files
- `data/` - Downloaded data (gitignored)

## Core Architecture

### Main Module: `eu_lobbyscraper/downloader.py`

The codebase centers around the `EUFeedbackDownloader` class in `eu_lobbyscraper/downloader.py`, which handles the complete download workflow:

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

1. **`eu_lobbyscraper/converter.py`**: Core conversion module with `DocumentConverter` class
   - Uses Pandoc for universal document conversion
   - Supports PDF, DOCX, XLSX, PPTX, EPUB, HTML, and many more formats
   - Native conversion without intermediate steps
   - Optional media extraction

2. **`eu_lobbyscraper/batch_converter.py`**: Batch conversion module with `AttachmentMarkdownConverter` class
   - Processes entire initiative directories
   - Selective publication processing
   - Skip already-converted files
   - Comprehensive statistics reporting

3. **Integration in the downloader**:
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

Downloaded data is saved to the `data/` directory by default:

```
data/
├── initiative_{id}_feedback/
│   ├── initiative_metadata.json          # Top-level initiative details
│   ├── consolidated_feedback.json        # All feedback from all publications
│   └── publication_{pub_id}/
│       ├── feedback_metadata.json        # Array of all feedback with downloadUrl fields
│       ├── summary.json                  # Statistics (total feedback, attachments)
│       └── attachments/
│           ├── feedback_{id}_{filename}      # Downloaded files (if --download-attachments used)
│           └── feedback_{id}_{filename}.md   # Markdown conversions (if --convert-to-markdown used)
├── all_initiatives.json              # List of all initiatives
└── initiatives.csv                   # CSV export of initiatives
```

## Common Commands

### Listing All Initiatives

```bash
eu-lobbyscraper-list
eu-lobbyscraper-list --topic CLIMA -o data/climate_initiatives.json
eu-lobbyscraper-list --max 100 --csv data/test.csv
```

### Running the Downloader

```bash
eu-lobbyscraper-download <initiative_id>
eu-lobbyscraper-download <initiative_id> --download-attachments
eu-lobbyscraper-download <initiative_id> --download-attachments --convert-to-markdown
eu-lobbyscraper-download <initiative_id> --download-attachments --convert-to-markdown --extract-media
```

### Document Conversion Commands

```bash
eu-lobbyscraper-convert document.pdf
eu-lobbyscraper-convert report.docx -o output.md
eu-lobbyscraper-batch-convert data/initiative_14855_feedback
eu-lobbyscraper-batch-convert data/initiative_14855_feedback -p 20401
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

The package interacts with these EU Better Regulation Portal endpoints:

- `GET /brpapi/searchInitiatives?page={page}&size={size}` - List all initiatives (paginated, used by lister module)
- `GET /brpapi/groupInitiatives/{id}` - Initiative metadata
- `GET /api/allFeedback?publicationId={pub_id}&page={page}&size={size}` - Feedback items (paginated)
- `GET /api/download/{documentId}` - Binary attachment downloads

All endpoints use base URL: `https://ec.europa.eu/info/law/better-regulation`

## Important Implementation Details

### Finding Initiative IDs

**Method 1: List all initiatives**
Use the lister to discover initiatives by topic, status, or browse all:
```bash
eu-lobbyscraper-list
eu-lobbyscraper-list --topic CLIMA
```

**Method 2: Extract from URLs**
Extract the numeric ID from Better Regulation Portal URLs:
```
https://ec.europa.eu/info/law/better-regulation/have-your-say/initiatives/14855-Simplification-digital-package-and-omnibus_en
                                                                              ^^^^^
```

### Session Management

The `EUFeedbackDownloader` uses `requests.Session()` with a Mozilla User-Agent to maintain consistent headers across all requests.

### Metadata-Driven Workflows

The `downloadUrl` field injected into attachment metadata enables selective post-processing. See `examples/example_download_from_metadata.py` for filtering patterns:
- Download by organization name
- Filter by file size or type
- Select based on country or user type
- Process attachments days/weeks after initial metadata collection

### Error Handling

The script uses `raise_for_status()` for HTTP errors and includes try/except blocks around individual attachment downloads to continue processing even if individual files fail.
