# SentinelScan v1.0.0

A lightweight Python-based URL discovery and reconnaissance tool
for authorized security testing.

SentinelScan crawls web pages, discovers URLs from HTML and
JavaScript, classifies discovered resources, and generates
structured JSON reports.

## Project Structure

sentinel_scan/
├── scanner/
│   ├── __init__.py
│   ├── __main__.py
│   ├── http/
│   │   ├── __init__.py
│   │   └── client.py
│   ├── discovery/
│   │   ├── __init__.py
│   │   ├── crawler.py
│   │   ├── url_utils.py
│   │   ├── js_discovery.py
│   │   └── classifier.py
│   └── reporting/
│       ├── __init__.py
│       └── json_report.py
├── reports/
├── requirements.txt
├── README.md
└── .gitignore

## Features

- HTTP requests with configurable timeouts.
- URL normalization and same-domain filtering.
- Recursive web crawling with configurable depth.
- Maximum page limit.
- URL discovery from HTML links and resource attributes.
- URL discovery from inline JavaScript.
- URL discovery from external JavaScript files.
- Resource classification, including:
  - HTML pages
  - Potential API endpoints
  - JavaScript files
  - Stylesheets
  - Images
  - Documents
  - Fonts
- Explicit handling of redirects within the target scope.
- Request delay to reduce unnecessary server load.
- Graceful handling of connection failures.
- JSON reports containing discovered URLs, categories,
  and visit status.

## Requirements

- Python 3.10 or newer
- pip

## Installation

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd sentinel_scan