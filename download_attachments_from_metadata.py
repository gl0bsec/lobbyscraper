#!/usr/bin/env python3
"""
Download attachments from previously downloaded metadata files.

This script reads feedback metadata JSON files and downloads attachments
selectively based on various criteria and query filters.
"""
import requests
import json
import os
import sys
from pathlib import Path
import time
import argparse
import re


class AttachmentDownloader:
    """Downloads attachments from metadata files"""

    def __init__(self, metadata_file, output_dir=None, max_files=None, query_filter=None):
        self.metadata_file = metadata_file
        self.max_files = max_files
        self.query_filter = query_filter

        # Determine output directory
        if output_dir:
            self.output_dir = output_dir
        else:
            # Default: create 'attachments' folder in same directory as metadata
            metadata_path = Path(metadata_file)
            self.output_dir = metadata_path.parent / "attachments"

        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        self.downloaded_count = 0
        self.metadata = None  # Store full metadata for query access

    def load_metadata(self):
        """Load metadata from JSON file"""
        print(f"Loading metadata from: {self.metadata_file}")

        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Store full metadata for query access
        self.metadata = data

        # Handle both consolidated and individual publication metadata formats
        if 'feedback' in data and isinstance(data['feedback'], list):
            # Consolidated format (consolidated_feedback.json)
            print(f"✓ Detected consolidated feedback format")
            feedback_items = data['feedback']
        elif isinstance(data, list):
            # Individual publication format (feedback_metadata.json - array of feedback)
            print(f"✓ Detected individual publication feedback format")
            feedback_items = data
        else:
            # Invalid format (probably initiative_metadata.json or other file)
            print("✗ Error: Invalid metadata file")
            print("  This script requires feedback metadata files:")
            print("  - consolidated_feedback.json (created by download_initiative_feedback.py)")
            print("  - publication_*/feedback_metadata.json (individual publication files)")
            print("\n  Note: initiative_metadata.json does NOT contain feedback data")
            return []

        return feedback_items

    def matches_query(self, feedback_item, attachment):
        """Check if feedback item and attachment match the query filter"""
        if not self.query_filter:
            return True

        # Extract feedback data (handle both consolidated and direct format)
        if 'feedback' in feedback_item and isinstance(feedback_item['feedback'], dict):
            feedback = feedback_item['feedback']
            initiative_id = feedback_item.get('initiative_id')
            initiative_title = feedback_item.get('initiative_title')
            publication_id = feedback_item.get('publication_id')
            publication_type = feedback_item.get('publication_type')
        else:
            feedback = feedback_item
            initiative_id = None
            initiative_title = None
            publication_id = feedback.get('publicationId')
            publication_type = None

        # Build context for query evaluation
        context = {
            # Feedback fields
            'organization': feedback.get('organization', ''),
            'country': feedback.get('country', ''),
            'userType': feedback.get('userType', ''),
            'user_type': feedback.get('userType', ''),
            'companySize': feedback.get('companySize', ''),
            'company_size': feedback.get('companySize', ''),
            'language': feedback.get('language', ''),
            'feedback_text': feedback.get('feedback', ''),
            'trNumber': feedback.get('trNumber', ''),
            'tr_number': feedback.get('trNumber', ''),
            # Initiative fields (from consolidated format)
            'initiative_id': initiative_id,
            'initiative_title': initiative_title or '',
            'publication_id': publication_id,
            'publication_type': publication_type or '',
            # Attachment fields
            'fileName': attachment.get('fileName', ''),
            'file_name': attachment.get('fileName', ''),
            'size': attachment.get('size', 0),
            'pages': attachment.get('pages', 0),
            'documentId': attachment.get('documentId', ''),
            # Full objects for complex queries
            'feedback': feedback,
            'attachment': attachment,
            'metadata': self.metadata
        }

        try:
            # Evaluate query as Python expression
            result = eval(self.query_filter, {"__builtins__": {}}, context)
            return bool(result)
        except Exception as e:
            print(f"  ⚠ Query evaluation error: {e}")
            print(f"    Query: {self.query_filter}")
            return False

    def download_attachment(self, attachment, feedback_id):
        """Download a single attachment"""
        url = attachment.get('downloadUrl')
        filename = attachment.get('fileName', 'unknown')

        if not url:
            print(f"  ⚠ No downloadUrl for: {filename}")
            return False

        # Generate safe filename with feedback ID prefix
        safe_filename = f"feedback_{feedback_id}_{filename}"
        filepath = os.path.join(self.output_dir, safe_filename)

        # Skip if already exists
        if os.path.exists(filepath):
            print(f"  ⊙ Already exists: {safe_filename}")
            return True

        try:
            print(f"  Downloading: {filename}")
            response = self.session.get(url, timeout=60)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                f.write(response.content)

            size_mb = len(response.content) / (1024 * 1024)
            print(f"  ✓ Saved: {safe_filename} ({size_mb:.2f} MB)")
            return True

        except Exception as e:
            print(f"  ✗ Failed to download {filename}: {e}")
            return False

    def download_all(self):
        """Download attachments with optional query filter"""
        feedback_items = self.load_metadata()

        if not feedback_items:
            print("No feedback items found in metadata")
            return

        total_attachments = 0
        for item in feedback_items:
            # Handle both consolidated format (with 'feedback' wrapper) and direct format
            if 'feedback' in item and isinstance(item['feedback'], dict):
                feedback = item['feedback']
            else:
                feedback = item

            attachments = feedback.get('attachments', [])
            total_attachments += len(attachments)

        print(f"\nFound {len(feedback_items)} feedback items with {total_attachments} total attachments")

        if self.query_filter:
            print(f"Query filter: {self.query_filter}")

        if self.max_files:
            print(f"Max files limit: {self.max_files}")

        print(f"Output directory: {os.path.abspath(self.output_dir)}\n")

        downloaded = 0
        skipped_by_query = 0
        failed = 0

        for i, item in enumerate(feedback_items, 1):
            # Check if we've reached the max files limit
            if self.max_files and self.downloaded_count >= self.max_files:
                print(f"\n✓ Reached max files limit ({self.max_files}). Stopping.")
                break

            # Handle both formats
            if 'feedback' in item and isinstance(item['feedback'], dict):
                feedback = item['feedback']
            else:
                feedback = item

            feedback_id = feedback.get('id')
            attachments = feedback.get('attachments', [])

            if not attachments:
                continue

            # Track if any attachment from this feedback matches query
            has_matching_attachment = False

            for attachment in attachments:
                # Check max files limit before each download
                if self.max_files and self.downloaded_count >= self.max_files:
                    if has_matching_attachment:
                        print(f"  ⊙ Skipping remaining attachments (max limit reached)")
                    break

                # Apply query filter
                if not self.matches_query(item, attachment):
                    skipped_by_query += 1
                    continue

                # First matching attachment - print feedback header
                if not has_matching_attachment:
                    org = feedback.get('organization', 'Unknown')
                    country = feedback.get('country', 'Unknown')
                    print(f"\n[{i}/{len(feedback_items)}] Feedback ID: {feedback_id}")
                    print(f"  From: {org} ({country})")
                    has_matching_attachment = True

                if self.download_attachment(attachment, feedback_id):
                    downloaded += 1
                    self.downloaded_count += 1
                else:
                    failed += 1

                # Rate limiting
                time.sleep(0.3)

        # Summary
        print(f"\n{'='*70}")
        print(f"Download Summary:")
        print(f"  Successfully downloaded: {downloaded}")
        if failed > 0:
            print(f"  Failed: {failed}")
        if skipped_by_query > 0:
            print(f"  Skipped by query filter: {skipped_by_query}")
        print(f"  Output directory: {os.path.abspath(self.output_dir)}")
        print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Download attachments from feedback metadata JSON files with powerful query filters',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all attachments from consolidated metadata
  python download_attachments_from_metadata.py initiative_14855_feedback/consolidated_feedback.json

  # Download only first 10 attachments
  python download_attachments_from_metadata.py initiative_14855_feedback/consolidated_feedback.json --max-files 10

  # Download PDFs from German organizations
  python download_attachments_from_metadata.py consolidated_feedback.json --query "country == 'DEU' and file_name.endswith('.pdf')"

  # Download large files (>1MB) from business associations
  python download_attachments_from_metadata.py consolidated_feedback.json --query "user_type == 'BUSINESS_ASSOCIATION' and size > 1000000"

  # Download attachments with specific keywords in filename
  python download_attachments_from_metadata.py consolidated_feedback.json --query "'omnibus' in file_name.lower()"

  # Download from CALL_FOR_EVIDENCE publications only
  python download_attachments_from_metadata.py consolidated_feedback.json --query "publication_type == 'CALL_FOR_EVIDENCE'"

  # Combine multiple criteria
  python download_attachments_from_metadata.py consolidated_feedback.json --query "country in ['DEU', 'FRA'] and size > 500000 and pages > 10" --max-files 5

Query Fields Available:
  Feedback: organization, country, userType/user_type, companySize/company_size, language, feedback_text, trNumber/tr_number
  Initiative: initiative_id, initiative_title, publication_id, publication_type
  Attachment: fileName/file_name, size, pages, documentId
  Objects: feedback, attachment, metadata (full objects for complex queries)
        """
    )

    parser.add_argument('metadata_file', type=str,
                        help='Path to feedback metadata JSON file (consolidated or individual publication)')
    parser.add_argument('-o', '--output-dir', type=str,
                        help='Custom output directory for attachments (default: attachments/ in metadata dir)')
    parser.add_argument('--max-files', type=int,
                        help='Maximum number of files to download (default: download all)')
    parser.add_argument('-q', '--query', type=str,
                        help='Python expression to filter attachments (e.g., "country == \'DEU\' and size > 1000000")')

    args = parser.parse_args()

    # Check if metadata file exists
    if not os.path.exists(args.metadata_file):
        print(f"✗ Error: Metadata file not found: {args.metadata_file}")
        sys.exit(1)

    try:
        downloader = AttachmentDownloader(
            args.metadata_file,
            args.output_dir,
            args.max_files,
            args.query
        )
        downloader.download_all()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
