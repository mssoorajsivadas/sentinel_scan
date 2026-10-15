from collections import deque
from urllib.parse import urlparse
import time
import requests
from bs4 import BeautifulSoup

from scanner.http.client import HTTPClient
from scanner.discovery.classifier import classify_url
from scanner.discovery.url_utils import normalize_url, same_domain
from scanner.discovery.js_discovery import (
    extract_inline_js_urls,
    discover_urls_from_external_js,
)
from scanner.reporting.json_report import save_json_report
from scanner.reporting.terminal import (
    print_banner,
    print_scan_config,
    print_resource_tree,
    print_scan_summary,
)


class Crawler:
    def __init__(
        self,
        start_url,
        max_depth=2,
        max_pages=100,
        report_path="reports/scan_report.json",
        request_delay=1.0,
    ):
        parsed_url = urlparse(start_url)

        if parsed_url.scheme not in {"http", "https"}:
            raise ValueError("URL must use HTTP or HTTPS.")

        if not parsed_url.netloc:
            raise ValueError("Please provide a valid URL.")

        if max_depth < 0:
            raise ValueError("Maximum depth cannot be negative.")

        if max_pages < 1:
            raise ValueError("Maximum pages must be at least 1.")

        self.start_url = normalize_url(start_url, start_url)
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.report_path = report_path
        self.request_delay = max(0.0, request_delay)

        self.client = HTTPClient()

        self.queue = deque()
        self.visited_urls = set()
        self.discovered_urls = set()

        self.url_categories = {}
        self.url_statuses = {}
        self.redirects = {}

    def add_url(self, url, depth):
        """Normalize a URL and queue it if it belongs to the target domain."""

        normalized_url = normalize_url(self.start_url, url)

        if normalized_url is None:
            return

        if not same_domain(self.start_url, normalized_url):
            return

        if normalized_url in self.visited_urls:
            return

        if normalized_url in self.discovered_urls:
            return

        self.discovered_urls.add(normalized_url)
        self.queue.append((normalized_url, depth))

    def crawl(self):
        """Start crawling and generate the final report."""

        print_banner()

        print_scan_config(
            target_url=self.start_url,
            max_depth=self.max_depth,
            max_pages=self.max_pages,
            report_path=self.report_path,
        )

        # Add the starting URL to the queue.
        self.discovered_urls.add(self.start_url)
        self.queue.append((self.start_url, 0))

        pages_processed = 0

        while self.queue and pages_processed < self.max_pages:
            current_url, depth = self.queue.popleft()

            if current_url in self.visited_urls:
                continue

            self.visited_urls.add(current_url)
            pages_processed += 1

            print(
                f"\n[{pages_processed}/{self.max_pages}] "
                f"Depth {depth}: {current_url}"
            )

            # Wait before sending each request.
            if pages_processed > 1 and self.request_delay > 0:
                time.sleep(self.request_delay)

            # Send the HTTP request.
            try:
                response = self.client.get(current_url)

            except requests.RequestException as error:
                self.url_statuses[current_url] = "ERROR"
                self.url_categories[current_url] = classify_url(current_url)

                print(f"  Request failed: {error}")
                continue

            status = response.status_code
            content_type = response.headers.get("Content-Type", "")

            self.url_statuses[current_url] = status

            self.url_categories[current_url] = classify_url(
                current_url,
                content_type,
                status,
            )

            print(
                f"  [{status}] "
                f"{self.url_categories[current_url]}"
            )

            # Handle redirects without automatically following them.
            if 300 <= status < 400:
                location = response.headers.get("Location")

                if location:
                    redirect_url = normalize_url(
                        current_url,
                        location,
                    )

                    if redirect_url:
                        self.redirects[current_url] = redirect_url

                    if (
                        redirect_url
                        and same_domain(self.start_url, redirect_url)
                    ):
                        self.add_url(redirect_url, depth)

                    else:
                        print(
                            "  Redirect destination is outside "
                            "the target scope."
                        )

                continue

            # Do not process unsuccessful HTTP responses.
            if status >= 400:
                print("  Skipping response with an HTTP error status.")
                continue

            # Only HTML pages can reveal more HTML links.
            if "text/html" not in content_type.lower():
                continue

            # Stop discovering deeper URLs at the configured depth.
            if depth >= self.max_depth:
                print("  Maximum discovery depth reached.")
                continue

            page_url = response.url
            html = response.text

            # -------------------------------------------------
            # 1. Discover URLs from HTML
            # -------------------------------------------------
            html_urls = extract_html_urls(
                page_url,
                html,
                self.start_url,
            )

            # -------------------------------------------------
            # 2. Discover URLs from inline JavaScript
            # -------------------------------------------------
            inline_candidates = extract_inline_js_urls(html)

            # -------------------------------------------------
            # 3. Discover URLs from external JavaScript files
            # -------------------------------------------------
            external_candidates = discover_urls_from_external_js(
                self.client,
                page_url,
                html,
                self.start_url,
            )

            # Combine all discovered candidates.
            all_candidates = set(html_urls)

            for candidate in inline_candidates | external_candidates:
                normalized = normalize_url(page_url, candidate)

                if normalized is None:
                    continue

                if not same_domain(self.start_url, normalized):
                    continue

                all_candidates.add(normalized)

            # IMPORTANT:
            # This loop must be outside the JavaScript candidate loop.
            # Otherwise, HTML links may not be queued correctly.
            new_count = 0

            for url in sorted(all_candidates):
                already_discovered = url in self.discovered_urls

                self.add_url(url, depth + 1)

                if (
                    not already_discovered
                    and url in self.discovered_urls
                ):
                    new_count += 1

            print(
                f"  Discovered {len(all_candidates)} candidates; "
                f"queued {new_count} new URL(s)."
            )

        # -----------------------------------------------------
        # Generate JSON report
        # -----------------------------------------------------
        report_file = save_json_report(
            target_url=self.start_url,
            discovered_urls=self.discovered_urls,
            visited_urls=self.visited_urls,
            url_categories=self.url_categories,
            output_path=self.report_path,
        )

        # -----------------------------------------------------
        # Display resource tree
        # -----------------------------------------------------
        print()

        print_resource_tree(
            target_url=self.start_url,
            discovered_urls=self.discovered_urls,
            url_categories=self.url_categories,
            url_statuses=self.url_statuses,
        )

        # -----------------------------------------------------
        # Display final summary
        # -----------------------------------------------------
        print_scan_summary(
            discovered_urls=self.discovered_urls,
            visited_urls=self.visited_urls,
            url_categories=self.url_categories,
            url_statuses=self.url_statuses,
            report_file=report_file,
        )

        return self.discovered_urls


def extract_html_urls(page_url, html, target_url):
    """Extract same-domain URLs from HTML elements."""

    soup = BeautifulSoup(html, "html.parser")

    discovered_urls = set()

    url_attributes = (
        "href",
        "src",
        "action",
        "formaction",
        "data",
        "poster",
    )

    for element in soup.find_all(True):
        for attribute in url_attributes:
            value = element.get(attribute)

            if not isinstance(value, str):
                continue

            value = value.strip()

            if not value:
                continue

            normalized_url = normalize_url(
                page_url,
                value,
            )

            if normalized_url is None:
                continue

            if not same_domain(target_url, normalized_url):
                continue

            discovered_urls.add(normalized_url)

    return discovered_urls