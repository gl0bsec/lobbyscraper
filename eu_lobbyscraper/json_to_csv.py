#!/usr/bin/env python3
"""
JSON to CSV Converter for EU Feedback Data

Converts index.json files (from feedback_data directories) into CSV format.
Creates a row for each downloaded file with full metadata.

Example usage:
    python json_to_csv.py feedback_data/14855/index.json
    python json_to_csv.py index.json --output feedback.csv
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Optional


class FeedbackJSONToCSVConverter:
    """Converts EU feedback index.json to CSV format."""

    def get_csv_headers(self) -> list[str]:
        """Get CSV headers."""
        return [
            "index",
            "filename",
            "original_filename",
            "feedback_id",
            "date",
            "user_type",
            "organization",
            "first_name",
            "surname",
            "country",
            "language",
            "publication_id"
        ]

    def convert_to_rows(self, json_data: dict) -> list[dict]:
        """
        Convert index.json data to CSV rows.

        Args:
            json_data: Parsed JSON data from index.json

        Returns:
            List of dictionaries representing CSV rows
        """
        # Simply extract the files array - it already has the right structure
        return json_data.get("files", [])

    def convert_file(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Convert a JSON file to CSV.

        Args:
            input_path: Path to input JSON file
            output_path: Path to output CSV file (auto-generated if None)

        Returns:
            Path to output CSV file
        """
        # Read JSON
        with open(input_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        # Convert to rows
        rows = self.convert_to_rows(json_data)

        # Determine output path
        if output_path is None:
            output_path = input_path.with_suffix(".csv")

        # Write CSV
        headers = self.get_csv_headers()

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

        return output_path


def get_metadata_summary(json_data: dict) -> dict:
    """Extract summary metadata from index.json."""
    return {
        "initiative_id": json_data.get("initiative_id"),
        "initiative_title": json_data.get("initiative_title"),
        "total_files": json_data.get("total_files", 0),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Convert EU feedback index.json to CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic conversion
  %(prog)s feedback_data/14855/index.json

  # Specify output file
  %(prog)s feedback_data/14855/index.json --output feedback.csv

  # Show metadata summary only
  %(prog)s feedback_data/14855/index.json --info-only
        """
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input index.json file from feedback_data directory"
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output CSV file (default: input filename with .csv extension)"
    )

    parser.add_argument(
        "--info-only",
        action="store_true",
        help="Show metadata summary without converting"
    )

    args = parser.parse_args()

    # Validate input file
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    # Load JSON
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file: {e}", file=sys.stderr)
        return 1

    # Show metadata summary
    metadata = get_metadata_summary(json_data)
    print(f"Input file: {args.input}")
    print(f"Initiative: [{metadata['initiative_id']}] {metadata['initiative_title']}")
    print(f"Total files: {metadata['total_files']}")

    if args.info_only:
        return 0

    # Convert
    print(f"\nConverting to CSV...")

    converter = FeedbackJSONToCSVConverter()

    output_path = converter.convert_file(args.input, args.output)

    # Count rows
    with open(output_path, "r", encoding="utf-8") as f:
        row_count = sum(1 for _ in f) - 1  # Subtract header

    print(f"\n✓ Converted to: {output_path}")
    print(f"  CSV rows: {row_count}")
    print(f"  Headers: {', '.join(converter.get_csv_headers())}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
