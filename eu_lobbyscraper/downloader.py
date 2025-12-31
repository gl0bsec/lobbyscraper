#!/usr/bin/env python3
"""
EU Better Regulation Portal - Bulk Feedback & Attachments Downloader

Downloads all feedback metadata and optionally attachments for a given initiative ID.
"""
import requests
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse
import time
import argparse

# Optional document converter import
try:
    from .converter import DocumentConverter
    CONVERTER_AVAILABLE = True
except ImportError:
    try:
        from eu_lobbyscraper.converter import DocumentConverter
        CONVERTER_AVAILABLE = True
    except ImportError:
        CONVERTER_AVAILABLE = False


class EUFeedbackDownloader:
    """Downloads feedback and attachments from EU Better Regulation Portal"""

    BASE_URL = "https://ec.europa.eu/info/law/better-regulation"

    def __init__(self, initiative_id, output_dir=None, download_attachments=True,
                 convert_to_markdown=False, extract_media=False):
        self.initiative_id = initiative_id
        self.output_dir = output_dir or f"feedback_data/{initiative_id}"
        self.download_attachments = download_attachments
        self.convert_to_markdown = convert_to_markdown
        self.extract_media = extract_media
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        self.file_index = []  # Store file metadata for index.json
        self.download_results = []  # Store download results

        # Initialize converter if requested
        self.converter = None
        if self.convert_to_markdown:
            if not CONVERTER_AVAILABLE:
                raise RuntimeError(
                    "Document converter not available. Ensure document_converter.py is in the same directory."
                )
            self.converter = DocumentConverter(verbose=False)

    def get_initiative_data(self):
        """Fetch initiative metadata"""
        url = f"{self.BASE_URL}/brpapi/groupInitiatives/{self.initiative_id}"
        print(f"Fetching initiative {self.initiative_id}...")

        response = self.session.get(url)
        response.raise_for_status()

        data = response.json()

        # Store for later use (will be saved in index.json)
        self.initiative_data = data

        print(f"✓ Retrieved initiative metadata")
        print(f"  Title: {data.get('shortTitle', 'N/A')}")
        print(f"  Reference: {data.get('reference', 'N/A')}")

        return data

    def get_all_feedback(self, publication_id):
        """Fetch all feedback for a publication with pagination"""
        url = f"{self.BASE_URL}/api/allFeedback"
        page = 0
        size = 100
        all_feedback = []

        print(f"\nFetching feedback for publication {publication_id}...")

        while True:
            params = {
                'publicationId': publication_id,
                'page': page,
                'size': size
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # API returns 'content' not '_embedded.feedback'
            feedbacks = data.get('content', [])
            if not feedbacks:
                break

            all_feedback.extend(feedbacks)

            total_pages = data.get('totalPages', 1)
            total_elements = data.get('totalElements', 0)

            print(f"  Page {page + 1}/{total_pages} - Retrieved {len(feedbacks)} items (Total: {total_elements})")

            page += 1
            if page >= total_pages:
                break

            time.sleep(0.5)  # Be nice to the server

        # Add download URLs to attachment metadata
        for feedback in all_feedback:
            if 'attachments' in feedback:
                for attachment in feedback['attachments']:
                    document_id = attachment.get('documentId')
                    if document_id:
                        attachment['downloadUrl'] = f"{self.BASE_URL}/api/download/{document_id}"

        return all_feedback

    def download_attachment(self, attachment, feedback_item, publication_id, file_index):
        """Download a single attachment and optionally convert to markdown"""
        # Construct download URL from documentId
        document_id = attachment.get('documentId')
        if not document_id:
            print(f"    ⚠ No documentId for attachment: {attachment.get('fileName')}")
            return None

        url = f"{self.BASE_URL}/api/download/{document_id}"

        # Extract feedback metadata
        feedback_id = feedback_item.get('id')
        original_filename = attachment.get('fileName', 'unknown')

        # Extract user information for filename
        organization = feedback_item.get('organization')
        first_name = feedback_item.get('firstName', 'Unknown').replace(' ', '_')
        surname = feedback_item.get('surname', 'Unknown').replace(' ', '_')
        language = feedback_item.get('language', 'EN')

        # Determine prefix for filename
        if organization:
            prefix = organization.replace(' ', '_').replace('/', '_').replace('\\', '_')
        else:
            prefix = f"{first_name}_{surname}"

        # Clean prefix
        prefix = prefix.replace('(', '').replace(')', '').replace('"', '').replace("'", '')

        # Generate safe filename: (Prefix)_original_filename_LANG_INDEX.ext
        base_name = Path(original_filename).stem
        extension = Path(original_filename).suffix
        safe_filename = f"({prefix})_{base_name}_{language}_{file_index}{extension}"
        filepath = os.path.join(self.output_dir, safe_filename)

        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                f.write(response.content)

            # Convert to markdown if requested
            if self.convert_to_markdown and self.converter:
                self._convert_attachment_to_markdown(filepath)

            return filepath, safe_filename
        except Exception as e:
            print(f"    ✗ Failed to download {original_filename}: {e}")
            return None, None

    def _convert_attachment_to_markdown(self, filepath):
        """Convert downloaded attachment to markdown if supported"""
        if not self.converter.can_convert(filepath):
            return

        try:
            markdown_path = self.converter.convert_to_markdown(
                filepath,
                extract_media=self.extract_media
            )
            print(f"      ✓ Converted to markdown: {Path(markdown_path).name}")
        except Exception as e:
            print(f"      ⚠ Markdown conversion failed: {e}")

    def process_publication(self, publication, initiative_metadata):
        """Process a single publication - download feedback and attachments"""
        pub_id = publication.get('id')
        pub_type = publication.get('type')
        total_feedback = publication.get('totalFeedback', 0)

        print(f"\n{'='*70}")
        print(f"Publication {pub_id} ({pub_type})")
        print(f"Total feedback: {total_feedback}")
        print(f"{'='*70}")

        if total_feedback == 0:
            print("  No feedback available for this publication")
            return

        # Get all feedback
        all_feedback = self.get_all_feedback(pub_id)

        # Download attachments if enabled
        attachment_count = 0
        if self.download_attachments:
            print(f"\nDownloading attachments...")

            for i, feedback in enumerate(all_feedback, 1):
                feedback_id = feedback.get('id')
                attachments = feedback.get('attachments', [])

                if attachments:
                    print(f"\n  Feedback {i}/{len(all_feedback)} (ID: {feedback_id}): {len(attachments)} attachment(s)")

                    for att in attachments:
                        att_name = att.get('fileName', 'unknown')
                        print(f"    Downloading: {att_name}")

                        filepath, safe_filename = self.download_attachment(att, feedback, pub_id, len(self.file_index) + 1)
                        if filepath:
                            print(f"    ✓ Saved to: {safe_filename}")
                            attachment_count += 1

                            # Add to file index
                            file_entry = {
                                'index': len(self.file_index) + 1,
                                'filename': safe_filename,
                                'original_filename': att.get('fileName'),
                                'feedback_id': feedback_id,
                                'date': feedback.get('dateFeedback'),
                                'user_type': feedback.get('userType'),
                                'organization': feedback.get('organization'),
                                'first_name': feedback.get('firstName'),
                                'surname': feedback.get('surname'),
                                'country': feedback.get('country'),
                                'language': feedback.get('language'),
                                'publication_id': pub_id
                            }
                            self.file_index.append(file_entry)

                            # Add to download results
                            result_entry = {
                                'feedback_id': feedback_id,
                                'document_id': att.get('documentId'),
                                'filename': att.get('fileName'),
                                'path': f"attachments/{self.initiative_id}/{feedback_id}/{att.get('fileName')}",
                                'status': 'success'
                            }
                            self.download_results.append(result_entry)

                    time.sleep(0.3)  # Rate limiting

            print(f"\n✓ Downloaded {attachment_count} attachments for publication {pub_id}")
        else:
            # Count attachments in metadata
            for feedback in all_feedback:
                attachment_count += len(feedback.get('attachments', []))
            print(f"\n  Skipped downloading {attachment_count} attachments (use --download-attachments to enable)")

    def download_all(self):
        """Main method to download everything"""
        print(f"\n{'='*70}")
        print(f"EU Better Regulation Portal - Feedback Downloader")
        print(f"Initiative ID: {self.initiative_id}")
        print(f"Output directory: {self.output_dir}")
        print(f"Download attachments: {'Yes' if self.download_attachments else 'No (metadata only)'}")
        if self.download_attachments and self.convert_to_markdown:
            print(f"Convert to markdown: Yes")
            if self.extract_media:
                print(f"Extract media: Yes")
        print(f"{'='*70}\n")

        # Get initiative data
        initiative_data = self.get_initiative_data()

        # Process each publication
        publications = initiative_data.get('publications', [])
        print(f"\nFound {len(publications)} publication(s)")

        for publication in publications:
            self.process_publication(publication, initiative_data)

        # Create index and results files
        self._create_index_files(initiative_data)

        print(f"\n{'='*70}")
        print(f"✓ Download complete!")
        print(f"All data saved to: {os.path.abspath(self.output_dir)}")
        print(f"{'='*70}\n")

    def _create_index_files(self, initiative_data):
        """Create index.json and download_results.json files"""
        # Create index.json
        index_data = {
            'initiative_id': self.initiative_id,
            'initiative_title': initiative_data.get('shortTitle'),
            'total_files': len(self.file_index),
            'files': self.file_index
        }

        index_file = os.path.join(self.output_dir, "index.json")
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Created index file: {index_file}")
        print(f"  Total files indexed: {len(self.file_index)}")

        # Create download_results.json
        if self.download_attachments and self.download_results:
            from datetime import datetime, timezone
            results_data = {
                'source_file': f"initiative_{self.initiative_id}_all_feedback.json",
                'downloaded_at': datetime.now(timezone.utc).isoformat(),
                'summary': {
                    'successful': len([r for r in self.download_results if r['status'] == 'success']),
                    'skipped': len([r for r in self.download_results if r['status'] == 'skipped']),
                    'failed': len([r for r in self.download_results if r['status'] == 'failed'])
                },
                'results': self.download_results
            }

            results_file = os.path.join(self.output_dir, "download_results.json")
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)

            print(f"✓ Created download results file: {results_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Download feedback and attachments from EU Better Regulation Portal',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download metadata only (no attachments)
  python download_initiative_feedback.py 14855

  # Download metadata and all attachments
  python download_initiative_feedback.py 14855 --download-attachments

  # Download and convert attachments to markdown
  python download_initiative_feedback.py 14855 --download-attachments --convert-to-markdown

  # Convert to markdown and extract images/media
  python download_initiative_feedback.py 14855 --download-attachments --convert-to-markdown --extract-media

  # Specify custom output directory
  python download_initiative_feedback.py 14855 -o my_data --download-attachments

Conversion requirements:
  - Pandoc must be installed: https://pandoc.org/installing.html
  - Ubuntu/Debian: sudo apt-get install pandoc
  - macOS: brew install pandoc
  - Windows: Download from pandoc.org
        """
    )

    parser.add_argument('initiative_id', type=str,
                        help='Initiative ID from the Better Regulation Portal URL')
    parser.add_argument('-o', '--output-dir', type=str,
                        help='Custom output directory (default: feedback_data/<id>)')
    parser.add_argument('--download-attachments', action='store_true',
                        help='Download attachment files (default: metadata only)')
    parser.add_argument('--convert-to-markdown', action='store_true',
                        help='Convert downloaded attachments to markdown (requires --download-attachments)')
    parser.add_argument('--extract-media', action='store_true',
                        help='Extract images and media from documents (requires --convert-to-markdown)')

    args = parser.parse_args()

    # Validate arguments
    if args.convert_to_markdown and not args.download_attachments:
        parser.error("--convert-to-markdown requires --download-attachments")

    if args.extract_media and not args.convert_to_markdown:
        parser.error("--extract-media requires --convert-to-markdown")

    try:
        downloader = EUFeedbackDownloader(
            args.initiative_id,
            args.output_dir,
            args.download_attachments,
            convert_to_markdown=args.convert_to_markdown,
            extract_media=args.extract_media
        )
        downloader.download_all()
    except requests.exceptions.HTTPError as e:
        print(f"\n✗ HTTP Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
