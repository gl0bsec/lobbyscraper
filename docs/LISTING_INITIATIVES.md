# Listing All Initiatives

The `list_all_initiatives.py` script allows you to fetch metadata for **all** initiatives from the EU Better Regulation Portal, not just a single initiative.

## Quick Start

```bash
# List all initiatives (this will fetch ~3,800+ initiatives)
python3 list_all_initiatives.py

# Test with first 100 initiatives
python3 list_all_initiatives.py --max 100

# Filter by topic
python3 list_all_initiatives.py --topic CLIMA -o climate_initiatives.json

# Export to CSV
python3 list_all_initiatives.py --csv initiatives.csv

# Download ALL feedback metadata for each initiative (WARNING: very slow)
python3 list_all_initiatives.py --max 10 --download-feedback
```

## Features

- **Bulk Metadata Fetching**: Downloads metadata for all initiatives in one run
- **CSV Export**: Export to spreadsheet-friendly CSV format
- **Feedback Download**: Optionally download ALL feedback metadata for each initiative
- **Filtering**: Filter by status, topic, or other criteria
- **Statistics**: Automatically generates summary statistics (by topic, status, act type, etc.)
- **URL Generation**: Adds direct URLs to each initiative for easy access
- **Enriched Data**: Adds computed fields like `topicCodes`, `feedbackStatus`, etc.
- **Progress Tracking**: Real-time progress updates during download
- **Rate Limiting**: Built-in delays to be respectful to the server

## Command-Line Options

```bash
python3 list_all_initiatives.py [OPTIONS]

Options:
  -o, --output FILE       Output JSON file (default: all_initiatives.json)
  --csv FILE             Output CSV file (optional)
  --download-feedback    Download all feedback metadata (WARNING: very slow)
  --status STATUS         Filter by initiative status (e.g., ACTIVE)
  --topic TOPIC          Filter by topic code (e.g., CLIMA, TRADE)
  --max N                Maximum number of initiatives to fetch
  --no-stats             Don't include statistics in output
  --quiet                Suppress console output
  --start-page N         Start from specific page number
  -h, --help             Show help message
```

## Examples

### Get All Initiatives

```bash
# Download all initiatives (takes ~2-3 minutes)
python3 list_all_initiatives.py
```

This creates `all_initiatives.json` with:
- Full metadata for all initiatives
- Statistics breakdown
- Direct URLs for each initiative

### Filter by Topic

```bash
# Climate action initiatives
python3 list_all_initiatives.py --topic CLIMA -o climate_initiatives.json

# Trade initiatives
python3 list_all_initiatives.py --topic TRADE -o trade_initiatives.json

# Financial services initiatives
python3 list_all_initiatives.py --topic FINANCE -o finance_initiatives.json
```

**Available Topic Codes**:
- `AGRI` - Agriculture
- `ASYL` - Asylum
- `BUSINESS` - Business & Entrepreneurship
- `CLIMA` - Climate action
- `COMP` - Competition
- `CONSUM` - Consumer protection
- `CULT` - Culture
- `CUSTOMS` - Customs
- `DIGITAL` - Digital economy and society
- `EMPL` - Employment & social affairs
- `ENER` - Energy
- `ENLARG` - Enlargement
- `ENV` - Environment
- `FINANCE` - Banking & financial services
- `FOOD` - Food safety
- `HEALTH` - Public health
- `HOME` - Home affairs
- `HUMAN` - Humanitarian aid
- `INST` - Institutional affairs
- `JUST` - Justice
- `MARE` - Maritime affairs
- `MIGR` - Migration
- `REGIO` - Regional policy
- `RESEARCH` - Research & innovation
- `TAXES` - Taxation
- `TRADE` - Trade
- `TRANS` - Transport
- And more...

### Export to CSV

```bash
# Export to CSV only
python3 list_all_initiatives.py --csv initiatives.csv

# Export to both JSON and CSV
python3 list_all_initiatives.py -o initiatives.json --csv initiatives.csv

# Filter climate initiatives and export to CSV
python3 list_all_initiatives.py --topic CLIMA --csv climate.csv
```

