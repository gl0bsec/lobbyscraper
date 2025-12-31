#!/usr/bin/env python3
"""
Batch Attachment to Markdown Converter

Converts downloaded attachments to markdown format.
Can process entire initiative folders or specific publications.
"""
import os
import sys
import json
from pathlib import Path
import argparse
from typing import List, Dict, Tuple
try:
    from .converter import DocumentConverter
except ImportError:
    from eu_lobbyscraper.converter import DocumentConverter


class AttachmentMarkdownConverter:
    """Batch converts attachments in initiative folders to markdown"""

    def __init__(self, verbose=False, extract_media=False):
        self.converter = DocumentConverter(verbose=verbose)
        self.verbose = verbose
        self.extract_media = extract_media
        self.stats = {
            'total_files': 0,
            'converted': 0,
            'skipped': 0,
            'failed': 0,
            'unsupported': 0
        }

    def _log(self, message):
        """Print log message if verbose mode enabled"""
        if self.verbose:
            print(message)

    def _should_convert(self, file_path: str, force: bool = False) -> bool:
        """Check if file should be converted"""
        # Check if markdown already exists
        md_path = Path(file_path).with_suffix('.md')
        if md_path.exists() and not force:
            self._log(f"  Skipping (markdown exists): {file_path}")
            return False

        # Check if file is convertible
        if not self.converter.can_convert(file_path):
            return False

        return True

    def convert_file(self, file_path: str, force: bool = False) -> Tuple[bool, str]:
        """
        Convert a single file to markdown

        Returns:
            (success: bool, message: str)
        """
        if not self._should_convert(file_path, force):
            can_convert, msg = self.converter.get_conversion_requirements(file_path)
            if not can_convert:
                return False, f"Unsupported: {msg}"
            return False, "Already converted (use --force to reconvert)"

        try:
            output_path = self.converter.convert_to_markdown(
                file_path,
                extract_media=self.extract_media
            )
            return True, f"✓ {output_path}"
        except Exception as e:
            return False, f"✗ Error: {e}"

    def convert_attachments_directory(self, attachments_dir: str, force: bool = False):
        """Convert all attachments in a directory"""
        attachments_path = Path(attachments_dir)

        if not attachments_path.exists():
            print(f"Directory not found: {attachments_dir}")
            return

        print(f"\nProcessing: {attachments_dir}")

        # Find all files
        all_files = [f for f in attachments_path.iterdir() if f.is_file()]
        convertible_files = [
            f for f in all_files
            if self.converter.can_convert(str(f))
        ]

        print(f"  Found {len(all_files)} files, {len(convertible_files)} convertible")

        # Convert each file
        for file_path in convertible_files:
            self.stats['total_files'] += 1
            print(f"\n  [{self.stats['total_files']}/{len(convertible_files)}] {file_path.name}")

            success, message = self.convert_file(str(file_path), force)

            if success:
                self.stats['converted'] += 1
                print(f"    {message}")
            elif "Already converted" in message:
                self.stats['skipped'] += 1
                print(f"    ⊘ {message}")
            elif "Unsupported" in message:
                self.stats['unsupported'] += 1
                self._log(f"    {message}")
            else:
                self.stats['failed'] += 1
                print(f"    {message}")

    def convert_initiative(self, initiative_dir: str, force: bool = False,
                         publications: List[str] = None):
        """
        Convert all attachments in an initiative directory (flat structure)

        Args:
            initiative_dir: Path to initiative directory (e.g., feedback_data/14855)
            force: Force reconversion of existing markdown files
            publications: Optional list of specific publication IDs to filter by
        """
        init_path = Path(initiative_dir)

        if not init_path.exists():
            print(f"Initiative directory not found: {initiative_dir}")
            return

        print(f"\n{'='*70}")
        print(f"Converting Initiative: {init_path.name}")
        print(f"{'='*70}")

        # Check for index.json to get file list
        index_file = init_path / "index.json"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)

            # Filter by publications if requested
            files_to_convert = index_data.get('files', [])
            if publications:
                pub_ids = [int(p) for p in publications]
                files_to_convert = [f for f in files_to_convert
                                   if f.get('publication_id') in pub_ids]

            convertible_files = [
                init_path / f['filename']
                for f in files_to_convert
                if self.converter.can_convert(str(init_path / f['filename']))
            ]

            print(f"  Found {len(convertible_files)} convertible files from index\n")
        else:
            # Fallback: scan directory for all files
            print("  No index.json found, scanning directory...\n")
            all_files = [f for f in init_path.iterdir() if f.is_file() and f.suffix not in ['.json']]
            convertible_files = [
                f for f in all_files
                if self.converter.can_convert(str(f))
            ]
            print(f"  Found {len(convertible_files)} convertible files\n")

        # Convert each file
        for file_path in convertible_files:
            self.stats['total_files'] += 1
            print(f"  [{self.stats['total_files']}/{len(convertible_files)}] {file_path.name}")

            success, message = self.convert_file(str(file_path), force)

            if success:
                self.stats['converted'] += 1
                print(f"    {message}")
            elif "Already converted" in message:
                self.stats['skipped'] += 1
                print(f"    ⊘ {message}")
            elif "Unsupported" in message:
                self.stats['unsupported'] += 1
                self._log(f"    {message}")
            else:
                self.stats['failed'] += 1
                print(f"    {message}")

        # Print summary
        self._print_summary()

    def _print_summary(self):
        """Print conversion statistics"""
        print(f"\n{'='*70}")
        print("Conversion Summary")
        print(f"{'='*70}")
        print(f"  Total files processed:  {self.stats['total_files']}")
        print(f"  Successfully converted: {self.stats['converted']}")
        print(f"  Skipped (already done): {self.stats['skipped']}")
        print(f"  Failed:                 {self.stats['failed']}")
        print(f"  Unsupported format:     {self.stats['unsupported']}")
        print(f"{'='*70}\n")


