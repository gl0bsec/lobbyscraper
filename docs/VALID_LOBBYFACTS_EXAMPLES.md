# Valid LobbyFacts CSV Export Examples

## ✅ Working Method: CSV Exports

The LobbyFacts API endpoints don't work, but **CSV exports via registration IDs work perfectly**.

## URL Pattern

```
https://www.lobbyfacts.eu/csv_export/{registration_id}
```

## Valid Examples

### Major Tech Companies

1. **Google**
   - Registration ID: `03181945560-59`
   - URL: https://www.lobbyfacts.eu/csv_export/03181945560-59
   - Download:
   ```bash
   curl -O "https://www.lobbyfacts.eu/csv_export/03181945560-59"
   ```

2. **Meta (Facebook)**
   - Registration ID: `28666427835-74`
   - URL: https://www.lobbyfacts.eu/csv_export/28666427835-74
   - Download:
   ```bash
   curl -O "https://www.lobbyfacts.eu/csv_export/28666427835-74"
   ```

3. **Microsoft**
   - Registration ID: `0801162959-21`
   - URL: https://www.lobbyfacts.eu/csv_export/0801162959-21
   - Download:
   ```bash
   curl -O "https://www.lobbyfacts.eu/csv_export/0801162959-21"
   ```

4. **Apple**
   - Registration ID: `588327811384-96`
   - URL: https://www.lobbyfacts.eu/csv_export/588327811384-96
   - Download:
   ```bash
   curl -O "https://www.lobbyfacts.eu/csv_export/588327811384-96"
   ```

### Other Major Organizations

5. **Shell Companies**
   - Registration ID: `05032108616-26`
   - URL: https://www.lobbyfacts.eu/csv_export/05032108616-26

6. **CEFIC (European Chemical Industry Council)**
   - Registration ID: `64879142323-90`
   - URL: https://www.lobbyfacts.eu/csv_export/64879142323-90

7. **Fleishman-Hillard** (Lobbying firm)
   - Registration ID: `56047191389-84`
   - URL: https://www.lobbyfacts.eu/csv_export/56047191389-84

## CSV Data Structure

Each CSV contains historical lobbying data with these key fields:

- `identification_code` - EU Transparency Register ID
- `original_name` - Organization name
- `registration_date` - When registered
- `start_date` / `end_date` - Reporting period
- `main_category` / `sub_category` - Organization type
- `total` - Total lobbying costs
- `min` / `max` / `calculated_cost` - Cost estimates
- `goals` - Organization mission/goals
- `networking` - Associated organizations
- `members` / `members_fte` - Staff information
- Contact information (head, legal, EU representatives)
- Address details (Brussels office, headquarters)

**Note:** Each row represents a different reporting period, so one organization may have multiple rows (annual updates).

## Example Output

```csv
identification_code,original_name,state_date,main_category,sub_category,start_date,end_date,calculated_cost
03181945560-59,Google,2012-03-29,II - In-house lobbyists,Companies & groups,2011-01-01,2011-12-01,650000
03181945560-59,Google,2013-03-28,II - In-house lobbyists,Companies & groups,2012-01-01,2012-12-01,1125000
```

## Python Usage

### Quick Download

```python
import requests

def download_lobbyfacts_csv(registration_id):
    url = f"https://www.lobbyfacts.eu/csv_export/{registration_id}"
    response = requests.get(url)

    if response.status_code == 200:
        filename = f"lobbyfacts_{registration_id.replace('-', '_')}.csv"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
        return True
    return False

# Example
download_lobbyfacts_csv("03181945560-59")  # Google
```

### Using the Provided Script

```python
from download_lobbyfacts_csv import LobbyFactsCSVDownloader

downloader = LobbyFactsCSVDownloader()

# Single download
downloader.download_csv("03181945560-59", "google.csv")

# Multiple downloads
org_ids = [
    "03181945560-59",  # Google
    "28666427835-74",  # Meta
    "0801162959-21",   # Microsoft
]
downloader.download_multiple(org_ids, output_dir="lobbying_data")
```

## How to Find Registration IDs

### Method 1: Search on LobbyFacts.eu
1. Go to https://www.lobbyfacts.eu/
2. Search for organization name
3. Click on organization
4. Registration ID is in URL: `https://www.lobbyfacts.eu/datacard/{name}?rid={REGISTRATION_ID}`

### Method 2: Direct Pattern
Registration IDs follow this format:
- Numbers-numbers-numbers (e.g., `03181945560-59`)
- Usually 13-14 digits with 2-digit suffix
- Example: `{11-14 digits}-{2 digits}`

## Tested Results

| Organization | Registration ID | Rows | Status |
|-------------|-----------------|------|--------|
| Google | 03181945560-59 | 45 | ✅ Works |
| Meta | 28666427835-74 | 37 | ✅ Works |
| Microsoft | 0801162959-21 | 28 | ✅ Works |
| Apple | 588327811384-96 | 27 | ✅ Works |
| Shell | 05032108616-26 | - | ✅ Works |
| CEFIC | 64879142323-90 | - | ✅ Works |

## Limitations

1. **Need Registration ID** - Must know or search for the ID first
2. **No Bulk Export** - Must download one organization at a time
3. **No Search API** - Can't programmatically search for organizations
4. **Rate Limiting** - Unknown limits, use respectful delays (1-2 seconds)
5. **Web-Based** - Requires web scraping for discovery of new IDs

## Alternative: EU Transparency Register

For bulk access to all organizations:
- Website: https://transparency-register.europa.eu/
- Data Portal: https://data.europa.eu/data/datasets/transparency-register
- Format: Complete XML/CSV dataset download
- Updates: Regular (official source)

## Summary

✅ **CSV exports work** - Valid method to retrieve organization data
❌ **API endpoints don't work** - All REST API attempts failed
💡 **Best approach** - Use CSV exports for specific orgs, EU Register for bulk data

---

**Files:**
- `download_lobbyfacts_csv.py` - Working Python implementation
- `google_lobbyfacts.csv` - Example: Google's lobbying data (45 reporting periods)
- `meta_lobbyfacts.csv` - Example: Meta's lobbying data
- `microsoft_lobbyfacts.csv` - Example: Microsoft's lobbying data
