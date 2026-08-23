"""
NIC Scraper — Department for Registration of Persons
Target: https://drp.gov.lk/en/
Scrapes: procedure pages, FAQs, available info

LEARNING NOTE:
- requests.get() sends an HTTP GET request (like your browser loading a page)
- response.text is the raw HTML string
- BeautifulSoup parses that string into a tree you can navigate
"""

import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
BASE_URL = "https://drp.gov.lk/en"
HEADERS = {
    # We identify ourselves politely — not hiding that we're a script
    "User-Agent": "GovFlowAI/1.0 Research Bot (government service guidance platform)",
    "Accept-Language": "en-US,en;q=0.9",
}
OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)


# ── Helper: fetch one page ───────────────────────────────────────────────────
def fetch_page(url: str) -> BeautifulSoup | None:
    """
    Fetch a URL and return a BeautifulSoup object.
    Returns None if the request fails.
    
    LEARNING: We wrap requests in try/except because network calls CAN fail.
    Always handle failure gracefully.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()  # raises exception for 4xx/5xx status codes
        print(f"  [OK] Fetched: {url} ({len(response.text)} chars)")
        return BeautifulSoup(response.text, "lxml")
    except requests.RequestException as e:
        print(f"  [ERROR] Failed: {url} -> {e}")
        return None


# ── Scraper 1: FAQ page ──────────────────────────────────────────────────────
def scrape_faq() -> list[dict]:
    """
    Scrapes drp.gov.lk/en/faq.php
    Returns list of {question, answer} dicts
    
    LEARNING: Government FAQ pages are usually accordion/collapse components.
    The text is in the HTML but hidden visually — BeautifulSoup sees all of it.
    """
    soup = fetch_page(f"{BASE_URL}/faq.php")
    if not soup:
        return []

    faqs = []
    
    # Each FAQ item is an <li> inside the .faq-list div
    # LEARNING: soup.select() uses CSS selectors — same syntax as browser DevTools
    faq_items = soup.select(".faq-list li")
    
    for item in faq_items:
        # The question is in the <a> tag inside the accordion trigger
        question_tag = item.find("a", {"data-bs-toggle": "collapse"})
        # The answer is in the collapse div
        answer_tag = item.find("div", {"class": "collapse"})
        
        if question_tag and answer_tag:
            question = question_tag.get_text(strip=True)
            # Remove the chevron icon text that gets picked up
            question = question.replace("", "").strip()
            answer = answer_tag.get_text(separator=" ", strip=True)
            
            # Only add if both exist and question is meaningful
            if len(question) > 10 and len(answer) > 10:
                faqs.append({
                    "question": question,
                    "answer": answer,
                    "source_url": f"{BASE_URL}/faq.php",
                    "section": "faq"
                })
    
    print(f"  -> Extracted {len(faqs)} FAQ items")
    return faqs


# ── Scraper 2: NIC procedure pages ───────────────────────────────────────────
def scrape_normal_service() -> list[dict]:
    """
    Scrapes drp.gov.lk/en/normal.php
    Returns list of service procedure sections
    
    LEARNING: This page uses Bootstrap tabs (v-pills).
    Each tab panel contains a different NIC service type.
    """
    soup = fetch_page(f"{BASE_URL}/normal.php")
    if not soup:
        return []

    procedures = []
    
    # Tab panels — each panel is one service type
    # LEARNING: We look for the tab-content div, then find each pane inside
    tab_content = soup.find("div", {"class": "tab-content"})
    if not tab_content:
        # Fallback: grab all content sections
        print("  [WARN] Could not find tab-content, using full page text")
        full_text = soup.get_text(separator="\n", strip=True)
        procedures.append({
            "service_type": "nic_procedures",
            "content": full_text[:5000],  # first 5000 chars
            "source_url": f"{BASE_URL}/normal.php",
            "section": "procedures"
        })
        return procedures
    
    # Map tab IDs to service types
    tab_map = {
        "v-pills-home": "nic_first_time",
        "v-pills-profile": "nic_lost",
        "v-pills-operation": "nic_amendment",
        "v-pills-development": "nic_dual_citizen",
        "v-pills-audit": "nic_one_day_service",
    }
    
    for tab_id, service_type in tab_map.items():
        panel = soup.find("div", {"id": tab_id})
        if panel:
            content = panel.get_text(separator="\n", strip=True)
            # Extract any list items (document lists are usually <li> tags)
            list_items = [li.get_text(strip=True) for li in panel.find_all("li")]
            
            procedures.append({
                "service_type": service_type,
                "content": content,
                "list_items": list_items,
                "source_url": f"{BASE_URL}/normal.php#{tab_id}-tab",
                "section": "procedures"
            })
            print(f"    -> {service_type}: {len(content)} chars, {len(list_items)} list items")
    
    return procedures


# ── Scraper 3: Downloads page (forms) ────────────────────────────────────────
def scrape_downloads() -> list[dict]:
    """
    Scrapes drp.gov.lk/en/downloads.php
    Returns list of downloadable forms with URLs
    """
    soup = fetch_page(f"{BASE_URL}/downloads.php")
    if not soup:
        return []

    downloads = []
    
    # Find all links that look like form downloads (PDFs)
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if ".pdf" in href.lower() or "download" in href.lower():
            full_url = href if href.startswith("http") else f"https://drp.gov.lk/{href.lstrip('/')}"
            downloads.append({
                "name": link.get_text(strip=True),
                "url": full_url,
                "source_url": f"{BASE_URL}/downloads.php",
                "section": "forms"
            })
    
    print(f"  -> Found {len(downloads)} downloadable forms")
    return downloads


# ── Main runner ──────────────────────────────────────────────────────────────
def run():
    print("[SCRAPE] Starting NIC scraper...")
    print(f"   Target: {BASE_URL}")
    print(f"   Output: {OUTPUT_DIR / 'nic_raw.json'}")
    print()
    
    result = {
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "source_department": "Department for Registration of Persons",
        "source_base_url": BASE_URL,
        "data": {}
    }
    
    # 1. FAQs
    print("[FAQ] Scraping FAQs...")
    result["data"]["faqs"] = scrape_faq()
    time.sleep(1)  # LEARNING: Be polite — don't hammer the server
    
    # 2. Procedures
    print("[PROCEDURES] Scraping NIC procedures...")
    result["data"]["procedures"] = scrape_normal_service()
    time.sleep(1)
    
    # 3. Downloads
    print("[FORMS] Scraping downloads/forms...")
    result["data"]["downloads"] = scrape_downloads()
    
    # Save
    output_path = OUTPUT_DIR / "nic_raw.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print()
    print(f"[OK] Done! Saved to: {output_path}")
    print(f"   FAQs: {len(result['data']['faqs'])}")
    print(f"   Procedures: {len(result['data']['procedures'])}")
    print(f"   Downloads: {len(result['data']['downloads'])}")


if __name__ == "__main__":
    run()
