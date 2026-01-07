import requests
from bs4 import BeautifulSoup
import os, json, time
from random import randint

BASE_URL = "https://www.amazon.in"
BASE_SEARCH = "https://www.amazon.in/s?k=bambu+lab+3d+printer"
MAX_PAGES = 5

OUT_DIR = "data/amazon/printers"
os.makedirs(OUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

BAD_WORDS = [
    "filament", "pla", "petg", "abs", "resin",
    "nozzle", "plate", "sheet", "spool",
    "accessory", "refill"
]

def is_printer(name: str) -> bool:
    n = name.lower()
    if "bambu" not in n:
        return False
    if "printer" not in n:
        return False
    return not any(b in n for b in BAD_WORDS)

def get_soup(url, retries=2):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=25)
            if r.status_code == 503:
                print(" 503 received, waiting and retrying...")
                time.sleep(randint(5, 8))
                continue
            r.raise_for_status()
            return BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(randint(5, 8))

print("Collecting Amazon product links...")

product_links = set()

for page in range(1, MAX_PAGES + 1):
    search_url = f"{BASE_SEARCH}&page={page}"
    print(f"➡ Page {page}")

    try:
        soup = get_soup(search_url)
    except:
        print(" Failed to load search page, skipping")
        continue

    for a in soup.select("a.a-link-normal[href*='/dp/']"):
        href = a.get("href")
        if not href:
            continue

        asin = href.split("/dp/")[1][:10].upper()
        product_links.add(f"{BASE_URL}/dp/{asin}")

    time.sleep(randint(4, 7))

print(f"\n Found {len(product_links)} product links")

for url in sorted(product_links):
    print(f"\n🖨 Scraping: {url}")

    try:
        soup = get_soup(url)
    except:
        print(" Failed to load product page")
        continue

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
    images_dir = os.path.join(product_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    imgs = soup.find_all("img")
    seen = set()
    count = 0

    for img in imgs:
        if count >= 3:
            break

        src = img.get("src")
        if not src:
            continue

        src_l = src.lower()
        if "sprite" in src_l or "icon" in src_l:
            continue
        if "images/i/" not in src_l:
            continue
        if src in seen:
            continue

        seen.add(src)

        try:
            img_data = requests.get(src, headers=HEADERS, timeout=10).content
            with open(os.path.join(images_dir, f"img_{count}.jpg"), "wb") as f:
                f.write(img_data)
            count += 1
        except:
            pass

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

    print(f" Saved: {name} | {price} | {count} images")
    time.sleep(randint(4, 7))

print("\n AMAZON SCRAPING COMPLETED")