**CSV columns include:**
- `id`, `initiativeUrl`, `shortTitle`, `reference`
- `initiativeStatus`, `foreseenActType`
- `topicCodes`, `topicLabels`
- `feedbackStatus`, `feedbackStartDate`, `feedbackEndDate`, `currentStage`

### Download Feedback Metadata

```bash
# Download feedback for first 10 initiatives (test)
python3 list_all_initiatives.py --max 10 --download-feedback

# Download feedback for all climate initiatives
python3 list_all_initiatives.py --topic CLIMA --download-feedback -o climate_with_feedback.json

# Combine with CSV export
python3 list_all_initiatives.py --max 5 --download-feedback --csv test.csv
```

**What gets downloaded:**
- All feedback text and metadata for each initiative
- Submitter information (organization, country, user type)
- Feedback dates, language, and status
- Organized by publication within each initiative

**Performance:**
- ~2-5 seconds per initiative with feedback
- 10 initiatives: ~30-60 seconds
- 100 initiatives: ~5-10 minutes
- All ~3,800 initiatives: ~3-6 hours

### Testing and Development

```bash
# Test with first 50 initiatives
python3 list_all_initiatives.py --max 50 -o test.json

# Quiet mode (no output, just save file)
python3 list_all_initiatives.py --quiet

# No statistics in output (smaller file)
python3 list_all_initiatives.py --no-stats
```

## Output Structure

The output JSON file has this structure:

```json
{
  "metadata": {
    "download_date": "2025-12-20T10:30:00",
    "total_initiatives": 3857,
    "source": "EU Better Regulation Portal",
    "api_endpoint": "https://ec.europa.eu/info/law/better-regulation/brpapi/searchInitiatives"
  },
  "statistics": {
    "total_initiatives": 3857,
    "by_status": {
      "ACTIVE": 3857
    },
    "by_topic": {
      "FINANCE": 450,
      "ENER": 320,
      "ENV": 280,
      ...
    },
    "by_act_type": {
      "PROP_REG": 1200,
      "REG_IMPL": 800,
      ...
    },
    "by_feedback_status": {
      "OPEN": 1500,
      "CLOSED": 2357
    }
  },
  "initiatives": [
    {
      "id": 16192,
      "initiativeStatus": "ACTIVE",
      "reference": "Ares(2025)11338719",
      "foreseenActType": "PROP_REG",
      "shortTitle": "EU aluminium sector – trade measure...",
      "topics": [...],
      "initiativeUrl": "https://ec.europa.eu/info/law/better-regulation/have-your-say/initiatives/16192",
      "topicCodes": ["TRADE"],
      "feedbackStatus": "OPEN",
      "feedbackStartDate": "2025/12/19 17:32:00",
      "feedbackEndDate": "2026/01/31 23:59:59",
      "currentStage": "PLANNING_WORKFLOW",
      ...
    },
    ...
  ]
}
```

### Key Fields

Each initiative includes:

- **`id`**: Unique initiative ID (use with `download_initiative_feedback.py`)
- **`initiativeUrl`**: Direct URL to the initiative page
- **`shortTitle`**: Initiative title
- **`reference`**: Official reference number
- **`initiativeStatus`**: Current status (usually `ACTIVE`)
- **`foreseenActType`**: Type of act (e.g., `PROP_REG`, `PROP_DIR`, `REG_IMPL`)
- **`topics`**: Full topic objects with codes and labels
- **`topicCodes`**: Simple array of topic codes for easy filtering
- **`feedbackStatus`**: Whether feedback is `OPEN` or `CLOSED`
- **`feedbackStartDate`**: When feedback period started
- **`feedbackEndDate`**: When feedback period ends
- **`currentStage`**: Current workflow stage

### With Feedback Download

When using `--download-feedback`, each initiative also includes:

- **`publications`**: Array of publication objects with feedback
- **`totalFeedbackDownloaded`**: Total number of feedback items

