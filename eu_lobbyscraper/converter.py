#!/usr/bin/env python3
"""
Document to Markdown Converter

Converts PDF and Office documents to markdown format using Pandoc.
Pandoc is a universal document converter that handles many formats natively.
"""
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List
import shutil
import json


class DocumentConverter:
    """Converts various document formats to markdown using Pandoc"""

    # Supported file extensions (Pandoc supports many more, these are the most common)
    SUPPORTED_EXTENSIONS = {
        # Word processing
        '.docx', '.doc', '.odt', '.rtf',
        # PDF
        '.pdf',
        # Spreadsheets
        '.xlsx', '.xls', '.ods',
        # Presentations
        '.pptx', '.ppt', '.odp',
        # E-books
        '.epub',
        # HTML
        '.html', '.htm',
        # Text formats
        '.txt', '.rst', '.textile',
        # LaTeX
        '.tex', '.latex'
    }

    def __init__(self, verbose=False):
        self.verbose = verbose
        self._pandoc_path = None

    def _log(self, message):
        """Print log message if verbose mode enabled"""
        if self.verbose:
            print(message)

    def _find_pandoc(self) -> Optional[str]:
        """Find Pandoc executable"""
        if self._pandoc_path:
            return self._pandoc_path

        # Check if pandoc is in PATH
        pandoc = shutil.which('pandoc')
        if pandoc:
            self._pandoc_path = pandoc
            return pandoc

        return None

    def get_pandoc_version(self) -> Optional[str]:
        """Get Pandoc version"""
        pandoc = self._find_pandoc()
        if not pandoc:
            return None

        try:
            result = subprocess.run(
                [pandoc, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # First line contains version
                return result.stdout.split('\n')[0]
        except Exception:
            pass

        return None

    def can_convert(self, file_path: str) -> bool:
        """Check if file can be converted to markdown"""
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_EXTENSIONS and self._find_pandoc() is not None

    def get_conversion_requirements(self, file_path: str) -> Tuple[bool, str]:
        """
        Check if file can be converted and return requirements message

        Returns:
            (can_convert: bool, message: str)
        """
        ext = Path(file_path).suffix.lower()

        if ext not in self.SUPPORTED_EXTENSIONS:
            return False, f"Unsupported file type: {ext}"

        if self._find_pandoc() is None:
            return False, "Pandoc not installed. Install from https://pandoc.org/installing.html"

        return True, f"Pandoc conversion available for {ext} files"

    def convert_to_markdown(self, input_path: str, output_path: Optional[str] = None,
                          extract_media: bool = False, **kwargs) -> str:
        """
        Convert any supported document to markdown using Pandoc

        Args:
            input_path: Path to input document
            output_path: Optional output path for markdown file
            extract_media: Extract images/media to a folder
            **kwargs: Additional Pandoc options

        Returns:
            Path to generated markdown file
        """
        pandoc = self._find_pandoc()
        if not pandoc:
            raise RuntimeError(
                "Pandoc not found. Install from https://pandoc.org/installing.html\n"
                "Ubuntu/Debian: sudo apt-get install pandoc\n"
                "macOS: brew install pandoc\n"
                "Windows: Download installer from pandoc.org"
            )

        ext = Path(input_path).suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}")

        if output_path is None:
            output_path = str(Path(input_path).with_suffix('.md'))

        self._log(f"Converting to markdown: {input_path}")

        # Build Pandoc command
        cmd = [
            pandoc,
            input_path,
            '-o', output_path,
            '--to', 'gfm',  # GitHub Flavored Markdown
            '--wrap', 'none',  # Don't wrap lines
            '--standalone',  # Include metadata
        ]

        # Extract media if requested
        if extract_media:
            media_dir = Path(output_path).parent / f"{Path(output_path).stem}_media"
            cmd.extend(['--extract-media', str(media_dir)])
            self._log(f"  Extracting media to: {media_dir}")

        # Add PDF-specific options
        if ext == '.pdf':
            # Use pdftotext for better text extraction (if available)
            cmd.extend([
                '--pdf-engine-opt', '-layout',  # Preserve layout
            ])

        # Add custom options from kwargs
        for key, value in kwargs.items():
            if value is True:
                cmd.append(f'--{key}')
            elif value is not False and value is not None:
                cmd.extend([f'--{key}', str(value)])

        # Run Pandoc
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                raise RuntimeError(f"Pandoc conversion failed: {error_msg}")

            # Verify output was created
            if not Path(output_path).exists():
                raise RuntimeError("Output file not created by Pandoc")

            self._log(f"  ✓ Created markdown: {output_path}")

            # Add metadata header
            self._add_metadata_header(input_path, output_path)

            return output_path

        except subprocess.TimeoutExpired:
            raise RuntimeError("Pandoc conversion timed out (>5 minutes)")
        except Exception as e:
            if "Pandoc conversion failed" in str(e):
                raise
            raise RuntimeError(f"Failed to convert document: {e}")

    def _add_metadata_header(self, input_path: str, output_path: str):
        """Add metadata header to markdown file"""
        try:
            # Read the generated markdown
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create metadata header
            input_file = Path(input_path)
            file_size = input_file.stat().st_size
            size_mb = file_size / (1024 * 1024)

            header = [
                f"<!-- Document Metadata -->",
                f"<!-- Source: {input_file.name} -->",
                f"<!-- Format: {input_file.suffix.upper().lstrip('.')} -->",
                f"<!-- Size: {size_mb:.2f} MB -->",
                f"<!-- Converted with: Pandoc -->",
                "",
                "---",
                "",
            ]

            # Prepend header to content
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(header))
                f.write(content)

            self._log(f"  ✓ Added metadata header")

        except Exception as e:
            # Non-fatal error
            self._log(f"  ⚠ Could not add metadata header: {e}")

    def batch_convert(self, input_dir: str, output_dir: Optional[str] = None,
                     pattern: str = '*', recursive: bool = True) -> List[Tuple[str, str, bool]]:
        """
        Batch convert all supported documents in a directory

        Args:
            input_dir: Input directory path
            output_dir: Output directory (defaults to input_dir)
            pattern: File pattern to match (e.g., '*.pdf')
            recursive: Search recursively

        Returns:
            List of (input_path, output_path, success) tuples
        """
        if output_dir is None:
            output_dir = input_dir

        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Find all matching files
        if recursive:
            files = input_path.rglob(pattern)
        else:
            files = input_path.glob(pattern)

        results = []

        for file in files:
            if file.is_file() and file.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                try:
                    # Preserve directory structure
                    rel_path = file.relative_to(input_path)
                    out_file = output_path / rel_path.with_suffix('.md')
                    out_file.parent.mkdir(parents=True, exist_ok=True)

                    # Convert
                    self.convert_to_markdown(str(file), str(out_file))
                    results.append((str(file), str(out_file), True))

                except Exception as e:
                    self._log(f"  ✗ Failed: {file.name}: {e}")
                    results.append((str(file), "", False))

        return results


