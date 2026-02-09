#!/usr/bin/env python3
"""
LobbyFacts CSV Export Downloader
Demonstrates working method to retrieve organization data from LobbyFacts.eu
"""

import requests
import time
import csv
import sys
from pathlib import Path


class LobbyFactsCSVDownloader:
    """Download CSV exports from LobbyFacts.eu"""

    BASE_URL = "https://www.lobbyfacts.eu/csv_export/{registration_id}"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) LobbyFactsDownloader/1.0'
        })

    def download_csv(self, registration_id: str, output_file: str = None) -> bool:
        """
        Download CSV export for a specific registration ID

        Args:
            registration_id: EU Transparency Register ID (e.g., "03181945560-59")
            output_file: Path to save CSV (optional, auto-generated if not provided)

        Returns:
            True if successful, False otherwise
        """
        if not output_file:
            # Create filename from registration ID
            safe_id = registration_id.replace("-", "_")
            output_file = f"lobbyfacts_{safe_id}.csv"

        url = self.BASE_URL.format(registration_id=registration_id)

        try:
            print(f"Downloading: {url}")
            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                # Save to file
                with open(output_file, 'wb') as f:
                    f.write(response.content)

                # Count rows
                with open(output_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    row_count = sum(1 for row in reader)

                print(f"✓ Success: {output_file} ({row_count} rows)")
                return True
            else:
                print(f"✗ Failed: HTTP {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"✗ Error: {e}")
            return False

    def download_multiple(self, registration_ids: list, output_dir: str = "lobbyfacts_data"):
        """
        Download CSV exports for multiple organizations

        Args:
            registration_ids: List of registration IDs
            output_dir: Directory to save CSV files
        """
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        results = {"success": 0, "failed": 0}

        for reg_id in registration_ids:
            safe_id = reg_id.replace("-", "_")
            output_file = output_path / f"{safe_id}.csv"

            success = self.download_csv(reg_id, str(output_file))

            if success:
                results["success"] += 1
            else:
                results["failed"] += 1

            # Be respectful with rate limiting
            time.sleep(1)

        print(f"\n{'='*60}")
        print(f"Download Summary:")
        print(f"  Successful: {results['success']}")
        print(f"  Failed: {results['failed']}")
        print(f"  Total: {len(registration_ids)}")
        print(f"{'='*60}")

    def preview_csv(self, csv_file: str, num_rows: int = 5):
        """
        Display preview of CSV file

        Args:
            csv_file: Path to CSV file
            num_rows: Number of data rows to display (default: 5)
        """
        print(f"\nPreview of {csv_file}:")
        print("="*80)

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Get column names
            columns = reader.fieldnames
            print(f"Columns ({len(columns)}): {', '.join(columns[:10])}...")
            print()

            # Display first few rows
            for i, row in enumerate(reader):
                if i >= num_rows:
                    break

                print(f"Row {i+1}:")
                for key in ['original_name', 'registration_date', 'main_category',
                           'sub_category', 'total', 'start_date', 'end_date']:
                    if key in row:
                        print(f"  {key}: {row[key]}")
                print()


# Known valid registration IDs for testing
EXAMPLE_ORGANIZATIONS = {
    "Google": "03181945560-59",
    "Meta (Facebook)": "28666427835-74",
    "Microsoft": "0801162959-21",
    "Apple": "588327811384-96",
    "Shell": "05032108616-26",
    "CEFIC": "64879142323-90",
    "Fleishman-Hillard": "56047191389-84",
}


def main():
    """Main demonstration"""
    downloader = LobbyFactsCSVDownloader()

    print("="*80)
    print("LobbyFacts CSV Export Downloader - Valid Examples")
    print("="*80)
    print()

    # Example 1: Download single organization
    print("Example 1: Download Google's lobbying data")
    print("-"*80)
    success = downloader.download_csv(
        EXAMPLE_ORGANIZATIONS["Google"],
        "google_lobbyfacts.csv"
    )

    if success:
        downloader.preview_csv("google_lobbyfacts.csv", num_rows=3)

    print("\n" + "="*80)
    print("Example 2: Download multiple organizations")
    print("-"*80)

    # Select a few organizations to download
    selected_orgs = ["Meta (Facebook)", "Microsoft", "Apple"]
    selected_ids = [EXAMPLE_ORGANIZATIONS[org] for org in selected_orgs]

    downloader.download_multiple(selected_ids, output_dir="lobbyfacts_exports")

    print("\n" + "="*80)
    print("Available Registration IDs for Testing:")
    print("="*80)
    for org_name, reg_id in EXAMPLE_ORGANIZATIONS.items():
        print(f"  {org_name:25} {reg_id}")
        print(f"    URL: https://www.lobbyfacts.eu/csv_export/{reg_id}")

    print("\n" + "="*80)
    print("Usage Examples:")
    print("="*80)
    print()
    print("# Download specific organization:")
    print('python download_lobbyfacts_csv.py')
    print()
    print("# Use in your code:")
    print('from download_lobbyfacts_csv import LobbyFactsCSVDownloader')
    print('downloader = LobbyFactsCSVDownloader()')
    print('downloader.download_csv("03181945560-59", "google.csv")')
    print()


if __name__ == "__main__":
    main()
