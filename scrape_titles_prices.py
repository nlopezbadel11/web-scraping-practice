#!/usr/bin/env python3
"""
Simple scraper for books.toscrape.com
Extracts book titles and prices and saves them to a CSV file.
"""

import time
import random
import argparse
import csv
from typing import Iterator, Tuple, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com"


def get_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.3, status_forcelist=(429, 500, 502, 503, 504))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; Bot/0.1)"})
    return session


def parse_books_from_page(html: bytes) -> Iterator[Tuple[str, float, str]]:
    soup = BeautifulSoup(html, "html.parser")
    books = soup.find_all("article", class_="product_pod")
    for book in books:
        title = book.h3.a.get("title", "").strip()
        price_text = book.find("p", class_="price_color").get_text(strip=True)
        try:
            price = float(price_text.replace("£", ""))
        except ValueError:
            continue

        rating_tag = book.find("p", class_="star-rating")
        rating_word = ""
        if rating_tag and rating_tag.get("class") and len(rating_tag["class"]) > 1:
            rating_word = rating_tag["class"][1]

        yield title, price, rating_word


def scrape_titles_prices(base_url: str, max_pages: Optional[int] = None) -> Iterator[Tuple[str, float, str]]:
    """Scrape book pages by following site's pagination links.

    If `max_pages` is None, the scraper will follow "next" links until none remain (crawl the whole site).
    Otherwise it will stop after `max_pages` pages.
    """
    session = get_session()
    url = f"{base_url}/index.html"
    page_num = 0

    while True:
        page_num += 1
        try:
            resp = session.get(url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException:
            # Stop on request error
            break

        books = list(parse_books_from_page(resp.content))
        if not books:
            break

        for title, price, rating_word in books:
            yield title, price, rating_word

        # If max_pages is set and we've reached it, stop
        if max_pages is not None and page_num >= max_pages:
            break

        # Find "next" link and follow it
        soup = BeautifulSoup(resp.content, "html.parser")
        next_link = soup.select_one("li.next a")
        if not next_link:
            break
        next_href = next_link.get("href")
        url = urljoin(url, next_href)

        # Be polite
        time.sleep(random.uniform(0.4, 1.2))


def save_to_csv(rows: Iterator[Tuple[str, float, str]], output_file: str) -> int:
    count = 0
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "price", "rating"])
        for title, price, rating_word in rows:
            writer.writerow([title, f"{price:.2f}", rating_word])
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape book titles and prices from books.toscrape.com")
    parser.add_argument("-o", "--output", default="books_titles_prices.csv", help="Output CSV file")
    parser.add_argument("-p", "--pages", type=int, default=None, help="Maximum number of pages to crawl (default: all pages) Specify a number to limit the crawl.")
    args = parser.parse_args()

    rows = scrape_titles_prices(BASE_URL, max_pages=args.pages)
    total = save_to_csv(rows, args.output)

    print(f"Saved {total} books to {args.output}")


if __name__ == "__main__":
    main()