def main():
    """Command-line interface for document conversion"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Convert documents to markdown using Pandoc',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert PDF to markdown
  python document_converter.py document.pdf

  # Convert Office document to markdown
  python document_converter.py presentation.pptx

  # Specify output path
  python document_converter.py document.pdf -o output.md

  # Extract images and media
  python document_converter.py document.pdf --extract-media

  # Batch convert all PDFs in a directory
  python document_converter.py --batch /path/to/pdfs -o /path/to/output

Supported formats:
  - PDF: .pdf
  - Word: .docx, .doc, .odt, .rtf
  - Excel: .xlsx, .xls, .ods
  - PowerPoint: .pptx, .ppt, .odp
  - E-books: .epub
  - HTML: .html, .htm
  - And many more...

Requirements:
  - Pandoc must be installed: https://pandoc.org/installing.html
  - Ubuntu/Debian: sudo apt-get install pandoc
  - macOS: brew install pandoc
  - Windows: Download from pandoc.org
        """
    )

    parser.add_argument('input_file', nargs='?', help='Input document path')
    parser.add_argument('-o', '--output', help='Output markdown path')
    parser.add_argument('--extract-media', action='store_true',
                       help='Extract images and media to a folder')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('--batch', metavar='DIR',
                       help='Batch convert all supported files in directory')
    parser.add_argument('--pattern', default='*',
                       help='File pattern for batch mode (default: *)')
    parser.add_argument('--version', action='store_true',
                       help='Show Pandoc version and exit')

    args = parser.parse_args()

    # Create converter
    converter = DocumentConverter(verbose=args.verbose)

    # Show version
    if args.version:
        version = converter.get_pandoc_version()
        if version:
            print(version)
        else:
            print("Pandoc not found")
            sys.exit(1)
        sys.exit(0)

    # Batch mode
    if args.batch:
        print(f"Batch converting files in: {args.batch}")
        results = converter.batch_convert(
            args.batch,
            args.output,
            pattern=args.pattern
        )

        success_count = sum(1 for _, _, success in results if success)
        print(f"\n✓ Converted {success_count}/{len(results)} files")
        sys.exit(0)

    # Single file mode
    if not args.input_file:
        parser.error("Either provide input_file or use --batch mode")

    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: File not found: {args.input_file}")
        sys.exit(1)

    # Check requirements
    can_convert, msg = converter.get_conversion_requirements(args.input_file)
    if not can_convert:
        print(f"Error: {msg}")
        sys.exit(1)

    # Convert document
    try:
        output_path = converter.convert_to_markdown(
            args.input_file,
            args.output,
            extract_media=args.extract_media
        )
        print(f"✓ Conversion successful: {output_path}")

    except Exception as e:
        print(f"✗ Conversion failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
