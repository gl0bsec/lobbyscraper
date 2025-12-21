#!/usr/bin/env python3
"""
Command-line interface entry points for EU Lobbyscraper
"""
import sys


def download_cli():
    """Entry point for eu-lobbyscraper-download command"""
    from eu_lobbyscraper.downloader import main
    sys.exit(main())


def convert_cli():
    """Entry point for eu-lobbyscraper-convert command"""
    from eu_lobbyscraper.converter import main
    sys.exit(main())


def batch_convert_cli():
    """Entry point for eu-lobbyscraper-batch-convert command"""
    from eu_lobbyscraper.batch_converter import main
    sys.exit(main())


def list_cli():
    """Entry point for eu-lobbyscraper-list command"""
    from eu_lobbyscraper.lister_cli import main
    sys.exit(main())


if __name__ == "__main__":
    print("Use one of the following commands:")
    print("  eu-lobbyscraper-download        - Download initiative feedback")
    print("  eu-lobbyscraper-convert         - Convert single document")
    print("  eu-lobbyscraper-batch-convert   - Batch convert attachments")
    print("  eu-lobbyscraper-list            - List all initiatives")
