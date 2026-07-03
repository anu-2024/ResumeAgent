# utils/jd_scraper.py
# ─────────────────────────────────────────────
# Fetches Job Description text from a URL
# Primary:  Firecrawl API (JS-heavy sites like
#           LinkedIn, Greenhouse, Lever)
# Fallback: httpx + BeautifulSoup (static pages)
# ─────────────────────────────────────────────

import os
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


def scrape_with_firecrawl(url: str) -> str:
    """
    Uses Firecrawl API to scrape JS-rendered pages.
    Works great for LinkedIn, Greenhouse, Lever, Workday.
    """
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise EnvironmentError("FIRECRAWL_API_KEY not set in .env")

    from firecrawl import FirecrawlApp
    app = FirecrawlApp(api_key=api_key)
    result = app.scrape_url(url, params={"formats": ["markdown"]})
    return result.get("markdown", "")


def scrape_with_httpx(url: str) -> str:
    """
    Simple fallback scraper using httpx + BeautifulSoup.
    Works for basic static job pages.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    response = httpx.get(url, headers=headers,
                         timeout=15, follow_redirects=True, verify=False)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove unnecessary parts of the page
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # Extract clean text
    text = soup.get_text(separator="\n", strip=True)

    # Remove excessive blank lines
    lines = [l for l in text.splitlines() if l.strip()]
    return "\n".join(lines)


def fetch_jd_from_url(url: str) -> str:
    """
    Main function called by Streamlit.
    Tries Firecrawl first, falls back to httpx.
    """
    # Try Firecrawl if API key exists
    if os.getenv("FIRECRAWL_API_KEY"):
        try:
            text = scrape_with_firecrawl(url)
            if text and len(text) > 200:
                return text
        except Exception:
            pass  # silently fall through to backup

    # Fallback to httpx + BeautifulSoup
    try:
        text = scrape_with_httpx(url)
        if text and len(text) > 200:
            return text
    except Exception as e:
        raise RuntimeError(
            f"Could not fetch JD from URL.\n"
            f"Error: {e}\n"
            f"💡 Tip: Paste the JD text directly instead."
        )

    raise RuntimeError(
        "Scraped content too short or empty. "
        "Please paste the JD text directly."
    )