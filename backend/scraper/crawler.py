"""
GovFlow AI — Site Crawler
Automatically discovers and scrapes ALL pages on a government website.

CONCEPT LESSON — Scraping vs Crawling:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  SCRAPING = You already know the URL → go fetch it.
    Example: "Go get https://drp.gov.lk/en/faq.php"

  CRAWLING = Start from one page → find all links → visit each one → repeat.
    Example: "Start at drp.gov.lk → follow every link → collect all pages"

THREE LEVELS of automation:
  Level 1 — Manual list    : you hardcode every URL (bad for big sites)
  Level 2 — Nav crawler    : scrape the navigation menu to get URLs (good)  ← WE DO THIS
  Level 3 — Full crawler   : follow EVERY link recursively (Googlebot style)

For government sites, Level 2 is best:
  - Navigation = the official list of important pages
  - Avoids junk pages (staff photos, procurement PDFs we don't need)
  - Fast and targeted
  - Stays within the service-relevant section

HOW THIS CRAWLER WORKS:
  Step 1 → Visit the homepage
  Step 2 → Extract ALL hrefs from the <nav> element
  Step 3 → Filter: same domain only, html pages only, no anchors-only
  Step 4 → Visit each discovered page
  Step 5 → Extract text content + metadata from each page
  Step 6 → Optionally: from each page, find MORE links (depth=2)
  Step 7 → Save everything to JSON

Run with:
  python -m scraper.crawler --site drp --depth 2
  python -m scraper.crawler --site drp --depth 1 --dry-run
"""

import json
import time
import argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Output directory ─────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# ── Site configurations ───────────────────────────────────────────────────────
# LEARNING: Instead of hardcoding URLs inside functions, we put site config
# in a dict. Add a new site = add one entry here. No other code changes.
SITE_CONFIGS = {
    "drp": {
        "name": "Department for Registration of Persons",
        "start_url": "https://drp.gov.lk/en/home.php",
        "base_domain": "drp.gov.lk",
        "allowed_path_prefix": "/en/",      # Only crawl English pages
        "nav_selector": "nav#navbar",        # CSS selector for the nav menu
        "content_selector": "main, section, .container",  # Where real content is
        "skip_patterns": [                   # URL patterns to skip
            "procurement",
            "staff",
            "structure",
            "vacancy",
            "inquire",
            "GN.php",
            "rif.php",
            "iau.php",
        ],
        "priority_pages": [                  # Always crawl these first
            "https://drp.gov.lk/en/normal.php",
            "https://drp.gov.lk/en/faq.php",
            "https://drp.gov.lk/en/downloads.php",
            "https://drp.gov.lk/en/other_service.php",
            "https://drp.gov.lk/en/contact.php",
        ],
        "output_file": "drp_crawled.json",
    },
    "gov_lk": {
        "name": "GOV.LK — Online Services",
        "start_url": "https://www.gov.lk/government/eservices",
        "base_domain": "gov.lk",
        "allowed_path_prefix": "/government/",
        "nav_selector": "nav, .navbar",
        "content_selector": "main, article, .content",
        "skip_patterns": ["login", "register", "search"],
        "priority_pages": [
            "https://www.gov.lk/government/eservices",
        ],
        "output_file": "govlk_crawled.json",
    },
}

HEADERS = {
    "User-Agent": "GovFlowAI/1.0 Research Bot (citizen service guidance platform)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
}


# ── Data model for a scraped page ────────────────────────────────────────────
@dataclass
class CrawledPage:
    url: str
    title: str
    page_type: str           # "nav_discovered" | "priority" | "linked"
    text_content: str
    headings: list[str]      # all h1, h2, h3 text
    links_found: list[str]   # outbound links found on this page
    word_count: int
    scraped_at: str
    http_status: int
    error: str | None = None


