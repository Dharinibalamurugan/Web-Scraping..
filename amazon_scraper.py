import requests
from bs4 import BeautifulSoup
import os, json, time
from urllib.parse import urljoin

BASE_URL = "https://www.amazon.in"
START_URLS = [
    "https://www.amazon.in/s?k=bambu+lab+3d+printer"
]

OUT_DIR = "data/amazon/printers"
os.makedirs(OUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-IN,en;q=0.9"
}

BAD_WORDS = [
    "filament", "pla", "petg", "abs", "resin",
    "nozzle", "plate", "sheet", "spool",
    "accessory"
]

def is_printer(name):
    n = name.lower()
    return "bambu" in n and "printer" in n and not any(b in n for b in BAD_WORDS)

print(" Searching Amazon...")

product_links = set()

for url in START_URLS:
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.select("a.a-link-normal.s-no-outline"):
        href = a.get("href")
        if not href or "/dp/" not in href:
            continue

        asin = href.split("/dp/")[1][:10].upper()
        product_links.add(f"{BASE_URL}/dp/{asin}")

print(f" Found {len(product_links)} product links")

for url in sorted(product_links):
    print(f"\n🖨 Scraping: {url}")
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    name = "N/A"
    price = "N/A"
    description = "N/A"

    title = soup.find("span", id="productTitle")
    if title:
        name = title.get_text(strip=True)

    if not is_printer(name):
        print(f" Skipped: {name}")
        continue

    price_tag = soup.select_one("span.a-price span.a-offscreen")
    if price_tag:
        price = price_tag.get_text(strip=True)

    bullets = soup.find("ul", id="feature-bullets")
    if bullets:
        description = bullets.get_text(" ", strip=True)

    asin = url.split("/dp/")[1]
    product_dir = os.path.join(OUT_DIR, asin)
    os.makedirs(product_dir, exist_ok=True)

    with open(os.path.join(product_dir, "product.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "name": name,
                "price": price,
                "description": description,
                "url": url,
                "source": "amazon"
            },
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"Saved: {name} | {price}")
    time.sleep(3)

print("\n AMAZON SIMPLE SCRAPING DONE")
