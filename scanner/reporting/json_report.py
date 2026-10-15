import json
from datetime import datetime, timezone
from pathlib import Path


def save_json_report(
    target_url,
    discovered_urls,
    visited_urls,
    url_categories,
    output_path="reports/scan_report.json",
):
    """
    Save crawler results as a JSON report.
    """

    discovered_urls = sorted(discovered_urls)
    visited_urls = set(visited_urls)

    # Build the inventory of discovered URLs.
    url_inventory = []

    for url in discovered_urls:
        url_inventory.append({
            "url": url,
            "category": url_categories.get(url, "Unknown"),
            "visited": url in visited_urls,
        })

    # Count categories in the inventory.
    category_counts = {}

    for item in url_inventory:
        category = item["category"]

        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

    # Build the report.
    report = {
        "scanner": "SentinelScan",
        "report_version": "1.0",
        "target": target_url,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "summary": {
            "total_discovered": len(discovered_urls),
            "total_visited": len(visited_urls),
            "categories": category_counts,
        },
        "discovered_urls": url_inventory,
    }

    # Create the output directory if necessary.
    output_file = Path(output_path)
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Write readable JSON.
    with output_file.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
        )

    return output_file