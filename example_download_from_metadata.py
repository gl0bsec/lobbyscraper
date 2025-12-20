#!/usr/bin/env python3
"""
Example: Download specific attachments using the metadata file

This demonstrates how to use the downloadUrl field in the metadata
to selectively download specific attachments without re-running the full scraper.
"""
import json
import requests
from pathlib import Path

# Load the metadata
with open('initiative_14855_feedback/publication_20401/feedback_metadata.json') as f:
    feedbacks = json.load(f)

# Create output directory
output_dir = Path('selected_downloads')
output_dir.mkdir(exist_ok=True)

# Example 1: Download only attachments from a specific organization
print("Downloading attachments from DIGITALEUROPE...")
for feedback in feedbacks:
    if feedback.get('organization') == 'DIGITALEUROPE':
        for attachment in feedback.get('attachments', []):
            url = attachment.get('downloadUrl')
            filename = attachment.get('fileName')

            if url and filename:
                print(f"  Downloading: {filename}")
                response = requests.get(url)

                filepath = output_dir / f"feedback_{feedback['id']}_{filename}"
                filepath.write_bytes(response.content)
                print(f"  ✓ Saved to {filepath}")

# Example 2: Download all PDFs larger than 1MB
print("\nDownloading PDFs larger than 1MB...")
count = 0
for feedback in feedbacks:
    for attachment in feedback.get('attachments', []):
        if attachment.get('fileName', '').endswith('.pdf'):
            size = attachment.get('size', 0)
            if size > 1_000_000:  # 1MB
                url = attachment.get('downloadUrl')
                filename = attachment.get('fileName')

                print(f"  {filename} ({size / 1_000_000:.1f} MB)")
                # Uncomment to actually download:
                # response = requests.get(url)
                # filepath = output_dir / f"feedback_{feedback['id']}_{filename}"
                # filepath.write_bytes(response.content)

                count += 1
                if count >= 5:  # Limit to 5 for demo
                    break
    if count >= 5:
        break

print(f"\n✓ Example complete. The downloadUrl field allows you to:")
print("  - Download specific attachments based on criteria")
print("  - Filter by organization, country, user type, etc.")
print("  - Process attachments without re-scraping the API")
