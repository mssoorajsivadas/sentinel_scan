from collections import defaultdict
from urllib.parse import urlparse


def print_banner():
    print()
    print("=" * 64)
    print("                    SENTINELSCAN")
    print("           URL Discovery & Reconnaissance")
    print("=" * 64)
    print()


def print_scan_config(target_url, max_depth, max_pages, report_path):
    print(f"  Target       : {target_url}")
    print(f"  Maximum depth: {max_depth}")
    print(f"  Maximum pages: {max_pages}")
    print(f"  Report       : {report_path}")
    print()


def print_resource_tree(
    target_url,
    discovered_urls,
    url_categories,
    url_statuses,
):
    """Print discovered URLs in a hierarchical tree."""

    parsed_target = urlparse(target_url)
    root_label = f"{parsed_target.scheme}://{parsed_target.netloc}"

    tree = {
        "children": {},
        "resources": [],
    }

    # Organize URLs into a tree based on their paths.
    for url in sorted(discovered_urls):
        parsed = urlparse(url)
        parts = [part for part in parsed.path.split("/") if part]

        # Keep query parameters visible in the tree.
        if parsed.query:
            query_label = f"?{parsed.query}"

            if parts:
                parts[-1] += query_label
            else:
                parts.append(query_label)

        node = tree

        for part in parts:
            if part not in node["children"]:
                node["children"][part] = {
                    "children": {},
                    "resources": [],
                }

            node = node["children"][part]

        node["resources"].append({
            "url": url,
            "category": url_categories.get(url, "Unknown"),
            "status": url_statuses.get(url),
        })

    print("DISCOVERED RESOURCES")
    print("-" * 64)
    print(root_label + "/")

    def display_resources(resources, prefix):
        for resource in resources:
            category = resource["category"].upper()
            status = resource["status"]

            if status is None:
                status_text = "NOT VISITED"
            else:
                status_text = str(status)

            print(
                f"{prefix}    "
                f"[{category}] [{status_text}]"
            )

    def display_node(node, prefix=""):
        children = sorted(node["children"].items())

        for index, (name, child) in enumerate(children):
            is_last = index == len(children) - 1

            branch = "└── " if is_last else "├── "
            print(f"{prefix}{branch}{name}")

            next_prefix = prefix + (
                "    " if is_last else "│   "
            )

            display_resources(child["resources"], next_prefix)
            display_node(child, next_prefix)

    # Show the starting URL's status/category, if available.
    display_resources(tree["resources"], "")

    display_node(tree)
    print()


def print_scan_summary(
    discovered_urls,
    visited_urls,
    url_categories,
    url_statuses,
    report_file,
):
    """Print final scan statistics and report location."""

    discovered_urls = set(discovered_urls)
    visited_urls = set(visited_urls)

    category_counts = defaultdict(int)

    for url in discovered_urls:
        category = url_categories.get(url, "Unknown")
        category_counts[category] += 1

    failed_requests = sum(
        1
        for status in url_statuses.values()
        if status == "ERROR"
    )

    print("SCAN SUMMARY")
    print("-" * 64)
    print(f"  URLs discovered : {len(discovered_urls)}")
    print(f"  URLs visited    : {len(visited_urls)}")
    print(f"  Failed requests : {failed_requests}")

    print()
    print("  RESOURCE CATEGORIES")

    for category, count in sorted(category_counts.items()):
        print(f"  {category:<30} {count}")

    print()
    print("JSON REPORT")
    print(f"  {report_file}")
    print()
    print("Scan completed.")
    print()