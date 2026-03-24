import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


USER_AGENT = "ThinkRoundFAQBot/1.0"
ALLOWED_DOMAINS = {"thinkround.org", "www.thinkround.org"}


def is_allowed(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.netloc in ALLOWED_DOMAINS
    except Exception:
        return False


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    # remove fragments like #section1
    return parsed._replace(fragment="").geturl()


def fetch_page(url: str) -> tuple[str, str]:
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=20
    )
    response.raise_for_status()
    return response.text, response.url


def extract_title_and_text(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")

    # remove unnecessary tags
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else "Untitled"

    main = soup.find("main")
    if main:
        text = main.get_text("\n", strip=True)
    elif soup.body:
        text = soup.body.get_text("\n", strip=True)
    else:
        text = soup.get_text("\n", strip=True)

    # clean extra blank lines/spaces
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return title, text.strip()


def crawl_site(start_url: str, max_pages: int = 10, delay: float = 0.5):
    visited = set()
    queue = [start_url]
    results = []

    while queue and len(results) < max_pages:
        current_url = normalize_url(queue.pop(0))

        if current_url in visited:
            continue
        if not is_allowed(current_url):
            continue

        visited.add(current_url)

        try:
            html, final_url = fetch_page(current_url)
            title, text = extract_title_and_text(html)

            results.append({
                "url": final_url,
                "title": title,
                "text": text
            })

            print(f"Fetched: {final_url}")

            soup = BeautifulSoup(html, "html.parser")
            for link in soup.find_all("a", href=True):
                next_url = normalize_url(urljoin(final_url, link["href"]))
                if is_allowed(next_url) and next_url not in visited:
                    queue.append(next_url)

            time.sleep(delay)

        except Exception as e:
            print(f"Failed: {current_url} -> {e}")

    return results


# if __name__ == "__main__":
#     pages = crawl_site("https://www.thinkround.org/", max_pages=5)

#     print("\n--- CRAWL SUMMARY ---")
#     print(f"Total pages fetched: {len(pages)}")

#     for i, page in enumerate(pages, start=1):
#         print(f"\nPage {i}")
#         print("URL:", page["url"])
#         print("Title:", page["title"])
#         print("Text preview:", page["text"][:500])

import json
import os

if __name__ == "__main__":
    pages = crawl_site("https://www.thinkround.org/", max_pages=20)

    print("\n--- CRAWL SUMMARY ---")
    print(f"Total pages fetched: {len(pages)}")

    os.makedirs("data", exist_ok=True)

    with open("data/thinkround_pages.json", "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2)

    print("\nSaved pages to data/thinkround_pages.json")