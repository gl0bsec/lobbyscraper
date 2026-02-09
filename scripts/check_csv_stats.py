#!/usr/bin/env python3
"""Check statistics for the documents_with_text.csv file."""

import csv
import sys

# Increase CSV field size limit
csv.field_size_limit(sys.maxsize)

csv_path = '/Users/geist/Desktop/Projects/lobbyscraper/feedback_data/14855/documents_with_text.csv'

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

successful = [r for r in rows if not r['document_text'].startswith('[ERROR:')]
errors = [r for r in rows if r['document_text'].startswith('[ERROR:')]

print('=' * 70)
print('CSV FILE STATISTICS')
print('=' * 70)
print(f'\nTotal rows: {len(rows)}')
print(f'Successful extractions: {len(successful)} ({len(successful)/len(rows)*100:.1f}%)')
print(f'Failed extractions: {len(errors)} ({len(errors)/len(rows)*100:.1f}%)')

if successful:
    lengths = [len(r['document_text']) for r in successful]
    print(f'\nDocument Text Statistics:')
    print(f'  Average length: {sum(lengths)//len(lengths):,} characters')
    print(f'  Shortest: {min(lengths):,} characters')
    print(f'  Longest: {max(lengths):,} characters')

# Show organization distribution
orgs = {}
for row in successful:
    org = row['organization'] if row['organization'] else '(Individual)'
    orgs[org] = orgs.get(org, 0) + 1

print(f'\nTop 10 Organizations by Document Count:')
sorted_orgs = sorted(orgs.items(), key=lambda x: x[1], reverse=True)[:10]
for i, (org, count) in enumerate(sorted_orgs, 1):
    org_display = org[:50] + '...' if len(org) > 50 else org
    print(f'  {i:2}. {org_display}: {count}')

# Show errors if any
if errors:
    print(f'\n{len(errors)} Files with Extraction Errors:')
    for i, row in enumerate(errors[:10], 1):
        error_msg = row['document_text'][:80]
        print(f'  {i:2}. {row["filename"][:60]}')
        print(f'      {error_msg}')
    if len(errors) > 10:
        print(f'  ... and {len(errors) - 10} more')

print('\n' + '=' * 70)
print(f'CSV file location: {csv_path}')
print('=' * 70)
