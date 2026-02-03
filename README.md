# web-scraping-practice ✅

A small practice repository demonstrating how to scrape book titles and prices from `books.toscrape.com` and save them to a CSV file.

## 🔧 Files

- `scraper.py` — an existing multi-field scraper (title, price, rating) that saves to `books.csv`.
- `scrape_titles_prices.py` — a focused script that extracts **title**, **price**, and **rating** and saves to `books_titles_prices.csv` by default.
- `requirements.txt` — minimal dependencies (`requests`, `beautifulsoup4`).

---

## Usage 💡

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the focused scraper (default crawls the whole site by following pagination and saves to `books_titles_prices.csv`):

```bash
python scrape_titles_prices.py
```

Output columns: `title`, `price`, `rating`.

Tip: Use `-p N` to limit the crawl to the first N pages (e.g., `-p 1` for just the first page).

Customize output file and number of pages:

```bash
python scrape_titles_prices.py -o my_books.csv -p 20
```

> Note: The site is paginated (up to 50 pages). The scraper stops early if it reaches a page with no books.

---

## License

This project is for practice and learning. Use responsibly and be polite to websites (rate-limit your requests).
