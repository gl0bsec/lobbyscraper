#!/usr/bin/env python3
"""
Test script to discover and validate LobbyFacts API endpoints.
Tests various approaches to retrieve organization data.
"""

import requests
import json
import time
from typing import Dict, List, Any

class LobbyFactsAPITester:
    """Tests various API patterns for LobbyFacts"""

    def __init__(self):
        self.base_urls = [
            "https://api.lobbyfacts.eu",
            "https://api2.lobbyfacts.eu",
            "http://api.lobbyfacts.eu",
        ]
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) LobbyFactsAPITester/1.0'
        })
        self.results = []

    def log_result(self, test_name: str, url: str, success: bool, status_code: int = None,
                   data: Any = None, error: str = None):
        """Log test results"""
        result = {
            'test': test_name,
            'url': url,
            'success': success,
            'status_code': status_code,
            'error': error,
            'data_preview': str(data)[:200] if data else None
        }
        self.results.append(result)

        status = "✓" if success else "✗"
        print(f"\n{status} {test_name}")
        print(f"  URL: {url}")
        if status_code:
            print(f"  Status: {status_code}")
        if error:
            print(f"  Error: {error}")
        if data:
            print(f"  Data preview: {str(data)[:200]}...")

    def test_endpoint(self, base_url: str, endpoint: str, params: Dict = None,
                     test_name: str = None) -> bool:
        """Test a specific endpoint"""
        url = f"{base_url}{endpoint}"
        if not test_name:
            test_name = f"GET {endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log_result(test_name, url, True, response.status_code, data)
                    return True
                except json.JSONDecodeError:
                    self.log_result(test_name, url, False, response.status_code,
                                  error="Invalid JSON response")
                    return False
            else:
                self.log_result(test_name, url, False, response.status_code,
                              error=f"HTTP {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            self.log_result(test_name, url, False, error=str(e))
            return False

    def test_common_patterns(self):
        """Test common REST API patterns"""
        print("\n" + "="*70)
        print("TESTING COMMON API PATTERNS")
        print("="*70)

        # Common endpoint patterns to test
        endpoints = [
            "/api/v1/representatives",
            "/api/v1/organizations",
            "/api/v1/entities",
            "/api/representatives",
            "/api/organizations",
            "/api/entities",
            "/representatives",
            "/organizations",
            "/entities",
            "/api",
            "/",
        ]

        for base_url in self.base_urls:
            print(f"\n--- Testing base URL: {base_url} ---")
            for endpoint in endpoints:
                self.test_endpoint(base_url, endpoint)
                time.sleep(0.2)  # Be respectful

    def test_with_search_params(self):
        """Test endpoints with search/filter parameters"""
        print("\n" + "="*70)
        print("TESTING WITH SEARCH PARAMETERS")
        print("="*70)

        test_params = [
            {'q': 'Google'},
            {'name': 'Google'},
            {'search': 'Google'},
            {'filter': 'name:Google'},
            {'query': 'Google'},
        ]

        endpoints = [
            "/api/representatives",
            "/representatives",
            "/api/organizations",
            "/organizations",
        ]

        for base_url in self.base_urls:
            for endpoint in endpoints:
                for params in test_params:
                    param_str = "&".join([f"{k}={v}" for k, v in params.items()])
                    test_name = f"GET {endpoint}?{param_str}"
                    self.test_endpoint(base_url, endpoint, params, test_name)
                    time.sleep(0.2)

    def test_csv_format(self):
        """Test CSV format requests"""
        print("\n" + "="*70)
        print("TESTING CSV FORMAT")
        print("="*70)

        endpoints = [
            "/api/representatives.csv",
            "/representatives.csv",
            "/api/organizations.csv",
        ]

        for base_url in self.base_urls:
            for endpoint in endpoints:
                self.test_endpoint(base_url, endpoint, test_name=f"GET {endpoint} (CSV)")
                time.sleep(0.2)

        # Also test with Accept header
        for base_url in self.base_urls:
            for endpoint in ["/api/representatives", "/representatives"]:
                url = f"{base_url}{endpoint}"
                try:
                    headers = {'Accept': 'text/csv'}
                    response = self.session.get(url, headers=headers, timeout=10)

                    if response.status_code == 200:
                        self.log_result(f"GET {endpoint} (Accept: text/csv)",
                                      url, True, response.status_code,
                                      response.text[:200])
                    else:
                        self.log_result(f"GET {endpoint} (Accept: text/csv)",
                                      url, False, response.status_code)
                except requests.exceptions.RequestException as e:
                    self.log_result(f"GET {endpoint} (Accept: text/csv)",
                                  url, False, error=str(e))
                time.sleep(0.2)

    def test_pagination(self):
        """Test pagination parameters"""
        print("\n" + "="*70)
        print("TESTING PAGINATION")
        print("="*70)

        pagination_patterns = [
            {'page': 1, 'limit': 10},
            {'page': 1, 'size': 10},
            {'offset': 0, 'limit': 10},
            {'skip': 0, 'take': 10},
        ]

        for base_url in self.base_urls:
            for endpoint in ["/api/representatives", "/representatives"]:
                for params in pagination_patterns:
                    param_str = "&".join([f"{k}={v}" for k, v in params.items()])
                    test_name = f"GET {endpoint}?{param_str}"
                    self.test_endpoint(base_url, endpoint, params, test_name)
                    time.sleep(0.2)

    def test_specific_entity(self):
        """Test accessing specific entities by ID"""
        print("\n" + "="*70)
        print("TESTING SPECIFIC ENTITY ACCESS")
        print("="*70)

        # Common ID patterns to test
        test_ids = ["1", "12345", "google"]

        for base_url in self.base_urls:
            for endpoint_base in ["/api/representatives", "/representatives",
                                 "/api/organizations", "/organizations"]:
                for entity_id in test_ids:
                    endpoint = f"{endpoint_base}/{entity_id}"
                    self.test_endpoint(base_url, endpoint)
                    time.sleep(0.2)

    def print_summary(self):
        """Print summary of all tests"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)

        total = len(self.results)
        successful = sum(1 for r in self.results if r['success'])

        print(f"\nTotal tests: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        print(f"Success rate: {(successful/total*100):.1f}%")

        # Show successful endpoints
        if successful > 0:
            print("\n✓ SUCCESSFUL ENDPOINTS:")
            for result in self.results:
                if result['success']:
                    print(f"  - {result['url']}")
                    if result['data_preview']:
                        print(f"    Response: {result['data_preview']}")

    def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "="*70)
        print("LOBBYFACTS API DISCOVERY & TESTING")
        print("="*70)

        self.test_common_patterns()
        self.test_with_search_params()
        self.test_csv_format()
        self.test_pagination()
        self.test_specific_entity()
        self.print_summary()

        # Save results to JSON
        output_file = "lobbyfacts_api_test_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✓ Detailed results saved to: {output_file}")


def main():
    tester = LobbyFactsAPITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
