#!/usr/bin/env python3
"""
Organization Matcher for EU Feedback Data

Matches organization names from feedback CSV with EU Transparency Register data.
Uses multiple strategies: exact matching, normalization, and fuzzy matching.

Example usage:
    python match_organizations.py initiative_14855_all_feedback.csv "organizations_new-Table 1.csv"
    python match_organizations.py feedback.csv orgs.csv --output matched.csv
    python match_organizations.py feedback.csv orgs.csv --threshold 0.85
"""

import argparse
import csv
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional, Dict, List, Tuple


# ISO 3166-1 alpha-3 to full country name mapping
COUNTRY_MAPPING = {
    'AUT': 'AUSTRIA', 'BEL': 'BELGIUM', 'BGR': 'BULGARIA', 'HRV': 'CROATIA',
    'CYP': 'CYPRUS', 'CZE': 'CZECH REPUBLIC', 'DNK': 'DENMARK', 'EST': 'ESTONIA',
    'FIN': 'FINLAND', 'FRA': 'FRANCE', 'DEU': 'GERMANY', 'GRC': 'GREECE',
    'HUN': 'HUNGARY', 'IRL': 'IRELAND', 'ITA': 'ITALY', 'LVA': 'LATVIA',
    'LTU': 'LITHUANIA', 'LUX': 'LUXEMBOURG', 'MLT': 'MALTA', 'NLD': 'NETHERLANDS',
    'POL': 'POLAND', 'PRT': 'PORTUGAL', 'ROU': 'ROMANIA', 'SVK': 'SLOVAKIA',
    'SVN': 'SLOVENIA', 'ESP': 'SPAIN', 'SWE': 'SWEDEN', 'GBR': 'UNITED KINGDOM',
    'USA': 'UNITED STATES', 'CAN': 'CANADA', 'CHE': 'SWITZERLAND', 'NOR': 'NORWAY',
    'ISL': 'ICELAND', 'JPN': 'JAPAN', 'CHN': 'CHINA', 'AUS': 'AUSTRALIA',
    'IND': 'INDIA', 'BRA': 'BRAZIL', 'MEX': 'MEXICO', 'KOR': 'SOUTH KOREA',
    'SGP': 'SINGAPORE', 'ZAF': 'SOUTH AFRICA', 'TUR': 'TURKEY', 'ISR': 'ISRAEL',
}


def normalize_org_name(name: str) -> str:
    """
    Normalize organization name for better matching.

    Removes legal suffixes, punctuation, and standardizes whitespace.
    """
    if not name:
        return ""

    # Convert to lowercase
    name = name.lower().strip()

    # Fold Unicode to ASCII (strips accents, diacritics) so e.g.
    # "Österreich" == "Osterreich" and "Économie" == "Economie"
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()

    # Remove common legal suffixes (order matters - remove longer patterns first)
    legal_suffixes = [
        # Multi-word suffixes (must come first)
        r'\s+cooperativa\s+sociale$',
        r'\s+societa\s+cooperativa$',
        r'\s+limited\s+liability\s+company$',
        r'\s+limited\s+liability\s+partnership$',
        r'\s+public\s+limited\s+company$',

        # Standard suffixes (with and without periods)
        r'\s+s\.p\.a\.?$',
        r'\s+spa$',           # Italian - unpunctuated
        r'\s+s\.r\.l\.?$',
        r'\s+srl$',           # Italian - unpunctuated
        r'\s+ltd\.?$',
        r'\s+limited$',
        r'\s+inc\.?$',
        r'\s+incorporated$',
        r'\s+corp\.?$',
        r'\s+corporation$',
        r'\s+b\.v\.?$',
        r'\s+bv$',            # Dutch - unpunctuated
        r'\s+n\.v\.?$',
        r'\s+nv$',            # Dutch - unpunctuated
        r'\s+gmbh$',
        r'\s+ag$',
        r'\s+e\.v\.?$',
        r'\s+ev$',            # German - unpunctuated
        r'\s+v\.z\.w\.?$',
        r'\s+vzw$',           # Belgian - unpunctuated
        r'\s+a\.s\.b\.l\.?$',
        r'\s+asbl$',          # Belgian - unpunctuated
        r'\s+s\.a\.?$',
        r'\s+sa$',
        r'\s+plc$',
        r'\s+llc$',
        r'\s+llp$',
        r'\s+oy$',
        r'\s+oyj$',
        r'\s+ry$',            # Finnish registered association
        r'\s+as$',
        r'\s+aps$',
        r'\s+a\.i\.s\.b\.l\.?$',
        r'\s+aisbl$',         # Belgian international non-profit
        r'\s+a\.g\.?$',
        r'\s+se$',            # European company (Societas Europaea)
        r'\s+eeig$',          # European Economic Interest Grouping
    ]

    for suffix in legal_suffixes:
        name = re.sub(suffix, '', name)

    # Remove text in parentheses (often acronyms or extra info)
    # But keep the text before comparing
    name_no_parens = re.sub(r'\([^)]*\)', '', name)

    # Remove punctuation except spaces
    name_no_parens = re.sub(r'[^\w\s]', ' ', name_no_parens)

    # Remove extra whitespace
    name_no_parens = ' '.join(name_no_parens.split())

    return name_no_parens


