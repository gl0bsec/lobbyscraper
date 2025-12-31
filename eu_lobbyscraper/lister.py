"""
EU Better Regulation Portal - Initiative Metadata Lister

Downloads metadata for all initiatives from the EU Better Regulation Portal.
Supports filtering by status, topic, and date ranges.
Exports to JSON and/or CSV formats.
"""
import requests
import json
import os
import csv
from pathlib import Path
import time
from datetime import datetime


class EUInitiativeLister:
    """Lists and downloads metadata for all initiatives from EU Better Regulation Portal"""

    BASE_URL = "https://ec.europa.eu/info/law/better-regulation"

    def __init__(self, output_file="all_initiatives.json", verbose=True, download_feedback=False, count_feedback_only=False):
        self.output_file = output_file
        self.verbose = verbose
        self.download_feedback = download_feedback
        self.count_feedback_only = count_feedback_only
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })

    def log(self, message):
        """Print message if verbose mode is enabled"""
        if self.verbose:
            print(message)

    def get_all_initiatives(self, status=None, topic=None, page_size=100,
                          max_initiatives=None, start_page=0):
        """
        Fetch all initiatives with pagination

        Args:
            status: Filter by initiative status (e.g., 'ACTIVE')
            topic: Filter by topic code (e.g., 'CLIMA', 'TRADE')
            page_size: Number of items per page (max 100)
            max_initiatives: Maximum number of initiatives to fetch (None = all)
            start_page: Page number to start from (default: 0)

        Returns:
            List of initiative metadata dictionaries
        """
        url = f"{self.BASE_URL}/brpapi/searchInitiatives"
        page = start_page
        all_initiatives = []

        self.log(f"\nFetching initiatives from EU Better Regulation Portal...")
        if status:
            self.log(f"  Filter: status={status}")
        if topic:
            self.log(f"  Filter: topic={topic}")

        while True:
            # Build request parameters
            params = {
                'page': page,
                'size': min(page_size, 100)  # API max is 100
            }

            if status:
                params['initiativeStatus'] = status
            if topic:
                params['topic'] = topic

            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.RequestException as e:
                self.log(f"\n✗ Error fetching page {page}: {e}")
                break

            # Extract initiatives from response
            page_data = data.get('initiativeResultDtoPage', {})
            initiatives = page_data.get('content', [])

            if not initiatives:
                self.log(f"\n  No more initiatives found at page {page}")
                break

            all_initiatives.extend(initiatives)

            # Get pagination info
            total_pages = page_data.get('totalPages', 1)
            total_elements = page_data.get('totalElements', 0)
            current_count = len(all_initiatives)

            self.log(f"  Page {page + 1}/{total_pages} - "
                    f"Retrieved {len(initiatives)} items "
                    f"(Total so far: {current_count}/{total_elements})")

            # Check if we've reached the limit
            if max_initiatives and current_count >= max_initiatives:
                self.log(f"\n  Reached maximum limit of {max_initiatives} initiatives")
                all_initiatives = all_initiatives[:max_initiatives]
                break

            # Check if we've reached the last page
            page += 1
            if page >= total_pages:
                self.log(f"\n✓ Reached last page ({total_pages})")
                break

            # Rate limiting
            time.sleep(0.5)

        self.log(f"\n✓ Total initiatives retrieved: {len(all_initiatives)}")
        return all_initiatives

    def get_initiative_details(self, initiative_id):
        """
        Fetch full initiative details including publications

        Args:
            initiative_id: Initiative ID

        Returns:
            Full initiative data dictionary or None on error
        """
        url = f"{self.BASE_URL}/brpapi/groupInitiatives/{int(initiative_id)}"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"    ⚠ Error fetching details for initiative {initiative_id}: {e}")
            return None

    def get_feedback_for_publication(self, publication_id):
        """
        Fetch all feedback for a single publication

        Args:
            publication_id: Publication ID to fetch feedback for

        Returns:
            List of feedback items
        """
        url = f"{self.BASE_URL}/api/allFeedback"
        page = 0
        size = 100
        all_feedback = []

        while True:
            params = {
                'publicationId': publication_id,
                'page': page,
                'size': size
            }

            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                self.log(f"    ⚠ Error fetching feedback for publication {publication_id}: {e}")
                break

            feedbacks = data.get('content', [])
            if not feedbacks:
                break

            all_feedback.extend(feedbacks)

            total_pages = data.get('totalPages', 1)
            page += 1
            if page >= total_pages:
                break

            time.sleep(0.3)  # Rate limiting

        return all_feedback

    def enrich_initiatives(self, initiatives):
        """
        Add computed fields and clean up data

        Args:
            initiatives: List of initiative dictionaries

        Returns:
            Enriched list of initiatives
        """
        self.log(f"\nEnriching initiative metadata...")

        for i, init in enumerate(initiatives, 1):
            # Add initiative URL
            init_id = init.get('id')
            if init_id:
                # Convert to int to remove decimal point
                init_id_int = int(init_id)
                init['initiativeUrl'] = (
                    f"https://ec.europa.eu/info/law/better-regulation/"
                    f"have-your-say/initiatives/{init_id_int}"
                )

            # Extract topic codes for easier filtering
            topics = init.get('topics', [])
            init['topicCodes'] = [t.get('code') for t in topics if t.get('code')]

            # Extract feedback status information
            current_statuses = init.get('currentStatuses', [])
            if current_statuses:
                latest_status = current_statuses[0]
                init['feedbackStatus'] = latest_status.get('receivingFeedbackStatus')
                init['feedbackStartDate'] = latest_status.get('feedbackStartDate')
                init['feedbackEndDate'] = latest_status.get('feedbackEndDate')
                init['currentStage'] = latest_status.get('frontEndStage')

            # Download feedback metadata if requested
            if self.download_feedback or self.count_feedback_only:
                self.log(f"  [{i}/{len(initiatives)}] {'Counting' if self.count_feedback_only else 'Downloading'} feedback for initiative {int(init_id)}...")

                # First get full initiative details to access publications
                full_details = self.get_initiative_details(init_id)

                if full_details:
                    publications = full_details.get('publications', [])
                    total_feedback_count = 0

                    for pub in publications:
                        pub_id = pub.get('id')
                        pub_feedback_count = pub.get('totalFeedback', 0)
                        total_feedback_count += pub_feedback_count

                        if self.count_feedback_only:
                            # Only store the count, not the actual feedback items
                            pub['feedbackItems'] = []
                        elif pub_id and pub_feedback_count > 0:
                            # Download actual feedback items
                            feedback = self.get_feedback_for_publication(pub_id)
                            pub['feedbackItems'] = feedback
                            self.log(f"    Publication {pub_id}: {len(feedback)} feedback items")
                        else:
                            pub['feedbackItems'] = []

                    # Store publications with feedback in the initiative
                    init['publications'] = publications
                    init['totalFeedbackCount'] = total_feedback_count
                    if not self.count_feedback_only:
                        init['totalFeedbackDownloaded'] = sum(len(pub.get('feedbackItems', [])) for pub in publications)
                    if total_feedback_count > 0:
                        self.log(f"    ✓ Total feedback count: {total_feedback_count}")
                else:
                    init['publications'] = []
                    init['totalFeedbackCount'] = 0
                    if not self.count_feedback_only:
                        init['totalFeedbackDownloaded'] = 0

        self.log(f"\n✓ Enriched {len(initiatives)} initiatives")
        return initiatives

    def save_initiatives(self, initiatives, include_stats=True):
        """
        Save initiatives to JSON file

        Args:
            initiatives: List of initiative dictionaries
            include_stats: Whether to include summary statistics
        """
        output = {
            'metadata': {
                'download_date': datetime.now().isoformat(),
                'total_initiatives': len(initiatives),
                'source': 'EU Better Regulation Portal',
                'api_endpoint': f"{self.BASE_URL}/brpapi/searchInitiatives"
            },
            'initiatives': initiatives
        }

        # Add statistics if requested
        if include_stats:
            output['statistics'] = self.generate_statistics(initiatives)

        # Save to file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        self.log(f"\n✓ Saved {len(initiatives)} initiatives to {self.output_file}")
        file_size = os.path.getsize(self.output_file) / (1024 * 1024)  # MB
        self.log(f"  File size: {file_size:.2f} MB")

    def save_initiatives_csv(self, initiatives, csv_file):
        """
        Save initiatives to CSV file

        Args:
            initiatives: List of initiative dictionaries
            csv_file: Path to output CSV file
        """
        # Define CSV columns
        fieldnames = [
            'id',
            'initiativeUrl',
            'shortTitle',
            'reference',
            'initiativeStatus',
            'foreseenActType',
            'topicCodes',
            'topicLabels',
            'feedbackStatus',
            'feedbackStartDate',
            'feedbackEndDate',
            'totalFeedbackCount',
            'currentStage'
        ]

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for init in initiatives:
                # Prepare row data
                row = {
                    'id': int(init.get('id', 0)),
                    'initiativeUrl': init.get('initiativeUrl', ''),
                    'shortTitle': init.get('shortTitle', ''),
                    'reference': init.get('reference', ''),
                    'initiativeStatus': init.get('initiativeStatus', ''),
                    'foreseenActType': init.get('foreseenActType', ''),
                    'topicCodes': ', '.join(init.get('topicCodes', [])),
                    'topicLabels': ', '.join([t.get('label', '') for t in init.get('topics', [])]),
                    'feedbackStatus': init.get('feedbackStatus', ''),
                    'feedbackStartDate': init.get('feedbackStartDate', ''),
                    'feedbackEndDate': init.get('feedbackEndDate', ''),
                    'totalFeedbackCount': init.get('totalFeedbackCount', ''),
                    'currentStage': init.get('currentStage', '')
                }

                writer.writerow(row)

        self.log(f"✓ Saved {len(initiatives)} initiatives to CSV: {csv_file}")
        file_size = os.path.getsize(csv_file) / (1024 * 1024)  # MB
        self.log(f"  CSV file size: {file_size:.2f} MB")

    def generate_statistics(self, initiatives):
        """
        Generate summary statistics from initiatives

        Args:
            initiatives: List of initiative dictionaries

        Returns:
            Dictionary of statistics
        """
        stats = {
            'total_initiatives': len(initiatives),
            'by_status': {},
            'by_topic': {},
            'by_act_type': {},
            'by_feedback_status': {}
        }

        for init in initiatives:
            # Count by status
            status = init.get('initiativeStatus', 'UNKNOWN')
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1

            # Count by topic
            for topic_code in init.get('topicCodes', []):
                stats['by_topic'][topic_code] = stats['by_topic'].get(topic_code, 0) + 1

            # Count by act type
            act_type = init.get('foreseenActType', 'UNKNOWN')
            stats['by_act_type'][act_type] = stats['by_act_type'].get(act_type, 0) + 1

            # Count by feedback status
            fb_status = init.get('feedbackStatus', 'UNKNOWN')
            stats['by_feedback_status'][fb_status] = stats['by_feedback_status'].get(fb_status, 0) + 1

        # Sort dictionaries by count
        stats['by_status'] = dict(sorted(stats['by_status'].items(),
                                        key=lambda x: x[1], reverse=True))
        stats['by_topic'] = dict(sorted(stats['by_topic'].items(),
                                       key=lambda x: x[1], reverse=True))
        stats['by_act_type'] = dict(sorted(stats['by_act_type'].items(),
                                          key=lambda x: x[1], reverse=True))
        stats['by_feedback_status'] = dict(sorted(stats['by_feedback_status'].items(),
                                                  key=lambda x: x[1], reverse=True))

        return stats

    def print_statistics(self, stats):
        """Print statistics in a readable format"""
        print(f"\n{'='*70}")
        print(f"STATISTICS")
        print(f"{'='*70}")
        print(f"\nTotal Initiatives: {stats['total_initiatives']}")

        print(f"\nBy Status:")
        for status, count in stats['by_status'].items():
            print(f"  {status}: {count}")

        print(f"\nBy Topic (top 10):")
        for i, (topic, count) in enumerate(list(stats['by_topic'].items())[:10], 1):
            print(f"  {i}. {topic}: {count}")

        print(f"\nBy Act Type (top 10):")
        for i, (act_type, count) in enumerate(list(stats['by_act_type'].items())[:10], 1):
            print(f"  {i}. {act_type}: {count}")

        print(f"\nBy Feedback Status:")
        for fb_status, count in stats['by_feedback_status'].items():
            print(f"  {fb_status}: {count}")

        print(f"\n{'='*70}\n")

    def list_all(self, status=None, topic=None, max_initiatives=None,
                include_stats=True, print_stats=True, csv_output=None):
        """
        Main method to list all initiatives

        Args:
            status: Filter by status
            topic: Filter by topic
            max_initiatives: Maximum number to fetch
            include_stats: Include statistics in output file
            print_stats: Print statistics to console
            csv_output: Path to CSV output file (optional)
        """
        print(f"\n{'='*70}")
        print(f"EU Better Regulation Portal - Initiative Lister")
        print(f"Output file: {self.output_file}")
        if csv_output:
            print(f"CSV output: {csv_output}")
        if self.download_feedback:
            print(f"Download feedback: Yes (WARNING: This will take significantly longer)")
        print(f"{'='*70}")

        # Fetch all initiatives
        initiatives = self.get_all_initiatives(
            status=status,
            topic=topic,
            max_initiatives=max_initiatives
        )

        if not initiatives:
            print("\n✗ No initiatives found")
            return

        # Enrich with additional fields
        initiatives = self.enrich_initiatives(initiatives)

        # Save to JSON file
        self.save_initiatives(initiatives, include_stats=include_stats)

        # Save to CSV if requested
        if csv_output:
            self.save_initiatives_csv(initiatives, csv_output)

        # Print statistics if requested
        if print_stats and include_stats:
            stats = self.generate_statistics(initiatives)
            self.print_statistics(stats)

        print(f"✓ Complete! All data saved to: {os.path.abspath(self.output_file)}")
        print(f"{'='*70}\n")


