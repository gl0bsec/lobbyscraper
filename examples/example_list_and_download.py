#!/usr/bin/env python3
"""
Example: List initiatives and download feedback for selected ones

This script demonstrates how to:
1. List all initiatives (or filter by topic)
2. Filter initiatives by specific criteria
3. Download feedback for selected initiatives
"""
import json
import subprocess
from pathlib import Path


def load_initiatives(json_file):
    """Load initiatives from JSON file"""
    with open(json_file) as f:
        data = json.load(f)
    return data


def find_initiatives_with_open_feedback(initiatives_data):
    """Find initiatives that are currently accepting feedback"""
    open_feedback = []

    for init in initiatives_data['initiatives']:
        if init.get('feedbackStatus') == 'OPEN':
            open_feedback.append(init)

    return open_feedback


def find_initiatives_by_topic(initiatives_data, topic_code):
    """Find initiatives by topic code"""
    matches = []

    for init in initiatives_data['initiatives']:
        if topic_code in init.get('topicCodes', []):
            matches.append(init)

    return matches


def download_initiative_feedback(initiative_id, download_attachments=False):
    """Download feedback for a specific initiative"""
    cmd = ['python3', 'download_initiative_feedback.py', str(initiative_id)]

    if download_attachments:
        cmd.append('--download-attachments')

    print(f"\nDownloading feedback for initiative {initiative_id}...")
    result = subprocess.run(cmd)

    return result.returncode == 0


def main():
    print("="*70)
    print("EU Better Regulation Portal - List & Download Example")
    print("="*70)

    # Step 1: Check if we have initiatives data
    initiatives_file = 'all_initiatives.json'

    if not Path(initiatives_file).exists():
        print(f"\n{initiatives_file} not found. Downloading...")
        print("This will take a few minutes...\n")

        # Download all initiatives (limited to 200 for this example)
        result = subprocess.run([
            'python3', 'list_all_initiatives.py',
            '--max', '200',
            '-o', initiatives_file
        ])

        if result.returncode != 0:
            print("\n✗ Failed to download initiatives")
            return

    # Step 2: Load and analyze initiatives
    print(f"\nLoading initiatives from {initiatives_file}...")
    data = load_initiatives(initiatives_file)

    print(f"✓ Loaded {data['metadata']['total_initiatives']} initiatives")

    # Step 3: Find initiatives with open feedback
    print("\n" + "="*70)
    print("Finding initiatives with open feedback...")
    print("="*70)

    open_initiatives = find_initiatives_with_open_feedback(data)
    print(f"\nFound {len(open_initiatives)} initiatives currently accepting feedback:")

    # Display first 5
    for i, init in enumerate(open_initiatives[:5], 1):
        init_id = int(init['id'])
        print(f"\n{i}. ID {init_id}: {init['shortTitle'][:80]}")
        print(f"   Topics: {', '.join(init.get('topicCodes', []))}")
        print(f"   Deadline: {init.get('feedbackEndDate', 'N/A')}")
        print(f"   URL: {init.get('initiativeUrl', 'N/A')}")

    # Step 4: Find climate initiatives
    print("\n" + "="*70)
    print("Finding climate-related initiatives...")
    print("="*70)

    climate_initiatives = find_initiatives_by_topic(data, 'CLIMA')
    print(f"\nFound {len(climate_initiatives)} climate initiatives:")

    for i, init in enumerate(climate_initiatives[:5], 1):
        init_id = int(init['id'])
        print(f"\n{i}. ID {init_id}: {init['shortTitle'][:80]}")
        print(f"   Feedback: {init.get('feedbackStatus', 'N/A')}")

    # Step 5: Example - Download feedback for first open climate initiative
    print("\n" + "="*70)
    print("Example: Download feedback for an initiative")
    print("="*70)

    # Find first climate initiative with open feedback
    open_climate = [
        init for init in climate_initiatives
        if init.get('feedbackStatus') == 'OPEN'
    ]

    if open_climate:
        example_init = open_climate[0]
        init_id = int(example_init['id'])

        print(f"\nExample initiative:")
        print(f"  ID: {init_id}")
        print(f"  Title: {example_init['shortTitle']}")
        print(f"  Topics: {', '.join(example_init.get('topicCodes', []))}")

        user_input = input("\nDownload feedback metadata for this initiative? (y/N): ")

        if user_input.lower() == 'y':
            success = download_initiative_feedback(init_id, download_attachments=False)
            if success:
                print(f"\n✓ Successfully downloaded feedback metadata")
                print(f"  Output directory: initiative_{init_id}_feedback/")
            else:
                print("\n✗ Download failed")
        else:
            print("\nSkipped download")
    else:
        print("\nNo climate initiatives with open feedback found in the dataset")

    # Summary
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print(f"\nTotal initiatives: {data['metadata']['total_initiatives']}")
    print(f"With open feedback: {len(open_initiatives)}")
    print(f"Climate-related: {len(climate_initiatives)}")

    print("\n" + "="*70)
    print("Next Steps:")
    print("="*70)
    print("""
1. Explore the initiatives in all_initiatives.json
2. Filter by topic, status, or other criteria
3. Use download_initiative_feedback.py to download specific initiatives
4. Add --download-attachments flag to download files

Example commands:
  # Download with attachments
  python3 download_initiative_feedback.py <ID> --download-attachments

  # Get all climate initiatives (no limit)
  python3 list_all_initiatives.py --topic CLIMA -o climate_full.json

  # Browse the JSON file
  python3 -m json.tool all_initiatives.json | less
    """)


if __name__ == "__main__":
    main()
