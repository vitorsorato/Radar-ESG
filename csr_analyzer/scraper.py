from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import List, Dict, Any, Iterable, Optional, Tuple
from urllib.parse import urljoin, urlparse

import feedparser
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import trafilatura


@dataclass
class Article:
    url: str
    title: str
    published: Optional[str]
    site: str
    text: str


# --- CSV loaders and pattern builders ---

def _load_list_with_optional_regex(path: str, value_col: str, regex_col: str) -> List[Tuple[str, Optional[re.Pattern]]]:
    df = pd.read_csv(path)
    values = []
    for _, row in df.iterrows():
        raw_value = str(row.get(value_col, "")).strip()
        raw_regex = str(row.get(regex_col, "")).strip() if regex_col in df.columns else ""
        if not raw_value and not raw_regex:
            continue
        if raw_regex:
            try:
                pattern = re.compile(raw_regex, flags=re.IGNORECASE)
            except re.error:
                pattern = re.compile(re.escape(raw_regex), flags=re.IGNORECASE)
            values.append((raw_value or raw_regex, pattern))
        else:
            # simple case-insensitive substring search
            pattern = re.compile(re.escape(raw_value), flags=re.IGNORECASE)
            values.append((raw_value, pattern))
    return values


# --- link discovery ---

LIKELY_ARTICLE_HINTS = [
    "/noticia", "/notícias", "/news", "/economia", "/sustentabilidade", "/meio-ambiente",
    "/ambiente", "/esg", "/responsabilidade-social", "/social", "/ambiental",
]


def _is_probable_article_path(path: str) -> bool:
    if any(hint in path.lower() for hint in LIKELY_ARTICLE_HINTS):
        return True
    if re.search(r"/(19|20)\d{2}/", path):  # contains a year
        return True
    if re.search(r"/\d{4,}/", path):  # long numeric ids
        return True
    return False


def _discover_links_from_homepage(base_url: str, limit: int = 100) -> List[Tuple[str, Optional[str]]]:
    headers = {"User-Agent": "csr-analyzer/0.1 (+research)"}
    try:
        resp = requests.get(base_url, headers=headers, timeout=15)
        resp.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    seen = set()
    links: List[Tuple[str, Optional[str]]] = []
    base = resp.url
    for a in soup.find_all("a", href=True):
        href = a["href"]
        url = urljoin(base, href)
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            continue
        if parsed.fragment:
            url = url.split("#", 1)[0]
        # same site only
        if urlparse(base).netloc != parsed.netloc:
            continue
        path = parsed.path or "/"
        if not _is_probable_article_path(path):
            continue
        if url in seen:
            continue
        seen.add(url)
        title = a.get_text(strip=True) or None
        links.append((url, title))
        if len(links) >= limit:
            break
    return links


def _discover_from_feed(base_url: str, limit: int = 200) -> List[Tuple[str, Optional[str], Optional[str]]]:
    # Try reading base_url as feed; if not, quick fallbacks are omitted for simplicity
    parsed = feedparser.parse(base_url)
    items: List[Tuple[str, Optional[str], Optional[str]]] = []
    for entry in parsed.entries[:limit]:
        url = getattr(entry, "link", None)
        title = getattr(entry, "title", None)
        published = getattr(entry, "published", None) or getattr(entry, "updated", None)
        if url:
            items.append((url, title, published))
    return items


# --- article extraction ---


def _extract_article(url: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Return (title, text, date) using trafilatura with JSON output if possible."""
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return None, None, None
    try:
        # Ask for JSON to capture metadata
        extracted_json = trafilatura.extract(downloaded, output_format="json", with_metadata=True)
        if extracted_json:
            import json

            data = json.loads(extracted_json)
            title = data.get("title")
            text = data.get("text")
            date = data.get("date")
            return title, text, date
        else:
            text_only = trafilatura.extract(downloaded)
            return None, text_only, None
    except Exception:
        try:
            text_only = trafilatura.extract(downloaded)
            return None, text_only, None
        except Exception:
            return None, None, None


# --- filtering ---

def _match_any(text: str, patterns: List[Tuple[str, re.Pattern]]) -> List[str]:
    matches: List[str] = []
    for label, patt in patterns:
        if patt.search(text):
            matches.append(label)
    return matches


# --- main orchestrator ---

def scrape_news(
    urls_file: str,
    companies_file: str,
    terms_file: str,
    max_articles_per_site: int = 100,
    request_delay: float = 0.2,
    homepage_link_limit: int = 100,
    feed_item_limit: int = 200,
) -> pd.DataFrame:
    """Collect candidate articles from a set of base URLs and filter by company and socio-environmental terms.

    Returns a DataFrame with columns: url, title, published, site, text, matched_companies, matched_terms
    """

    company_patterns = _load_list_with_optional_regex(companies_file, value_col="name", regex_col="regex")
    term_patterns = _load_list_with_optional_regex(terms_file, value_col="term", regex_col="regex")

    urls_df = pd.read_csv(urls_file)
    base_urls = [str(u).strip() for u in urls_df["url"].dropna().astype(str).tolist() if str(u).strip()]

    collected: List[Article] = []

    for base_url in tqdm(base_urls, desc="Sites"):
        # First try feeds
        feed_items = _discover_from_feed(base_url, limit=feed_item_limit)
        candidate_links: List[Tuple[str, Optional[str], Optional[str]]] = []
        if feed_items:
            candidate_links.extend(feed_items)
        else:
            # Fallback to homepage link discovery
            links = _discover_links_from_homepage(base_url, limit=homepage_link_limit)
            candidate_links.extend([(u, t, None) for (u, t) in links])

        seen_urls = set()
        per_site_count = 0

        for url, title_hint, published in tqdm(candidate_links[:max_articles_per_site], leave=False, desc="Artigos"):
            if url in seen_urls:
                continue
            seen_urls.add(url)

            extracted_title, extracted_text, extracted_date = _extract_article(url)
            title = extracted_title or title_hint or ""
            text = extracted_text or ""
            published_str = extracted_date or published
            if not text:
                continue

            site = urlparse(url).netloc
            collected.append(Article(url=url, title=title, published=published_str, site=site, text=text))
            per_site_count += 1
            time.sleep(request_delay)

            if per_site_count >= max_articles_per_site:
                break

    # Build DataFrame
    rows: List[Dict[str, Any]] = []
    for art in collected:
        haystack = f"{art.title}\n{art.text}"
        matched_companies = _match_any(haystack, company_patterns)
        matched_terms = _match_any(haystack, term_patterns)
        if matched_companies and matched_terms:
            rows.append(
                {
                    "url": art.url,
                    "title": art.title,
                    "published": art.published,
                    "site": art.site,
                    "text": art.text,
                    "matched_companies": "; ".join(sorted(set(matched_companies))),
                    "matched_terms": "; ".join(sorted(set(matched_terms))),
                }
            )

    return pd.DataFrame(rows)