```json
{
  "id": 16192,
  "shortTitle": "EU aluminium sector...",
  "publications": [
    {
      "id": 21769,
      "type": "OPEN_FOR_FEEDBACK",
      "totalFeedback": 1,
      "feedbackItems": [
        {
          "id": "...",
          "dateFeedback": "2025/12/20 10:30:00",
          "feedback": "Full feedback text here...",
          "organization": "Example Organization",
          "country": "Belgium",
          "userType": "COMPANY",
          "language": "EN",
          "firstName": "...",
          "lastName": "...",
          "status": "PUBLISHED",
          "attachments": [...]
        }
      ]
    }
  ],
  "totalFeedbackDownloaded": 1
}
```

## Use Cases

### 1. Find Initiatives by Topic

```python
import json

# Load all initiatives
with open('all_initiatives.json') as f:
    data = json.load(f)

# Find climate-related initiatives
climate_initiatives = [
    init for init in data['initiatives']
    if 'CLIMA' in init.get('topicCodes', [])
]

print(f"Found {len(climate_initiatives)} climate initiatives")
```

### 2. Find Initiatives with Open Feedback

```python
import json

with open('all_initiatives.json') as f:
    data = json.load(f)

# Find initiatives accepting feedback
open_feedback = [
    init for init in data['initiatives']
    if init.get('feedbackStatus') == 'OPEN'
]

for init in open_feedback[:5]:
    print(f"{init['id']}: {init['shortTitle']}")
    print(f"  Feedback deadline: {init['feedbackEndDate']}")
    print()
```

### 3. Download Feedback for Multiple Initiatives

```bash
# First, get all initiatives
python3 list_all_initiatives.py --topic CLIMA -o climate_initiatives.json

# Then use Python to extract IDs and download each
python3 << 'EOF'
import json
import subprocess

with open('climate_initiatives.json') as f:
    data = json.load(f)

# Download feedback for climate initiatives with open feedback
for init in data['initiatives']:
    if init.get('feedbackStatus') == 'OPEN':
        init_id = int(init['id'])
        print(f"\nDownloading feedback for initiative {init_id}...")
        subprocess.run([
            'python3', 'download_initiative_feedback.py',
            str(init_id),
            '--download-attachments'
        ])
EOF
```

### 4. Analyze Feedback Data

```python
import json
from collections import Counter

# Load initiatives with feedback
with open('initiatives_with_feedback.json') as f:
    data = json.load(f)

# Analyze feedback by organization
organizations = []
for init in data['initiatives']:
    for pub in init.get('publications', []):
        for feedback in pub.get('feedbackItems', []):
            org = feedback.get('organization')
            if org:
                organizations.append(org)

# Most active organizations
org_counts = Counter(organizations)
print("Top 10 Organizations by Feedback Count:")
for org, count in org_counts.most_common(10):
    print(f"  {org}: {count} submissions")

# Analyze by country
countries = []
for init in data['initiatives']:
    for pub in init.get('publications', []):
        for feedback in pub.get('feedbackItems', []):
            country = feedback.get('country')
            if country:
                countries.append(country)

country_counts = Counter(countries)
print("\nTop 10 Countries by Feedback Count:")
for country, count in country_counts.most_common(10):
    print(f"  {country}: {count} submissions")
```

### 5. Generate Summary Report

```python
import json
from datetime import datetime

with open('all_initiatives.json') as f:
    data = json.load(f)

print("EU Better Regulation Portal - Summary Report")
print("=" * 70)
print(f"Total Initiatives: {data['metadata']['total_initiatives']}")
print(f"Download Date: {data['metadata']['download_date']}")
print()

# Show top topics
print("Top 10 Topics:")
for i, (topic, count) in enumerate(list(data['statistics']['by_topic'].items())[:10], 1):
    pct = (count / data['metadata']['total_initiatives']) * 100
    print(f"{i:2}. {topic:15} - {count:4} initiatives ({pct:5.1f}%)")
```

## API Endpoints Used

The script uses these EU Better Regulation Portal endpoints:

