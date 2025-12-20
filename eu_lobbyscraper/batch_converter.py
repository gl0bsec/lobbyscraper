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

    def convert_publication(self, publication_dir: str, force: bool = False):
        """Convert all attachments in a publication directory"""
        pub_path = Path(publication_dir)

        if not pub_path.exists():
            print(f"Publication directory not found: {publication_dir}")
            return

        # Check for attachments subdirectory
        attachments_dir = pub_path / "attachments"
        if not attachments_dir.exists():
            print(f"No attachments directory found in: {publication_dir}")
            return

        self.convert_attachments_directory(str(attachments_dir), force)

    def convert_initiative(self, initiative_dir: str, force: bool = False,
                         publications: List[str] = None):
        """
        Convert all attachments in an initiative directory

        Args:
            initiative_dir: Path to initiative directory
            force: Force reconversion of existing markdown files
            publications: Optional list of specific publication IDs to process
        """
        init_path = Path(initiative_dir)

        if not init_path.exists():
            print(f"Initiative directory not found: {initiative_dir}")
            return

        print(f"\n{'='*70}")
        print(f"Converting Initiative: {init_path.name}")
        print(f"{'='*70}")

        # Find all publication directories
        pub_dirs = [d for d in init_path.iterdir()
                   if d.is_dir() and d.name.startswith('publication_')]

        if not pub_dirs:
            print("No publication directories found")
            return

        # Filter by specific publications if requested
        if publications:
            pub_dirs = [d for d in pub_dirs
                       if any(f"publication_{pub_id}" == d.name for pub_id in publications)]

        print(f"Found {len(pub_dirs)} publication(s) to process\n")

        # Process each publication
        for pub_dir in pub_dirs:
            self.convert_publication(str(pub_dir), force)

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


def find_initiative_directories(base_dir: str = '.') -> List[str]:
    """Find all initiative directories in base directory"""
    base_path = Path(base_dir)
    return [str(d) for d in base_path.iterdir()
            if d.is_dir() and d.name.startswith('initiative_')]


def main():
    parser = argparse.ArgumentParser(
        description='Convert downloaded EU feedback attachments to markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all attachments in an initiative
  python convert_attachments_to_markdown.py initiative_14855_feedback

  # Convert specific publication only
  python convert_attachments_to_markdown.py initiative_14855_feedback -p 20401

  # Convert multiple publications
  python convert_attachments_to_markdown.py initiative_14855_feedback -p 20401 20402

  # Force reconversion of existing markdown files
  python convert_attachments_to_markdown.py initiative_14855_feedback --force

  # Extract images and media from documents
  python convert_attachments_to_markdown.py initiative_14855_feedback --extract-media

  # Process all initiative directories in current folder
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
                       help='Initiative directory (e.g., initiative_14855_feedback)')
    parser.add_argument('-p', '--publications', nargs='+',
                       help='Specific publication IDs to process (default: all)')
    parser.add_argument('--all', action='store_true',
                       help='Process all initiative directories in current folder')
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
