from playwright.sync_api import sync_playwright
import os
import json
import requests
from urllib.parse import urlparse

BASE_DIR = "data/robu"
LINKS_FILE = os.path.join(os.path.dirname(__file__), "robu_links.txt")

os.makedirs(BASE_DIR, exist_ok=True)

def is_3d_printer(name: str) -> bool:
    name = name.lower()

    include_keywords = ["3d printer", "printer", "bambu"]
    exclude_keywords = [
        "filament",
        "nozzle",
        "plate",
        "service",
        "refill",
        "spare",
        "accessory"
    ]

    return any(k in name for k in include_keywords) and not any(
        k in name for k in exclude_keywords
    )
with open(LINKS_FILE, "r", encoding="utf-8") as f:
    product_links = [line.strip() for line in f if line.strip()]

print("Total product links:", len(product_links))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    for url in product_links:
        print("\nScraping:", url)
        page.goto(url)
        page.wait_for_timeout(5000)

        try:
            name = page.locator("h1").inner_text().strip()
            if not is_3d_printer(name):
                print("Skipped (not a printer):", name)
                continue
        except:
            print("Failed to get name")
            continue

        try:
            price = page.locator("p.price bdi").first.inner_text().strip()
        except:
            price = "N/A"

        try:
            description = page.locator(
                "div.woocommerce-product-details__short-description"
            ).inner_text().strip()
        except:
            description = ""

        slug = urlparse(url).path.strip("/").split("/")[-1]
        product_dir = os.path.join(BASE_DIR, slug)
        images_dir = os.path.join(product_dir, "images")

        os.makedirs(images_dir, exist_ok=True)

        product_data = {
            "name": name,
            "price": price,
            "description": description,
            "url": url
        }

        with open(os.path.join(product_dir, "product.json"), "w", encoding="utf-8") as f:
            json.dump(product_data, f, indent=2, ensure_ascii=False)

        images = page.locator("img.wp-post-image, img.attachment-woocommerce_single")
        count = images.count()
        print("Images found:", count)
        for i in range(count):
            try:
                img = images.nth(i)
                img.scroll_into_view_if_needed()
                img.screenshot(path=os.path.join(images_dir, f"img_{i+1}.png"))
            except:
                pass



        print(" Saved:", name)

    browser.close()

print("\n ROBU scraping completed successfully!")
