#!/usr/bin/env python3
"""
Extract text from English documents in feedback_data/14855 and create CSV with metadata.
"""

import json
import os
import csv
from pathlib import Path
from pypdf import PdfReader
from docx import Document


def extract_pdf_text(pdf_path):
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return '\n'.join(text_parts)
    except Exception as e:
        return f"[ERROR: Could not extract text from PDF: {str(e)}]"


def extract_docx_text(docx_path):
    """Extract text from a DOCX file."""
    try:
        doc = Document(docx_path)
        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        return '\n'.join(text_parts)
    except Exception as e:
        return f"[ERROR: Could not extract text from DOCX: {str(e)}]"


def extract_text_from_file(file_path):
    """Extract text based on file extension."""
    file_path = Path(file_path)

    if not file_path.exists():
        return f"[ERROR: File not found: {file_path}]"

    ext = file_path.suffix.lower()

    if ext == '.pdf':
        return extract_pdf_text(file_path)
    elif ext in ['.docx', '.doc']:
        return extract_docx_text(file_path)
    else:
        return f"[ERROR: Unsupported file type: {ext}]"


def main():
    # Paths
    feedback_dir = Path('/Users/geist/Desktop/Projects/lobbyscraper/feedback_data/14855')
    index_path = feedback_dir / 'index.json'
    output_csv = feedback_dir / 'documents_with_text.csv'

    print(f"Loading metadata from {index_path}...")
    with open(index_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Filter for English files only
    all_files = data['files']
    en_files = [f for f in all_files if f['language'] == 'EN']

    print(f"Found {len(en_files)} English documents out of {len(all_files)} total")

    # Prepare CSV output
    csv_columns = [
        'index',
        'filename',
        'original_filename',
        'feedback_id',
        'date',
        'user_type',
        'organization',
        'first_name',
        'surname',
        'country',
        'language',
        'publication_id',
        'document_text'
    ]

    print(f"Extracting text from {len(en_files)} documents...")
    print("This may take a while...")

    rows = []
    success_count = 0
    error_count = 0

    for i, file_meta in enumerate(en_files, 1):
        filename = file_meta['filename']
        file_path = feedback_dir / filename

        # Show progress every 10 files
        if i % 10 == 0 or i == 1:
            print(f"Processing {i}/{len(en_files)}: {filename}")

        # Extract text
        text = extract_text_from_file(file_path)

        if text.startswith("[ERROR:"):
            error_count += 1
        else:
            success_count += 1

        # Create row with metadata and text
        row = {
            'index': file_meta.get('index', ''),
            'filename': file_meta.get('filename', ''),
            'original_filename': file_meta.get('original_filename', ''),
            'feedback_id': file_meta.get('feedback_id', ''),
            'date': file_meta.get('date', ''),
            'user_type': file_meta.get('user_type', ''),
            'organization': file_meta.get('organization', ''),
            'first_name': file_meta.get('first_name', ''),
            'surname': file_meta.get('surname', ''),
            'country': file_meta.get('country', ''),
            'language': file_meta.get('language', ''),
            'publication_id': file_meta.get('publication_id', ''),
            'document_text': text
        }

        rows.append(row)

    # Write to CSV
    print(f"\nWriting results to {output_csv}...")
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✓ Successfully created CSV with {len(rows)} rows")
    print(f"  - Successfully extracted: {success_count}")
    print(f"  - Errors encountered: {error_count}")
    print(f"\nOutput file: {output_csv}")


if __name__ == '__main__':
    main()
