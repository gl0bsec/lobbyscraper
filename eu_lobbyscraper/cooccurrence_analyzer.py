#!/usr/bin/env python3
"""
Co-occurrence Analyzer for Organization Fields of Interest

Creates a co-occurrence table showing which organizations are interested in which fields,
along with relevant metadata and feedback text.

Example usage:
    python cooccurrence_analyzer.py initiative_14855_all_feedback_matched.csv
    python cooccurrence_analyzer.py matched.csv --output cooccurrence.csv
    python cooccurrence_analyzer.py matched.csv --min-occurrences 2
    python cooccurrence_analyzer.py matched.csv --field-filter "Digital economy"
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional


class CooccurrenceAnalyzer:
    """Analyzes co-occurrence of organizations and their fields of interest."""

    def __init__(self, min_occurrences: int = 1, field_filter: Optional[str] = None):
        """
        Initialize analyzer.

        Args:
            min_occurrences: Minimum number of times an org-field pair must occur (default: 1)
            field_filter: Optional substring to filter fields of interest (case-insensitive)
        """
        self.min_occurrences = min_occurrences
        self.field_filter = field_filter.lower() if field_filter else None

        # Track co-occurrences: (org_name, field) -> list of feedback data
        self.cooccurrences = defaultdict(list)

        # Statistics
        self.total_matched = 0
        self.total_with_fields = 0
        self.unique_orgs = set()
        self.unique_fields = set()

    def process_matched_csv(self, filepath: Path) -> None:
        """Process matched CSV and build co-occurrence data."""
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Only process matched organizations
                if row.get('matched?') != 'yes':
                    continue

                self.total_matched += 1

                org_name = row.get('transparency_name', '').strip()
                fields_str = row.get('org_fields_of_interest', '').strip()

                if not org_name or not fields_str:
                    continue

                self.total_with_fields += 1

                # Parse fields (comma-separated)
                fields = [f.strip() for f in fields_str.split(',') if f.strip()]

                # Apply field filter if specified
                if self.field_filter:
                    fields = [f for f in fields if self.field_filter in f.lower()]

                if not fields:
                    continue

                # Track organization
                self.unique_orgs.add(org_name)

                # Build metadata for this feedback
                feedback_data = {
                    'feedback_id': row.get('feedback_id', ''),
                    'organization': row.get('organization', ''),  # Original name from feedback
                    'transparency_name': org_name,
                    'country': row.get('country', ''),
                    'user_type': row.get('user_type', ''),
                    'date': row.get('date', ''),
                    'match_type': row.get('match_type', ''),
                    'match_confidence': row.get('match_confidence', ''),
                    'org_category': row.get('org_category', ''),
                    'org_subcategory': row.get('org_subcategory', ''),
                    'feedback_text': row.get('feedback_text', ''),
                    'feedback_translated': row.get('feedback_translated', ''),
                    'language': row.get('language', ''),
                    'attachment_count': row.get('attachment_count', '0'),
                    'attachment_filenames': row.get('attachment_filenames', ''),
                }

                # Create co-occurrence entries for each field
                for field in fields:
                    self.unique_fields.add(field)
                    self.cooccurrences[(org_name, field)].append(feedback_data)

    def generate_cooccurrence_table(self, output_path: Path) -> None:
        """
        Generate co-occurrence table CSV.

        Each row represents one (organization, field) pair with aggregated feedback metadata.
        """
        headers = [
            'organization_name',
            'field_of_interest',
            'org_category',
            'org_subcategory',
            'countries',
            'user_types',
            'match_types',
            'avg_match_confidence',
            'feedback_dates',
            'total_attachments',
            'feedback_texts',
            'feedback_ids',
            'languages',
        ]

        rows = []

        for (org_name, field), feedbacks in self.cooccurrences.items():
            occurrence_count = len(feedbacks)

            # Filter by minimum occurrences
            if occurrence_count < self.min_occurrences:
                continue

            # Aggregate metadata from all feedbacks
            countries = set()
            user_types = set()
            match_types = set()
            confidences = []
            dates = []
            languages = set()
            feedback_texts = []
            feedback_ids = []
            total_attachments = 0

            # Use first feedback for org-level metadata (should be same across all)
            org_category = feedbacks[0]['org_category']
            org_subcategory = feedbacks[0]['org_subcategory']

            for fb in feedbacks:
                if fb['country']:
                    countries.add(fb['country'])
                if fb['user_type']:
                    user_types.add(fb['user_type'])
                if fb['match_type']:
                    match_types.add(fb['match_type'])
                if fb['match_confidence']:
                    try:
                        confidences.append(float(fb['match_confidence']))
                    except ValueError:
                        pass
                if fb['date']:
                    dates.append(fb['date'])
                if fb['language']:
                    languages.add(fb['language'])
                if fb['feedback_text']:
                    # Truncate long feedback texts and add separator
                    text = fb['feedback_text'][:200].replace('\n', ' ').replace('\r', ' ')
                    if len(fb['feedback_text']) > 200:
                        text += '...'
                    feedback_texts.append(text)
                if fb['feedback_id']:
                    feedback_ids.append(fb['feedback_id'])
                if fb['attachment_count']:
                    try:
                        total_attachments += int(fb['attachment_count'])
                    except ValueError:
                        pass

            # Calculate average confidence
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            row = {
                'organization_name': org_name,
                'field_of_interest': field,
                'org_category': org_category,
                'org_subcategory': org_subcategory,
                'countries': '; '.join(sorted(countries)),
                'user_types': '; '.join(sorted(user_types)),
                'match_types': '; '.join(sorted(match_types)),
                'avg_match_confidence': f'{avg_confidence:.3f}',
                'feedback_dates': '; '.join(dates),
                'total_attachments': total_attachments,
                'feedback_texts': ' | '.join(feedback_texts),
                'feedback_ids': '; '.join(feedback_ids),
                'languages': '; '.join(sorted(languages)),
            }

            rows.append(row)

        # Sort by org name, then by field
        rows.sort(key=lambda x: (x['organization_name'], x['field_of_interest']))

        # Write CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

        return len(rows)

    def print_statistics(self):
        """Print analysis statistics."""
        total_cooccurrences = sum(
            len(feedbacks) for feedbacks in self.cooccurrences.values()
            if len(feedbacks) >= self.min_occurrences
        )
        unique_pairs = sum(
            1 for feedbacks in self.cooccurrences.values()
            if len(feedbacks) >= self.min_occurrences
        )

        print(f"\nCo-occurrence Analysis Statistics:")
        print(f"  Total matched organizations: {self.total_matched}")
        print(f"  With fields of interest: {self.total_with_fields}")
        print(f"  Unique organizations: {len(self.unique_orgs)}")
        print(f"  Unique fields: {len(self.unique_fields)}")
        if self.field_filter:
            print(f"  Field filter applied: '{self.field_filter}'")
        print(f"  Minimum occurrences: {self.min_occurrences}")
        print(f"  Total co-occurrences: {total_cooccurrences}")
        print(f"  Unique (org, field) pairs: {unique_pairs}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze co-occurrence of organizations and fields of interest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic co-occurrence table
  %(prog)s initiative_14855_all_feedback_matched.csv

  # Only include org-field pairs that occur at least 2 times
  %(prog)s matched.csv --min-occurrences 2

  # Filter to specific field of interest
  %(prog)s matched.csv --field-filter "Digital economy"

  # Custom output file
  %(prog)s matched.csv --output my_cooccurrence.csv

  # Combine filters
  %(prog)s matched.csv --min-occurrences 3 --field-filter "AI" --output ai_orgs.csv
        """
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input matched CSV file (from match_organizations.py)"
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output CSV file (default: input_cooccurrence.csv)"
    )

    parser.add_argument(
        "--min-occurrences",
        type=int,
        default=1,
        help="Minimum occurrences for an (org, field) pair to be included (default: 1)"
    )

    parser.add_argument(
        "--field-filter",
        type=str,
        help="Filter to fields containing this substring (case-insensitive)"
    )

    args = parser.parse_args()

    # Validate input file
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    # Determine output path
    if args.output is None:
        args.output = args.input.parent / f"{args.input.stem}_cooccurrence.csv"

    print(f"Input file: {args.input}")
    print(f"Output file: {args.output}")

    # Process
    analyzer = CooccurrenceAnalyzer(
        min_occurrences=args.min_occurrences,
        field_filter=args.field_filter,
    )

    print("\nProcessing matched CSV...")
    analyzer.process_matched_csv(args.input)

    print("Generating co-occurrence table...")
    num_rows = analyzer.generate_cooccurrence_table(args.output)

    analyzer.print_statistics()

    print(f"\n✓ Co-occurrence table saved to: {args.output}")
    print(f"  Total rows: {num_rows}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