# ── Core crawler ──────────────────────────────────────────────────────────────
class SiteCrawler:
    """
    Automatic site crawler.

    LEARNING — Key concepts inside this class:
    - visited set     : prevents crawling the same URL twice (infinite loop protection)
    - queue           : list of URLs to visit next (breadth-first traversal)
    - depth control   : stop following links after N levels deep
    - domain filter   : only follow links to the same website
    - robots courtesy : sleep between requests (don't hammer servers)
    """

    def __init__(self, site_key: str, depth: int = 2, delay: float = 1.0, dry_run: bool = False):
        if site_key not in SITE_CONFIGS:
            raise ValueError(f"Unknown site: {site_key}. Options: {list(SITE_CONFIGS.keys())}")

        self.config = SITE_CONFIGS[site_key]
        self.max_depth = depth
        self.delay = delay          # seconds between requests
        self.dry_run = dry_run      # if True, only discover URLs — don't fetch content
        self.visited: set[str] = set()
        self.results: list[CrawledPage] = []

    # ── Step 1: Discover URLs from the navigation ─────────────────────────
    def discover_nav_urls(self) -> list[str]:
        """
        LEARNING: The navigation menu is the site's own curated list of
        important pages. Instead of blindly following every link,
        we start here — it's like asking "what does this site consider important?"

        This is smarter than a full crawl because:
        - Nav links = content pages (what citizens need)
        - Non-nav links = images, scripts, staff bios, search results (noise)
        """
        print(f"\n🔍 Discovering URLs from navigation...")
        print(f"   Start URL: {self.config['start_url']}")

        soup = self._fetch_soup(self.config["start_url"])
        if not soup:
            print("   ✗ Could not fetch start page")
            return []

        # Find the nav element using our CSS selector
        nav = soup.select_one(self.config["nav_selector"])

        if nav:
            link_elements = nav.find_all("a", href=True)
            print(f"   Found navigation element with {len(link_elements)} links")
        else:
            # Fallback: use ALL links on the page
            print(f"   ⚠ Nav selector '{self.config['nav_selector']}' not found — using all page links")
            link_elements = soup.find_all("a", href=True)

        discovered = []
        for link in link_elements:
            href = link["href"]
            label = link.get_text(strip=True)

            # Convert relative URLs to absolute
            # LEARNING: urljoin handles this correctly
            # urljoin("https://drp.gov.lk/en/home.php", "faq.php")
            # → "https://drp.gov.lk/en/faq.php"
            full_url = urljoin(self.config["start_url"], href)

            # Remove fragment (#section-name) — the page is the same
            full_url, _ = urldefrag(full_url)

            if self._should_crawl(full_url):
                discovered.append(full_url)
                print(f"   ✓ {label:<35} → {full_url}")
            else:
                pass  # Skip silently

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for url in discovered:
            if url not in seen:
                seen.add(url)
                unique.append(url)

        print(f"\n   Navigation discovered {len(unique)} crawlable URLs")
        return unique

    # ── Step 2: Crawl all discovered URLs ─────────────────────────────────
    def crawl(self) -> list[CrawledPage]:
        """
        Main crawl loop.

        LEARNING — Breadth-First Traversal:
        We use a queue (FIFO list). Each item is (url, depth).
        When we visit a page, we add its links to the END of the queue.
        This visits all depth-1 pages before any depth-2 pages.

        Depth 1: pages found in navigation
        Depth 2: pages linked FROM those pages
        Depth 3: pages linked from depth-2 pages (usually too much)
        """
        # Build initial queue: priority pages + nav-discovered pages
        queue: list[tuple[str, int]] = []

        # Priority pages always go first (depth=1)
        for url in self.config["priority_pages"]:
            if url not in self.visited:
                queue.append((url, 1))

        # Nav-discovered pages go next
        nav_urls = self.discover_nav_urls()
        for url in nav_urls:
            if url not in self.visited:
                queue.append((url, 1))

        print(f"\n🕷  Starting crawl ({len(queue)} URLs queued, max depth={self.max_depth})")
        print(f"   Dry run: {self.dry_run}")
        print()

        while queue:
            url, depth = queue.pop(0)  # Take from front = breadth-first

            # Skip if already visited
            if url in self.visited:
                continue

            self.visited.add(url)

            if self.dry_run:
                print(f"  [DRY] depth={depth} → {url}")
                continue

            # Fetch and process the page
            page = self._scrape_page(url, depth)
            self.results.append(page)

            # If within depth limit, add links found on this page to queue
            if depth < self.max_depth and page.error is None:
                new_links_added = 0
                for link_url in page.links_found:
                    if link_url not in self.visited and self._should_crawl(link_url):
                        queue.append((link_url, depth + 1))
                        new_links_added += 1

                if new_links_added > 0:
                    print(f"     → Queued {new_links_added} new links (depth {depth + 1})")

            # Be polite — wait between requests
            time.sleep(self.delay)

        print(f"\n✅ Crawl complete: {len(self.results)} pages scraped")
        return self.results

    # ── Step 3: Scrape a single page ──────────────────────────────────────
    def _scrape_page(self, url: str, depth: int) -> CrawledPage:
        """
        LEARNING: This is where we extract structured data from each page.
        We extract:
        - Title (from <title> tag or <h1>)
        - Main text content (from content area, not nav/footer)
        - All headings (good for chunking later in RAG)
        - All outbound links (for further crawling at next depth)
        """
        print(f"  [{depth}] Fetching: {url}")

        soup = self._fetch_soup(url)
        if not soup:
            return CrawledPage(
                url=url, title="", page_type="nav_discovered",
                text_content="", headings=[], links_found=[],
                word_count=0, scraped_at=datetime.now(timezone.utc).isoformat(),
                http_status=0, error="Failed to fetch page"
            )

        # Extract title
        title_tag = soup.find("title")
        h1_tag = soup.find("h1")
        title = (title_tag.get_text(strip=True) if title_tag else
                 h1_tag.get_text(strip=True) if h1_tag else url)

        # Extract main content (remove nav, footer, scripts)
        # LEARNING: We remove noise elements before extracting text
        for tag in soup.find_all(["nav", "footer", "script", "style", "header"]):
            tag.decompose()  # removes the tag and its children from the tree

        # Try content selector first, fall back to body
        content_area = soup.select_one(self.config["content_selector"])
        if not content_area:
            content_area = soup.find("body")

        text_content = content_area.get_text(separator="\n", strip=True) if content_area else ""

        # Extract headings (useful for RAG chunking later)
        headings = [
            f"{tag.name.upper()}: {tag.get_text(strip=True)}"
            for tag in soup.find_all(["h1", "h2", "h3", "h4"])
            if tag.get_text(strip=True)
        ]

        # Extract all links on this page (for depth+1 crawling)
        links_found = []
        for link in soup.find_all("a", href=True):
            full_url = urljoin(url, link["href"])
            full_url, _ = urldefrag(full_url)
            if self._should_crawl(full_url):
                links_found.append(full_url)

        word_count = len(text_content.split())
        print(f"     ✓ {title[:50]:<50} | {word_count} words | {len(links_found)} links")

        return CrawledPage(
            url=url,
            title=title,
            page_type="depth_" + str(depth),
            text_content=text_content,
            headings=headings,
            links_found=list(set(links_found)),
            word_count=word_count,
            scraped_at=datetime.now(timezone.utc).isoformat(),
            http_status=200,
        )

    # ── Helpers ───────────────────────────────────────────────────────────
    def _fetch_soup(self, url: str) -> BeautifulSoup | None:
        """Fetch a URL and return BeautifulSoup, or None on failure."""
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")
        except requests.RequestException as e:
            print(f"     ✗ Request failed: {e}")
            return None

    def _should_crawl(self, url: str) -> bool:
        """
        Decide whether a URL is worth crawling.

        LEARNING: This is the "filter" step. Without this, a crawler
        would follow links to:
        - External websites (twitter.com, youtube.com)
        - Asset files (images, CSS, JS)
        - Anchor-only links (#section)
        - Pages we've decided to skip (procurement, staff bios)

        Filtering = signal over noise.
        """
        parsed = urlparse(url)

        # Must be http or https
        if parsed.scheme not in ("http", "https"):
            return False

        # Must be same domain
        # LEARNING: netloc is "drp.gov.lk" — we check if it ends with our domain
        # This also allows subdomains like "www.drp.gov.lk"
        if self.config["base_domain"] not in parsed.netloc:
            return False

        # Must match allowed path prefix (if configured)
        if self.config.get("allowed_path_prefix"):
            if not parsed.path.startswith(self.config["allowed_path_prefix"]):
                return False

        # Skip non-HTML files
        path_lower = parsed.path.lower()
        skip_extensions = (".jpg", ".jpeg", ".png", ".gif", ".pdf",
                           ".css", ".js", ".svg", ".ico", ".zip", ".docx")
        if any(path_lower.endswith(ext) for ext in skip_extensions):
            return False

        # Skip patterns defined in site config
        for pattern in self.config.get("skip_patterns", []):
            if pattern.lower() in url.lower():
                return False

        return True

    def save(self) -> Path:
        """Save crawl results to JSON."""
        output = {
            "crawled_at": datetime.now(timezone.utc).isoformat(),
            "site": self.config["name"],
            "total_pages": len(self.results),
            "pages": [asdict(page) for page in self.results],
        }

        output_path = DATA_DIR / self.config["output_file"]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Saved to: {output_path}")
        print(f"   Total pages: {len(self.results)}")
        print(f"   Total words: {sum(p.word_count for p in self.results):,}")
        return output_path


# ── CLI entry point ───────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="GovFlow AI Site Crawler")
    parser.add_argument(
        "--site",
        choices=list(SITE_CONFIGS.keys()),
        default="drp",
        help="Which site to crawl (default: drp)"
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=2,
        help="How many levels deep to follow links (default: 2)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Seconds to wait between requests (default: 1.0 — be polite!)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only discover URLs, don't fetch content"
    )
    args = parser.parse_args()

    crawler = SiteCrawler(
        site_key=args.site,
        depth=args.depth,
        delay=args.delay,
        dry_run=args.dry_run,
    )

    print(f"🚀 GovFlow AI Crawler")
    print(f"   Site    : {crawler.config['name']}")
    print(f"   Domain  : {crawler.config['base_domain']}")
    print(f"   Depth   : {args.depth}")
    print(f"   Delay   : {args.delay}s")

    crawler.crawl()

    if not args.dry_run:
        crawler.save()


if __name__ == "__main__":
    main()