### List Initiatives
```
GET https://ec.europa.eu/info/law/better-regulation/brpapi/searchInitiatives
```
**Parameters**:
- `page` - Page number (0-based)
- `size` - Items per page (max 100)
- `initiativeStatus` - Filter by status (optional)
- `topic` - Filter by topic code (optional)

### Get Initiative Details (when using `--download-feedback`)
```
GET https://ec.europa.eu/info/law/better-regulation/brpapi/groupInitiatives/{id}
```

### Get Feedback (when using `--download-feedback`)
```
GET https://ec.europa.eu/info/law/better-regulation/api/allFeedback
```
**Parameters**:
- `publicationId` - Publication ID
- `page` - Page number (0-based)
- `size` - Items per page (max 100)

## Performance

### Metadata Only (default)
- **~3,800 initiatives**: ~2-3 minutes
- **Rate limiting**: 0.5 seconds between page requests
- **File size**: ~20-30 MB JSON for all initiatives with statistics
- **CSV size**: ~1-2 MB for all initiatives

### With Feedback Download (`--download-feedback`)
- **Per initiative**: ~2-5 seconds (depending on number of feedback items)
- **10 initiatives**: ~30-60 seconds
- **100 initiatives**: ~5-10 minutes
- **All ~3,800 initiatives**: ~3-6 hours
- **File size**: Varies greatly (can be 100+ MB with all feedback)
- **Rate limiting**: 0.5s between initiatives, 0.3s between feedback pages

## Combining with Other Tools

### Workflow 1: Find and Download

```bash
# Step 1: List all initiatives
python3 list_all_initiatives.py

# Step 2: Find interesting initiatives (manually or with Python)
# Look through all_initiatives.json

# Step 3: Download specific initiative
python3 download_initiative_feedback.py 14855 --download-attachments
```

### Workflow 2: Bulk Feedback Download (New Approach)

```bash
# Use the built-in feedback download feature
python3 list_all_initiatives.py --topic CLIMA --download-feedback -o climate_with_feedback.json

# This downloads ALL feedback metadata in one run
# Much more efficient than looping through download_initiative_feedback.py
```

### Workflow 3: Topic-Specific with Individual Downloads

```bash
# Get all climate initiatives
python3 list_all_initiatives.py --topic CLIMA -o climate_initiatives.json

# Then download individual initiatives with attachments
python3 << 'EOF'
import json
import subprocess

with open('climate_initiatives.json') as f:
    data = json.load(f)

# Filter for initiatives with open feedback
for init in data['initiatives']:
    if init.get('feedbackStatus') == 'OPEN':
        init_id = int(init['id'])
        print(f"Processing initiative {init_id}: {init['shortTitle']}")

        # Use download_initiative_feedback.py for full download with attachments
        subprocess.run([
            'python3', 'download_initiative_feedback.py',
            str(init_id),
            '--download-attachments'
        ])
EOF
```

### Workflow 4: CSV Export for Analysis

```bash
# Export all initiatives to CSV
python3 list_all_initiatives.py --csv all_initiatives.csv

# Open in Excel/Google Sheets for filtering and analysis
# Filter by topic, feedback status, dates, etc.
# Then download specific initiatives based on your analysis
```

## Troubleshooting

### Script is slow

This is normal. The script:
- Fetches 100 initiatives per page
- Adds 0.5 second delay between requests
- For ~3,800 initiatives = ~40 pages = ~20 seconds minimum

To speed up testing, use `--max`:
```bash
python3 list_all_initiatives.py --max 100
```

### HTTP errors

If you get HTTP errors:
1. Check your internet connection
2. The EU portal may be temporarily down
3. Try again with `--start-page N` to resume from a specific page

### Out of memory

For very large datasets, use `--no-stats` to reduce memory usage:
```bash
python3 list_all_initiatives.py --no-stats
```

## Notes

- The script only fetches **metadata** (not feedback or attachments)
- Use `download_initiative_feedback.py` to get detailed feedback for specific initiatives
- All data is publicly available from the EU Better Regulation Portal
- Respect rate limits - the script includes automatic delays