def similarity_ratio(s1: str, s2: str) -> float:
    """Calculate similarity ratio between two strings using SequenceMatcher."""
    return SequenceMatcher(None, s1, s2).ratio()


class OrganizationMatcher:
    """Matches organization names using multiple strategies."""

    def __init__(self, fuzzy_threshold: float = 0.85):
        """
        Initialize matcher.

        Args:
            fuzzy_threshold: Minimum similarity ratio for fuzzy matching (0.0-1.0)
        """
        self.fuzzy_threshold = fuzzy_threshold

        # Organization lookup structures
        self.orgs_by_exact_name: Dict[str, dict] = {}
        self.orgs_by_normalized_name: Dict[str, dict] = {}
        self.orgs_by_country: Dict[str, List[Tuple[str, str, dict]]] = {}
        self.all_orgs: List[Tuple[str, str, dict]] = []  # global list for cross-country passes

        # Statistics
        self.stats = {
            'exact': 0,
            'normalized': 0,
            'fuzzy': 0,
            'starts_with': 0,
            'cross_country': 0,
            'no_match': 0,
            'no_org_field': 0,
        }

    def load_organizations(self, filepath: Path) -> None:
        """Load organizations from transparency register CSV."""
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                name = row.get('Name', '').strip()
                if not name:
                    continue

                norm_name = normalize_org_name(name)
                country = row.get('Country', '').strip().upper()

                # Store by exact name
                self.orgs_by_exact_name[name] = row

                # Store by normalized name
                if norm_name not in self.orgs_by_normalized_name:
                    self.orgs_by_normalized_name[norm_name] = row

                # Store by country for fuzzy matching
                if country not in self.orgs_by_country:
                    self.orgs_by_country[country] = []
                self.orgs_by_country[country].append((name, norm_name, row))

                # Global list for cross-country passes
                self.all_orgs.append((name, norm_name, row))

        print(f"Loaded {len(self.orgs_by_exact_name)} organizations from transparency register")
        print(f"  Countries: {len(self.orgs_by_country)}")

    def match_organization(
        self,
        org_name: str,
        country_code: str,
    ) -> Tuple[Optional[dict], str, float]:
        """
        Match an organization name to the transparency register.

        Args:
            org_name: Organization name from feedback
            country_code: ISO 3-letter country code

        Returns:
            Tuple of (matched_org_data, match_type, confidence_score)
            - matched_org_data: Dictionary with org info, or None if no match
            - match_type: 'exact', 'normalized', 'fuzzy', or 'no_match'
            - confidence_score: 1.0 for exact/normalized, similarity ratio for fuzzy
        """
        if not org_name:
            return None, 'no_org_field', 0.0

        org_name = org_name.strip()

        # Strategy 1: Exact match
        if org_name in self.orgs_by_exact_name:
            return self.orgs_by_exact_name[org_name], 'exact', 1.0

        # Strategy 2: Normalized match
        norm_name = normalize_org_name(org_name)
        if norm_name in self.orgs_by_normalized_name:
            return self.orgs_by_normalized_name[norm_name], 'normalized', 1.0

        # Strategy 3: Fuzzy match (within same country)
        country_full = COUNTRY_MAPPING.get(country_code, country_code)
        country_orgs = self.orgs_by_country.get(country_full, [])

        best_match = None
        best_score = self.fuzzy_threshold

        for orig_name, org_norm_name, org_data in country_orgs:
            # Compare normalized names
            score = similarity_ratio(norm_name, org_norm_name)

            if score > best_score:
                best_score = score
                best_match = org_data

        if best_match:
            return best_match, 'fuzzy', best_score

        # Strategy 4: Starts-with match (within same country, both directions)
        # Min 4 chars — safe given the trailing-space boundary check.
        if len(norm_name) >= 4:
            for orig_name, org_norm_name, org_data in country_orgs:
                # Forward: register name starts with submission name
                # e.g. "GSMA" → "GSMA Europe", "noyb" → "noyb - European Center for Digital Rights"
                if org_norm_name.startswith(norm_name + ' ') or org_norm_name == norm_name:
                    return org_data, 'starts_with', 0.95
                # Reverse: submission name starts with register name
                # e.g. "Nordic Financial Unions - the Nordic..." → "Nordic Financial Unions"
                # e.g. "Bundesverband der Deutschen Industrie (BDI) / ..." → "Bundesverband der Deutschen Industrie"
                if len(org_norm_name) >= 5 and (
                    norm_name.startswith(org_norm_name + ' ') or norm_name == org_norm_name
                ):
                    return org_data, 'starts_with', 0.95

        # Strategy 5: Cross-country fallback
        # Only try if we have a reasonably specific name (min 5 chars)
        if len(norm_name) >= 5:
            for orig_name, org_norm_name, org_data in self.all_orgs:
                # Skip orgs already scanned in the within-country passes
                org_country = org_data.get('Country', '').strip().upper()
                if org_country == country_full:
                    continue

                # Exact normalized match in different country
                if norm_name == org_norm_name:
                    return org_data, 'cross_country', 0.90

                # Starts-with in either direction, cross-country (min 6 chars)
                if len(norm_name) >= 6 and len(org_norm_name) >= 6:
                    if org_norm_name.startswith(norm_name + ' '):
                        return org_data, 'cross_country', 0.85
                    if norm_name.startswith(org_norm_name + ' '):
                        return org_data, 'cross_country', 0.85

            # Global fuzzy fallback: try all countries when within-country fuzzy failed.
            # Uses a raised threshold (max of user threshold and 0.88) to limit false
            # positives that arise from matching against a much larger candidate pool.
            global_fuzzy_threshold = max(self.fuzzy_threshold, 0.88)
            best_match = None
            best_score = global_fuzzy_threshold

            for orig_name, org_norm_name, org_data in self.all_orgs:
                org_country = org_data.get('Country', '').strip().upper()
                if org_country == country_full:
                    continue  # already covered by within-country fuzzy above
                # Pre-filter: skip if length difference is too large
                if abs(len(org_norm_name) - len(norm_name)) > 25:
                    continue
                score = similarity_ratio(norm_name, org_norm_name)
                if score > best_score:
                    best_score = score
                    best_match = org_data

            if best_match:
                return best_match, 'cross_country', best_score

        return None, 'no_match', 0.0

    def match_feedback_csv(
        self,
        feedback_path: Path,
        output_path: Optional[Path] = None,
        report_unmatched: bool = True,
    ) -> Path:
        """
        Match organizations in feedback CSV and create enriched output.

        Args:
            feedback_path: Path to feedback CSV
            output_path: Path to output CSV (auto-generated if None)
            report_unmatched: If True, print unmatched organizations

        Returns:
            Path to output CSV file
        """
        if output_path is None:
            output_path = feedback_path.parent / f"{feedback_path.stem}_matched.csv"

        # Read feedback CSV and match
        matched_rows = []
        unmatched = []

        with open(feedback_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            feedback_headers = reader.fieldnames

            for row in reader:
                org_name = row.get('organization', '').strip()
                country_code = row.get('country', '').strip()

                # Match organization
                org_data, match_type, score = self.match_organization(org_name, country_code)

                # Update statistics
                if match_type == 'no_org_field':
                    self.stats['no_org_field'] += 1
                else:
                    self.stats[match_type] += 1

                # Enrich row with org data
                enriched_row = row.copy()

                # Determine if matched
                is_matched = 'yes' if org_data else 'no'
                enriched_row['matched?'] = is_matched

                if org_data:
                    enriched_row['match_type'] = match_type
                    enriched_row['match_confidence'] = f"{score:.3f}"
                    enriched_row['transparency_id'] = org_data.get('Id', '')
                    enriched_row['transparency_name'] = org_data.get('Name', '')
                    enriched_row['org_category'] = org_data.get('Cat', '')
                    enriched_row['org_subcategory'] = org_data.get('Cat2', '')
                    enriched_row['org_registration_date'] = org_data.get('RegDate', '')
                    enriched_row['org_people'] = org_data.get('People', '')
                    enriched_row['org_fte'] = org_data.get('FTE', '')
                    enriched_row['org_fields_of_interest'] = org_data.get('FoI', '')
                    enriched_row['org_costs'] = org_data.get('Costs', '')
                    enriched_row['org_meetings'] = org_data.get('Meetings', '')
                else:
                    enriched_row['match_type'] = match_type
                    enriched_row['match_confidence'] = f"{score:.3f}"
                    enriched_row['transparency_id'] = ''
                    enriched_row['transparency_name'] = ''
                    enriched_row['org_category'] = ''
                    enriched_row['org_subcategory'] = ''
                    enriched_row['org_registration_date'] = ''
                    enriched_row['org_people'] = ''
                    enriched_row['org_fte'] = ''
                    enriched_row['org_fields_of_interest'] = ''
                    enriched_row['org_costs'] = ''
                    enriched_row['org_meetings'] = ''

                    if org_name and match_type == 'no_match':
                        unmatched.append((org_name, country_code))

                matched_rows.append(enriched_row)

        # Write output CSV with intuitive column order
        # Dynamically build headers: preserve all input columns + new matching columns
        # New matching columns to add
        new_matching_columns = [
            'matched?',
            'match_type',
            'match_confidence',
            'transparency_id',
            'transparency_name',
            'org_category',
            'org_subcategory',
            'org_registration_date',
            'org_people',
            'org_fte',
            'org_fields_of_interest',
            'org_costs',
            'org_meetings',
        ]

        # Preserve all input columns and add new ones at the beginning
        output_headers = new_matching_columns + [col for col in feedback_headers if col not in new_matching_columns]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=output_headers, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(matched_rows)

        # Print statistics
        total_with_org = sum([
            self.stats['exact'],
            self.stats['normalized'],
            self.stats['fuzzy'],
            self.stats['starts_with'],
            self.stats['cross_country'],
            self.stats['no_match']
        ])
        total_matched = (self.stats['exact'] + self.stats['normalized'] +
                        self.stats['fuzzy'] + self.stats['starts_with'] +
                        self.stats['cross_country'])

        print(f"\nMatching Statistics:")
        print(f"  Total feedback: {len(matched_rows)}")
        print(f"  With organization field: {total_with_org}")
        print(f"  Without organization field: {self.stats['no_org_field']}")
        print(f"\nMatching results:")
        print(f"  Exact matches: {self.stats['exact']} ({self.stats['exact']/total_with_org*100:.1f}%)")
        print(f"  Normalized matches: {self.stats['normalized']} ({self.stats['normalized']/total_with_org*100:.1f}%)")
        print(f"  Fuzzy matches: {self.stats['fuzzy']} ({self.stats['fuzzy']/total_with_org*100:.1f}%)")
        print(f"  Starts-with matches: {self.stats['starts_with']} ({self.stats['starts_with']/total_with_org*100:.1f}%)")
        print(f"  Cross-country matches: {self.stats['cross_country']} ({self.stats['cross_country']/total_with_org*100:.1f}%)")
        print(f"  Total matched: {total_matched} ({total_matched/total_with_org*100:.1f}%)")
        print(f"  Unmatched: {self.stats['no_match']} ({self.stats['no_match']/total_with_org*100:.1f}%)")

        if report_unmatched and unmatched:
            print(f"\nSample unmatched organizations (first 20):")
            for org, country in unmatched[:20]:
                print(f"  [{country}] {org}")

        return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Match organization names from feedback to EU Transparency Register",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic matching
  %(prog)s initiative_14855_all_feedback.csv "organizations_new-Table 1.csv"

  # Specify output file
  %(prog)s feedback.csv orgs.csv --output matched.csv

  # Adjust fuzzy matching threshold
  %(prog)s feedback.csv orgs.csv --threshold 0.90

  # Don't show unmatched organizations
  %(prog)s feedback.csv orgs.csv --no-report-unmatched
        """
    )

    parser.add_argument(
        'feedback_csv',
        type=Path,
        help='Feedback CSV file (from json_to_csv.py)'
    )

    parser.add_argument(
        'organizations_csv',
        type=Path,
        help='EU Transparency Register organizations CSV'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output CSV file (default: <feedback>_matched.csv)'
    )

    parser.add_argument(
        '-t', '--threshold',
        type=float,
        default=0.85,
        help='Fuzzy matching threshold 0.0-1.0 (default: 0.85)'
    )

    parser.add_argument(
        '--no-report-unmatched',
        action='store_true',
        help='Do not print unmatched organizations'
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.feedback_csv.exists():
        print(f"Error: Feedback CSV not found: {args.feedback_csv}", file=sys.stderr)
        return 1

    if not args.organizations_csv.exists():
        print(f"Error: Organizations CSV not found: {args.organizations_csv}", file=sys.stderr)
        return 1

    if not (0.0 <= args.threshold <= 1.0):
        print(f"Error: Threshold must be between 0.0 and 1.0", file=sys.stderr)
        return 1

    # Match organizations
    print(f"Matching organizations...")
    print(f"  Feedback: {args.feedback_csv}")
    print(f"  Organizations: {args.organizations_csv}")
    print(f"  Fuzzy threshold: {args.threshold}")
    print()

    matcher = OrganizationMatcher(fuzzy_threshold=args.threshold)
    matcher.load_organizations(args.organizations_csv)

    output_path = matcher.match_feedback_csv(
        args.feedback_csv,
        args.output,
        report_unmatched=not args.no_report_unmatched,
    )

    print(f"\n✓ Matched CSV saved to: {output_path}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
