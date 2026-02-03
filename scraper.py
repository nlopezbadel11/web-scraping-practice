import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import pandas as pd

# This script downloads all pages from https://books.toscrape.com,
# extracts book titles, prices, and star ratings, and saves them to books.csv.


def scrape_all_pages(base_url: str, total_pages: int = 50) -> pd.DataFrame:
    """Scrape book data from all pages and return a DataFrame.

    Args:
        base_url: Base site URL (e.g., 'https://books.toscrape.com')
        total_pages: Number of paginated pages to attempt (default 50)
    """
    # Create a requests Session with retries for robustness
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.3, status_forcelist=(429, 500, 502, 503, 504))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; Bot/0.1)'})

    data = []  # list to collect book dicts

    # Mapping from textual rating to numeric value
    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}

    for page_num in range(1, total_pages + 1):
        # Build the URL for each page
        if page_num == 1:
            url = f"{base_url}/index.html"
        else:
            url = f"{base_url}/catalogue/page-{page_num}.html"

        try:
            print(f"Downloading page {page_num} -> {url}")
            resp = session.get(url, timeout=10)
            resp.raise_for_status()

            # Parse page HTML
            soup = BeautifulSoup(resp.content, 'html.parser')
            books = soup.find_all('article', class_='product_pod')

            # If no books found, assume we've reached the end and stop early
            if not books:
                print(f"No books found on page {page_num}; stopping early.")
                break

            # Extract data for each book on the page
            for book in books:
                try:
                    title = book.h3.a['title']
                    price_text = book.find('p', class_='price_color').get_text(strip=True)
                    price = float(price_text.replace('£', ''))
                    rating_word = book.find('p', class_='star-rating')['class'][1]
                    rating_value = rating_map.get(rating_word, None)

                    data.append({
                        'title': title,
                        'price': price,
                        'rating': rating_word,
                        'rating_value': rating_value,
                        'page': page_num,
                    })
                except (AttributeError, KeyError, ValueError) as e:
                    print(f"Error parsing a book on page {page_num}: {e}")
                    continue

        except requests.exceptions.RequestException as e:
            print(f"Request error on page {page_num}: {e} -- skipping page")
            continue

        # Be polite and wait a short random interval between requests
        time.sleep(random.uniform(0.5, 1.5))

    # Convert to DataFrame
    df = pd.DataFrame(data)
    return df


if __name__ == '__main__':
    BASE_URL = 'https://books.toscrape.com'

    print('Starting multi-page scrape of books.toscrape.com...')
    df_all = scrape_all_pages(BASE_URL, total_pages=50)

    output_file = 'books.csv'
    df_all.to_csv(output_file, index=False)

    print(f'Finished. Saved {len(df_all)} books to {output_file}')
    print('\nFirst 5 rows:')
    print(df_all.head())

