import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = "https://ideal3d.in"
START_URL = "https://ideal3d.in/collections/bambulab-printers"
OUT_DIR = "data/ideal3d/printers"

os.makedirs(OUT_DIR, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_soup(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        return BeautifulSoup(r.text, "html.parser")
    except:
        return None

def is_bambu_printer(title: str) -> bool:
    t = title.lower()
    return "bambu lab" in t and "printer" in t

print(" Scanning Ideal3D Bambu Lab collection...")

product_links = set()
page = 1

while True:
    url = START_URL if page == 1 else f"{START_URL}?page={page}"
    print(f"➡ Page {page}")

    soup = get_soup(url)
    if not soup:
        break

    cards = soup.select("a.full-unstyled-link[href*='/products/']")

    if not cards:
        break

    before = len(product_links)

    for a in cards:
        href = a.get("href")
        if href:
            product_links.add(urljoin(BASE_URL, href))

    if len(product_links) == before:
        break

    page += 1

print(f"\n Found {len(product_links)} collection products")

for url in sorted(product_links):
    print("\n🖨 Scraping:", url)

    soup = get_soup(url)
    if not soup:
        print(" Skipped (404):", url)
        continue

    h1 = soup.find("h1")
    if not h1:
        continue

    title = h1.get_text(strip=True)

    if not is_bambu_printer(title):
        print(" Skipped:", title)
        continue

    price_tag = soup.select_one(".price, .price-item")
    price = price_tag.get_text(strip=True) if price_tag else "N/A"

    desc_tag = soup.select_one(".product__description, .rte")
    description = desc_tag.get_text(" ", strip=True) if desc_tag else ""

    slug = urlparse(url).path.split("/")[-1]
    product_dir = os.path.join(OUT_DIR, slug)
    images_dir = os.path.join(product_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    with open(os.path.join(product_dir, "product.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "name": title,
                "price": price,
                "description": description,
                "url": url,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    imgs = soup.find_all("img")
    seen = set()
    count = 0

    for img in imgs:
        if count >= 3:
            break

        src = img.get("src") or img.get("data-src")
        if not src:
            continue

        src = urljoin(BASE_URL, src)
        s = src.lower()

        if any(x in s for x in ["logo", "icon", "badge", "exclusive"]):
            continue
        if any(x in s for x in ["-100x", "-150x", "-300x"]):
            continue
        if s in seen:
            continue

        seen.add(s)

        try:
            data = requests.get(src, headers=HEADERS, timeout=10).content
            with open(os.path.join(images_dir, f"img_{count}.jpg"), "wb") as f:
                f.write(data)
            count += 1
        except:
            pass

    print(" Saved:", title)

print("\n IDEAL3D SCRAPING DONE — ONLY BAMBU LAB PRINTERS")
