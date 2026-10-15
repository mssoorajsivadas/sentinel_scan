# SentinelScan v1.0.0

A lightweight Python-based URL discovery and reconnaissance tool
for authorized security testing.

SentinelScan crawls web pages, discovers URLs from HTML and
JavaScript, classifies discovered resources, and generates
structured JSON reports.

![image](https://github.com/mssoorajsivadas/sentinel_scan/blob/c21bd7ab9adeabf70bdd327e64b5585c90935c04/sentinel_scan.png)

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
git clone https://github.com/mssoorajsivadas/sentinel_scan.git
cd sentinel_scan
python run.py (target)
