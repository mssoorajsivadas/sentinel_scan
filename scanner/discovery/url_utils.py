from urllib.parse import urljoin, urlparse, urldefrag


def normalize_url(base_url, found_url):
    absolute_url = urljoin(base_url, found_url)

    absolute_url, _ = urldefrag(absolute_url)

    parsed = urlparse(absolute_url)

    if parsed.scheme not in {"http", "https"}:
        return None

    if parsed.path != "/":
        absolute_url = absolute_url.rstrip("/")

    return absolute_url


def same_domain(base_url, candidate_url):
    base = urlparse(base_url)
    candidate = urlparse(candidate_url)

    return (
        base.scheme in {"http", "https"}
        and candidate.scheme in {"http", "https"}
        and base.netloc == candidate.netloc
    )