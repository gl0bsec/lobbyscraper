# EU Better Regulation Portal - Feedback Downloader

A Python package for bulk downloading and converting public consultation feedback from the EU Better Regulation Portal.

## Features

- Downloads all feedback metadata including submitter information, organizations, dates, and feedback text
- Downloads all PDF, DOCX, and other file attachments
- Converts documents to markdown format using Pandoc (PDF, Word, Excel, PowerPoint, EPUB, HTML, and more)
- Batch conversion of existing attachments
- Handles pagination automatically to retrieve all feedback items
- Organizes downloads by publication ID
- Saves comprehensive JSON metadata for further analysis
- Rate limiting to be respectful to the server

## Quick Start

### Installation

```bash
# Install from source
cd /path/to/lobbyscraper
pip install .

# Or install in development mode
pip install -e .
```

### Basic Usage

```bash
# Download feedback (metadata only)
eu-lobbyscraper-download 14855

# Download with attachments
eu-lobbyscraper-download 14855 --download-attachments

# Download and convert to markdown
eu-lobbyscraper-download 14855 --download-attachments --convert-to-markdown

# Convert a single document
eu-lobbyscraper-convert document.pdf

# Batch convert attachments
eu-lobbyscraper-batch-convert initiative_14855_feedback
```

### Use as Python Package

```python
from eu_lobbyscraper import EUFeedbackDownloader, DocumentConverter

# Download initiative feedback
downloader = EUFeedbackDownloader(
    initiative_id="14855",
    download_attachments=True,
    convert_to_markdown=True
)
downloader.download_all()

# Convert documents
converter = DocumentConverter()
converter.convert_to_markdown("document.pdf", extract_media=True)
```

### Use as Standalone Scripts (Without Installation)

```bash
pip install requests  # Only dependency
python3 download_initiative_feedback.py 14855 --download-attachments
python3 document_converter.py document.pdf
python3 convert_attachments_to_markdown.py initiative_14855_feedback
```

## Requirements

### Basic Requirements
- Python 3.6+
- `requests` library (automatically installed with package)

### Optional: Document Conversion
- **Pandoc**: Universal document converter

```bash
# Ubuntu/Debian
sudo apt-get install pandoc

# macOS
brew install pandoc

# Windows
# Download from: https://pandoc.org/installing.html

# Verify installation
pandoc --version
```

## Command-Line Tools

### eu-lobbyscraper-download

Download initiative feedback and attachments.

```bash
eu-lobbyscraper-download <initiative_id> [OPTIONS]

Options:
  --download-attachments    Download attachment files
  --convert-to-markdown     Convert to markdown (requires Pandoc)
  --extract-media           Extract images and media from documents
  -o, --output-dir DIR      Custom output directory
```

### eu-lobbyscraper-convert

Convert documents to markdown.

```bash
eu-lobbyscraper-convert <input_file> [OPTIONS]

Options:
  -o, --output FILE        Output markdown path
  --extract-media          Extract images/media to folder
  --batch DIR              Batch convert directory
  -v, --verbose            Verbose output
  --version                Show Pandoc version
```

### eu-lobbyscraper-batch-convert

Batch convert attachments in downloaded initiatives.

```bash
eu-lobbyscraper-batch-convert <initiative_dir> [OPTIONS]

Options:
  -p, --publications IDS   Specific publication IDs to process
  --all                    Process all initiative directories
  --force                  Force reconversion
  --extract-media          Extract images/media
  -v, --verbose            Verbose output
```

## Finding Initiative IDs

Initiative IDs can be found in the URL of any initiative page:

```
https://ec.europa.eu/info/law/better-regulation/have-your-say/initiatives/14855-Simplification-digital-package-and-omnibus_en
                                                                              ^^^^^
```

The initiative ID is `14855`.

## Output Structure

```
initiative_<id>_feedback/
├── initiative_metadata.json          # Initiative details
├── consolidated_feedback.json        # All feedback from all publications
├── publication_<pub_id>/
│   ├── feedback_metadata.json        # Feedback metadata array
│   ├── summary.json                  # Summary statistics
│   └── attachments/
│       ├── feedback_<id>_<filename>       # Downloaded files
│       ├── feedback_<id>_<filename>.md    # Markdown conversions
│       └── feedback_<id>_<filename>_media/ # Extracted media (if --extract-media)
```

## Supported Document Formats

