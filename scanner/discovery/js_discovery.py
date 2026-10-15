import re
from scanner.discovery.url_utils import normalize_url, same_domain
from bs4 import BeautifulSoup
from scanner.http.client import HTTPClient

# Recognize common JavaScript URL patterns.
URL_PATTERNS = [
    # window.location.href = "/dashboard"
    r"""(?:window\.)?location(?:\.href)?\s*=\s*(['"`])([^'"`]+)\1""",

    # window.location.assign("/dashboard")
    # window.location.replace("/dashboard")
    r"""(?:window\.)?location\.(?:assign|replace)\s*\(\s*(['"`])([^'"`]+)\1""",

    # window.open("/dashboard")
    r"""window\.open\s*\(\s*(['"`])([^'"`]+)\1""",

    # fetch("/api/products")
    r"""fetch\s*\(\s*(['"`])([^'"`]+)\1""",

    # axios.get("/api/products")
    # axios.post("/api/products")
    r"""axios\.(?:get|post|put|patch|delete)\s*\(\s*(['"`])([^'"`]+)\1""",
]


def extract_js_url_candidates(javascript_text):
    discovered_urls = set()

    for pattern in URL_PATTERNS:
        matches = re.findall(pattern, javascript_text, re.IGNORECASE)

        for match in matches:
            url = match[1].strip()

            if url:
                discovered_urls.add(url)

    return discovered_urls


def extract_inline_js_urls(html):
    soup = BeautifulSoup(html, "html.parser")

    discovered_urls = set()

    # Find JavaScript written inside HTML event attributes.
    for element in soup.find_all(True):
        for attribute, value in element.attrs.items():

            if attribute.lower().startswith("on"):
                if isinstance(value, str):
                    discovered_urls.update(
                        extract_js_url_candidates(value)
                    )

    # Find JavaScript written directly inside script elements.
    for script in soup.find_all("script"):

        # External scripts will be analyzed separately.
        if script.get("src"):
            continue

        javascript_text = script.string or script.get_text()

        discovered_urls.update(
            extract_js_url_candidates(javascript_text)
        )

    return discovered_urls


def find_javascript_files(page_url, html, target_url):
    soup = BeautifulSoup(html, "html.parser")

    javascript_urls = set()

    for script in soup.find_all("script", src=True):
        script_src = script["src"]

        script_url = normalize_url(page_url, script_src)

        if script_url is None:
            continue

        if not same_domain(target_url, script_url):
            continue

        javascript_urls.add(script_url)

    return javascript_urls


def analyze_javascript_file(client, javascript_url):
    try:
        response = client.get(javascript_url)

        response.raise_for_status()

        javascript_text = response.text

        discovered_urls = extract_js_url_candidates(
            javascript_text
        )

        return discovered_urls

    except Exception as error:
        print(f"Could not analyze {javascript_url}: {error}")
        return set()


def discover_urls_from_external_js(client, page_url, html, target_url):
    discovered_urls = set()

    javascript_files = find_javascript_files(
        page_url,
        html,
        target_url
    )

    for javascript_url in sorted(javascript_files):
        urls = analyze_javascript_file(
            client,
            javascript_url
        )

        for url in urls:
            normalized_url = normalize_url(
                javascript_url,
                url
            )

            if normalized_url is None:
                continue

            if not same_domain(target_url, normalized_url):
                continue

            discovered_urls.add(normalized_url)

    return discovered_urls