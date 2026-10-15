import argparse
import sys

from scanner.discovery.crawler import Crawler


def main():

    parser = argparse.ArgumentParser(
        prog="SentinelScan",
        description="A URL discovery and reconnaissance scanner.",
    )

    parser.add_argument(
        "target",
        help="Target URL to scan. Only scan systems you are authorized to test.",
    )

    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Maximum crawl depth (default: 2).",
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=100,
        help="Maximum number of pages processed (default: 100).",
    )

    parser.add_argument(
        "--output",
        default="reports/scan_report.json",
        help="JSON report path (default: reports/scan_report.json).",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay in seconds between HTTP requests (default: 1.0)",
    )

    args = parser.parse_args()

    if args.max_depth < 0:
        parser.error("--max-depth cannot be negative.")

    if args.max_pages < 1:
        parser.error("--max-pages must be at least 1.")

    try:
        crawler = Crawler(
            start_url=args.target,
            max_depth=args.max_depth,
            max_pages=args.max_pages,
            report_path=args.output,
            request_delay=args.delay,
        )

        crawler.crawl()

    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()