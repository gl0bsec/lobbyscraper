#!/usr/bin/env python3
"""
CLI entry point for list_all_initiatives
"""
import sys
import argparse
import requests
from .lister import EUInitiativeLister


def main():
    parser = argparse.ArgumentParser(
        description='List and download metadata for all initiatives from EU Better Regulation Portal',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all initiatives
  eu-lobbyscraper-list

  # Export to CSV
  eu-lobbyscraper-list --csv initiatives.csv

  # Export to both JSON and CSV
  eu-lobbyscraper-list -o initiatives.json --csv initiatives.csv

  # Download all feedback metadata (WARNING: slow)
  eu-lobbyscraper-list --max 10 --download-feedback

  # Filter by topic
  eu-lobbyscraper-list --topic CLIMA

  # List first 100 initiatives (for testing)
  eu-lobbyscraper-list --max 100

Available topic codes:
  AGRI, ASYL, BUSINESS, CLIMA, COMP, CONSUM, CULT, CUSTOMS, DIGITAL,
  EMPL, ENER, ENLARG, ENV, FINANCE, FOOD, HEALTH, HOME, HUMAN, INST,
  JUST, MARE, MIGR, REGIO, RESEARCH, TAXES, TRADE, TRANS, etc.
        """
    )

    parser.add_argument('-o', '--output', type=str, default='all_initiatives.json',
                       help='Output JSON file (default: all_initiatives.json)')
    parser.add_argument('--csv', type=str, dest='csv_output',
                       help='Output CSV file (optional, e.g., initiatives.csv)')
    parser.add_argument('--download-feedback', action='store_true',
                       help='Download all feedback metadata for each initiative (WARNING: very slow)')
    parser.add_argument('--status', type=str,
                       help='Filter by initiative status (e.g., ACTIVE)')
    parser.add_argument('--topic', type=str,
                       help='Filter by topic code (e.g., CLIMA, TRADE)')
    parser.add_argument('--max', type=int, dest='max_initiatives',
                       help='Maximum number of initiatives to fetch (for testing)')
    parser.add_argument('--no-stats', action='store_true',
                       help='Do not include statistics in output file')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress console output (quiet mode)')
    parser.add_argument('--start-page', type=int, default=0,
                       help='Page number to start from (default: 0)')

    args = parser.parse_args()

    try:
        lister = EUInitiativeLister(
            output_file=args.output,
            verbose=not args.quiet,
            download_feedback=args.download_feedback
        )

        lister.list_all(
            status=args.status,
            topic=args.topic,
            max_initiatives=args.max_initiatives,
            include_stats=not args.no_stats,
            print_stats=not args.quiet,
            csv_output=args.csv_output
        )
        return 0
    except requests.exceptions.HTTPError as e:
        print(f"\n✗ HTTP Error: {e}")
        return 1
    except KeyboardInterrupt:
        print(f"\n\n⚠ Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