def find_initiative_directories(base_dir: str = 'feedback_data') -> List[str]:
    """Find all initiative directories in base directory"""
    base_path = Path(base_dir)
    if not base_path.exists():
        return []
    return [str(d) for d in base_path.iterdir()
            if d.is_dir() and d.name.isdigit()]


def main():
    parser = argparse.ArgumentParser(
        description='Convert downloaded EU feedback attachments to markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all attachments in an initiative
  python convert_attachments_to_markdown.py feedback_data/14855

  # Convert specific publication only
  python convert_attachments_to_markdown.py feedback_data/14855 -p 21325

  # Convert multiple publications
  python convert_attachments_to_markdown.py feedback_data/14855 -p 21325 21346

  # Force reconversion of existing markdown files
  python convert_attachments_to_markdown.py feedback_data/14855 --force

  # Extract images and media from documents
  python convert_attachments_to_markdown.py feedback_data/14855 --extract-media

  # Process all initiative directories in feedback_data folder
  python convert_attachments_to_markdown.py --all

Requirements:
  - Pandoc must be installed: https://pandoc.org/installing.html
  - Ubuntu/Debian: sudo apt-get install pandoc
  - macOS: brew install pandoc
  - Windows: Download from pandoc.org

Supported formats:
  - PDF: .pdf
  - Word: .docx, .doc, .odt, .rtf
  - Excel: .xlsx, .xls, .ods
  - PowerPoint: .pptx, .ppt, .odp
  - E-books: .epub
  - HTML: .html, .htm
  - And many more...
        """
    )

    parser.add_argument('initiative_dir', nargs='?',
                       help='Initiative directory (e.g., feedback_data/14855)')
    parser.add_argument('-p', '--publications', nargs='+',
                       help='Specific publication IDs to process (default: all)')
    parser.add_argument('--all', action='store_true',
                       help='Process all initiative directories in feedback_data folder')
    parser.add_argument('--force', action='store_true',
                       help='Force reconversion even if markdown exists')
    parser.add_argument('--extract-media', action='store_true',
                       help='Extract images and media from documents')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    # Validate arguments
    if not args.all and not args.initiative_dir:
        parser.error("Either provide initiative_dir or use --all flag")

    # Create converter
    batch_converter = AttachmentMarkdownConverter(
        verbose=args.verbose,
        extract_media=args.extract_media
    )

    # Check requirements
    print("Checking conversion requirements...")
    pandoc_version = batch_converter.converter.get_pandoc_version()

    if pandoc_version:
        print(f"  {pandoc_version}")
    else:
        print("\nError: Pandoc not installed!")
        print("Install Pandoc:")
        print("  Ubuntu/Debian: sudo apt-get install pandoc")
        print("  macOS: brew install pandoc")
        print("  Windows: https://pandoc.org/installing.html")
        sys.exit(1)

    # Process directories
    if args.all:
        # Find and process all initiative directories
        init_dirs = find_initiative_directories()
        if not init_dirs:
            print("No initiative directories found in current folder")
            sys.exit(1)

        print(f"\nFound {len(init_dirs)} initiative directory(ies)")

        for init_dir in init_dirs:
            batch_converter.convert_initiative(
                init_dir,
                force=args.force,
                publications=args.publications
            )
    else:
        # Process single initiative
        batch_converter.convert_initiative(
            args.initiative_dir,
            force=args.force,
            publications=args.publications
        )


if __name__ == '__main__':
    main()
