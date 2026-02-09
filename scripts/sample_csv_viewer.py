#!/usr/bin/env python3
"""Display sample rows from the documents_with_text.csv file."""

import csv
import sys

# Increase CSV field size limit
csv.field_size_limit(sys.maxsize)

csv_path = '/Users/geist/Desktop/Projects/lobbyscraper/feedback_data/14855/documents_with_text.csv'

print('=' * 100)
print('SAMPLE ROWS FROM documents_with_text.csv')
print('=' * 100)

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)

    # Get first 3 successful extractions
    count = 0
    for row in reader:
        if row['document_text'].startswith('[ERROR:'):
            continue

        count += 1
        if count > 3:
            break

        print(f'\n--- DOCUMENT {count} ---')
        print(f'Filename: {row["filename"]}')
        print(f'Organization: {row["organization"] or "(Individual)"}')
        print(f'Submitter: {row["first_name"]} {row["surname"]}')
        print(f'Country: {row["country"]}')
        print(f'Date: {row["date"]}')
        print(f'User Type: {row["user_type"]}')
        print(f'Text Length: {len(row["document_text"]):,} characters')
        print(f'\nText Preview (first 500 characters):')
        print('-' * 100)
        print(row["document_text"][:500])
        print('-' * 100)

print('\n' + '=' * 100)