All formats are converted natively by Pandoc:
- **PDF**: `.pdf`
- **Word**: `.docx`, `.doc`, `.odt`, `.rtf`
- **Excel**: `.xlsx`, `.xls`, `.ods`
- **PowerPoint**: `.pptx`, `.ppt`, `.odp`
- **E-books**: `.epub`
- **HTML**: `.html`, `.htm`
- **Text**: `.txt`, `.rst`, `.textile`
- **LaTeX**: `.tex`, `.latex`

## Python API

### EUFeedbackDownloader

```python
from eu_lobbyscraper import EUFeedbackDownloader

downloader = EUFeedbackDownloader(
    initiative_id="14855",
    output_dir="my_output",              # Optional
    download_attachments=True,           # Default: True
    convert_to_markdown=False,           # Default: False
    extract_media=False                  # Default: False
)

# Download everything
downloader.download_all()

# Access downloaded data
# initiative_metadata: downloader.get_initiative_data()
```

### DocumentConverter

```python
from eu_lobbyscraper import DocumentConverter

converter = DocumentConverter(verbose=False)

# Convert single document
converter.convert_to_markdown(
    "document.pdf",
    output_path="output.md",      # Optional
    extract_media=True            # Optional
)

# Check if file can be converted
if converter.can_convert("document.pdf"):
    print("Can convert!")

# Get Pandoc version
version = converter.get_pandoc_version()
```

### AttachmentMarkdownConverter

```python
from eu_lobbyscraper import AttachmentMarkdownConverter

batch = AttachmentMarkdownConverter(
    verbose=True,
    extract_media=True
)

# Convert entire initiative
batch.convert_initiative(
    "initiative_14855_feedback",
    force=False,                  # Force reconversion
    publications=["20401"]        # Specific publications (optional)
)

# Convert single publication
batch.convert_publication("initiative_14855_feedback/publication_20401")
```

## Examples

### Download and Convert Everything

```bash
eu-lobbyscraper-download 14855 \
  --download-attachments \
  --convert-to-markdown \
  --extract-media
```

### Download Now, Convert Later

```bash
# Step 1: Download
eu-lobbyscraper-download 14855 --download-attachments

# Step 2: Convert later
eu-lobbyscraper-batch-convert initiative_14855_feedback --extract-media
```

### Selective Conversion in Python

```python
from eu_lobbyscraper import AttachmentMarkdownConverter
from pathlib import Path
import json

# Load metadata
with open('initiative_14855_feedback/consolidated_feedback.json') as f:
    data = json.load(f)

# Convert only documents from specific organizations
batch = AttachmentMarkdownConverter(verbose=True)
for item in data['feedback']:
    org = item['feedback'].get('organization')
    if org == 'DIGITALEUROPE':
        pub_id = item['publication_id']
        batch.convert_publication(f"initiative_14855_feedback/publication_{pub_id}")
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/eu-lobbyscraper.git
cd eu-lobbyscraper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Build and Distribute

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Upload to PyPI
twine upload dist/*
```

## Troubleshooting

### Command not found after installation

Ensure pip's bin directory is in your PATH:

```bash
# Linux/macOS
export PATH="$HOME/.local/bin:$PATH"

# Or reinstall
pip install --force-reinstall .
```

### Pandoc not found

```bash
# Check if Pandoc is installed
pandoc --version

# If not, install it (see Requirements section above)
```

### Import errors

```bash
# Reinstall package
pip uninstall eu-lobbyscraper
pip install -e .

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
```

## API Endpoints Used

The tool interacts with these EU Better Regulation Portal endpoints:

- `GET /brpapi/groupInitiatives/{id}` - Initiative metadata
- `GET /api/allFeedback?publicationId={pub_id}&page={page}&size={size}` - Feedback (paginated)
- `GET /api/download/{documentId}` - Binary attachment downloads

Base URL: `https://ec.europa.eu/info/law/better-regulation`

## Notes

- The script includes rate limiting (0.3-0.5 second delays) to avoid overwhelming the server
- Attachments are prefixed with `feedback_{id}_` to prevent filename collisions
- Download URLs are added to all metadata, enabling selective post-processing
- Some publications may have no feedback (e.g., planned initiatives)

## License

MIT License - See [LICENSE](LICENSE) file for details.

This is a research tool for downloading public consultation data. All data downloaded belongs to the European Commission and is subject to their terms of use.

## Acknowledgments

This tool was developed through research of the EU Better Regulation Portal API structure, based on analysis of:
- The [eu_consultations](https://github.com/marioangst/eu_consultations) Python package
- Direct API endpoint testing and reverse engineering
- EU Better Regulation Portal public API documentation
