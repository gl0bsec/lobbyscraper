# LobbyFacts API Investigation - Final Report

**Date:** January 23, 2026
**Investigation:** Comprehensive API endpoint discovery and data access methods

## Executive Summary

After extensive testing of 168 different API endpoint patterns, **the LobbyFacts programmatic API is currently non-functional**. However, alternative data access methods exist through CSV exports and the official EU Transparency Register.

## Test Results

### API Endpoints Tested

**Test Coverage:**
- 168 total endpoint patterns tested
- 0 successful responses (0% success rate)
- Multiple base URLs tested:
  - `https://api.lobbyfacts.eu` - Connection refused
  - `http://api.lobbyfacts.eu` - Connection refused
  - `https://api2.lobbyfacts.eu` - Server responds but all endpoints return 404

### Endpoint Patterns Attempted

All tested patterns failed across:
- Common REST patterns: `/api/representatives`, `/api/organizations`, `/api/entities`
- Versioned endpoints: `/api/v1/representatives`, `/api/v1/organizations`
- Direct endpoints: `/representatives`, `/organizations`
- Search parameters: `?q=`, `?name=`, `?search=`, `?filter=`, `?query=`
- Pagination: `?page=`, `?limit=`, `?size=`, `?offset=`
- CSV formats: `.csv` extension and `Accept: text/csv` header
- Entity access: `/{id}` patterns with numeric and string IDs

## Root Cause Analysis

### 1. API Service Status

**Finding:** The LobbyFacts API service appears to be **discontinued or offline**.

**Evidence:**
- api.lobbyfacts.eu refuses all connections (port 80 and 443)
- api2.lobbyfacts.eu responds but returns 404 for all documented endpoints
- API documentation URL (http://api.lobbyfacts.eu/docs/api) is inaccessible
- GitHub repository shows project was "REPLACED BY pudo/openinterests.eu"
- OpenInterests.eu project was archived on March 15, 2020

### 2. Project Evolution

The LobbyFacts project has undergone several transitions:

1. **Original LobbyFacts API** (pre-2014) - REST API for lobbying data
2. **OpenInterests.eu** (2014-2020) - Expanded scope, archived in 2020
3. **Current LobbyFacts.eu** (2020-present) - Web interface only, no public API

## Working Alternative: CSV Exports

### ✅ Method: Web-Based CSV Downloads

LobbyFacts.eu provides CSV exports through their search interface:

**Export URL Pattern:**
```
https://www.lobbyfacts.eu/csv_export/{registration_id}
```

**Example:**
```bash
curl -O "https://www.lobbyfacts.eu/csv_export/758108426123-73"
# Response: 200 OK
# Content-Type: application/csv
# Content-Disposition: attachment; filename="lobbyfacts_result.csv"
```

**Capabilities:**
- Search by country
- Filter by organization type
- Date range filtering
- Export results as CSV

**Limitations:**
- Requires knowing registration IDs or using web interface
- No programmatic search API
- Rate limiting unknown
- Bulk access patterns unclear

## Direct Data Source: EU Transparency Register

### Official API Alternative

Since LobbyFacts sources data from the EU Transparency Register, access the source directly:

**EU Transparency Register:**
- Website: https://transparency-register.europa.eu/
- Data Portal: https://data.europa.eu/data/datasets/transparency-register
- Format: XML, CSV downloads available

**Advantages:**
- Official, authoritative source
- Regular updates
- Complete dataset access
- No intermediary processing

## Recommendations

### For Organization Data Retrieval

**Option 1: Use EU Transparency Register Directly** (Recommended)
- Download complete dataset from data.europa.eu
- Most reliable and comprehensive
- Official source with guaranteed accuracy
- Download link: https://data.europa.eu/data/datasets/transparency-register

**Option 2: LobbyFacts CSV Exports**
- Useful for filtered/processed data
- Good for specific organization lookups
- Limited by web interface constraints

**Option 3: Web Scraping LobbyFacts.eu**
- Last resort option
- Requires respecting robots.txt and rate limits
- More maintenance overhead
- Risk of access restrictions

### Do NOT Rely On

❌ LobbyFacts API endpoints (api.lobbyfacts.eu, api2.lobbyfacts.eu)
❌ OpenInterests.eu (archived since 2020)
❌ Undocumented API patterns

## Code Examples

### Working: CSV Export Download

```python
import requests

def download_lobbyfacts_csv(registration_id, output_file):
    """
    Download CSV export for a specific registration ID
    """
    url = f"https://www.lobbyfacts.eu/csv_export/{registration_id}"
    response = requests.get(url)

    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
        return True
    return False

# Example usage
download_lobbyfacts_csv("758108426123-73", "organization_data.csv")
```

### Alternative: EU Transparency Register

```python
import requests

def download_eu_transparency_register():
    """
    Download the complete EU Transparency Register dataset
    Check data.europa.eu for current download URL
    """
    # Note: URL may change, verify at data.europa.eu
    base_url = "https://data.europa.eu/data/datasets/transparency-register"

    # Follow links to get actual data file
    # Format is typically XML or CSV
    pass
```

## Technical Details

### Test Script

The comprehensive test script `test_lobbyfacts_api.py` attempted:
- 3 base URLs (HTTPS/HTTP variations)
- 11 endpoint patterns per base URL
- 5 search parameter combinations per endpoint
- 4 pagination patterns
- CSV format requests with headers and extensions
- Individual entity access with various ID formats

Full test results available in: `lobbyfacts_api_test_results.json`

### Error Patterns Observed

1. **Connection Refused** (api.lobbyfacts.eu)
   ```
   Failed to establish a new connection: [Errno 61] Connection refused
   ```

2. **HTTP 404** (api2.lobbyfacts.eu)
   ```
   Status: 404 - All endpoints
   ```

3. **Invalid JSON** (api2.lobbyfacts.eu root)
   ```
   Status: 200 but returns HTML instead of JSON
   ```

## Conclusion

**The LobbyFacts programmatic API is not accessible via any tested method.** The service has likely been discontinued or significantly changed since its original documentation was published.

**Recommended Action:** Use the official EU Transparency Register as the primary data source, supplemented by LobbyFacts CSV exports for specific filtered queries when needed.

## References

- [GitHub - LobbyFacts (Archived)](https://github.com/pudo-attic/lobbyfacts)
- [GitHub - OpenInterests.eu (Archived)](https://github.com/pudo-attic/openinterests.eu)
- [LobbyFacts.eu How To Guide](https://www.lobbyfacts.eu/how-to)
- [EU Transparency Register](https://transparency-register.europa.eu/)
- [EU Data Portal - Transparency Register Dataset](https://data.europa.eu/data/datasets/transparency-register)
- [Influence Mapping Toolbox - Lobby Facts](https://iilab.github.io/influencemapping-toolbox/projects/lobby-facts.html)

---

**Investigation conducted:** January 23, 2026
**Test script:** `test_lobbyfacts_api.py`
**Results file:** `lobbyfacts_api_test_results.json`
