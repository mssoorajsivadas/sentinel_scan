from urllib.parse import urlparse
from pathlib import PurePosixPath


def classify_url(url, content_type=None, status_code=None):
    """
    Classify a resource using its URL, response type, and status.
    """

    parsed_url = urlparse(url)

    path = parsed_url.path.lower()
    filename = PurePosixPath(path).name
    extension = PurePosixPath(filename).suffix

    # Identify likely API endpoints first.
    if (
        path == "/api"
        or path.startswith("/api/")
    ):
        if status_code == 405:
            return "Potential API (method restricted)"

        return "Potential API"

    # Identify JavaScript files.
    if extension in {".js", ".mjs"}:
        return "JavaScript"

    # Identify stylesheets.
    if extension == ".css":
        return "Stylesheet"

    # Identify images.
    if extension in {
        ".png", ".jpg", ".jpeg", ".gif",
        ".webp", ".svg", ".ico", ".bmp",
    }:
        return "Image"

    # Identify documents.
    if extension in {
        ".pdf", ".doc", ".docx",
        ".xls", ".xlsx", ".txt",
    }:
        return "Document"

    # Identify fonts.
    if extension in {
        ".woff", ".woff2", ".ttf", ".otf",
    }:
        return "Font"

    # Examine the actual response type.
    if content_type:
        content_type = (
            content_type.split(";")[0].strip().lower()
        )

        if content_type in {
            "text/html",
            "application/xhtml+xml",
        }:
            return "HTML page"

        if (
            content_type in {
                "application/json",
                "text/json",
            }
            or content_type.endswith("+json")
        ):
            return "Potential API"

        if content_type in {
            "application/javascript",
            "text/javascript",
        } or content_type.endswith("/javascript"):
            return "JavaScript"

        if content_type == "text/css":
            return "Stylesheet"

        if content_type.startswith("image/"):
            return "Image"

        if content_type == "application/pdf":
            return "Document"

        if content_type.startswith("font/"):
            return "Font"

    return "Unknown"