from playwright.sync_api import sync_playwright
import os

URL = "https://robu.in/brand/bambu-lab/"
OUTPUT_FILE = "robu_links.txt"

product_links = set()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(URL)
    page.wait_for_timeout(8000)

    links = page.query_selector_all("a")

    for a in links:
        href = a.get_attribute("href")
        if href and "/product/" in href:
            if href.startswith("/"):
                href = "https://robu.in" + href
            product_links.add(href)

    browser.close()

print("Total product links found:", len(product_links))

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for link in product_links:
        f.write(link + "\n")

print("Saved to robu_links.txt")
