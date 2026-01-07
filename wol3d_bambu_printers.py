from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os, json, requests
from urllib.parse import urlparse

BASE_URL = "https://wol3d.com/product-category/brand/bambu-lab/3d-printer/"
OUT_DIR = "data/wol3d/printers"

os.makedirs(OUT_DIR, exist_ok=True)

PRINTER_KEYS = [
    "x1-carbon",
    "p1s",
    "p1p",
    "a1",
    "a1-mini",
    "3d-printer"
]

def is_bambu_printer(url: str) -> bool:
    u = url.lower()
    return (
        "/product/" in u
        and "bambu-lab" in u
        and "3d-printer" in u
        and any(k in u for k in PRINTER_KEYS)
    )

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    printer_links = set()
    page_no = 1

    while True:
        url = BASE_URL if page_no == 1 else f"{BASE_URL}page/{page_no}/"
        print(f"🔎 Scanning page {page_no}")

        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        anchors = page.locator("a")
        found = False

        for i in range(anchors.count()):
            href = anchors.nth(i).get_attribute("href")
            if not href:
                continue

            if is_bambu_printer(href):
                printer_links.add(href)
                found = True

        if not found:
            break

        page_no += 1

    print(f"\n Found {len(printer_links)} Bambu Lab printers")

    for url in sorted(printer_links):
        print("\n🖨️ Scraping:", url)

        page.goto(url, timeout=60000)
        page.wait_for_timeout(4000)

        try:
            name = page.locator("h1").inner_text().strip()
        except:
            continue

        try:
            price = page.locator("p.price").inner_text().strip()
        except:
            price = "N/A"

        try:
            desc = page.locator(
                "div.woocommerce-product-details__short-description"
            ).inner_text().strip()
        except:
            desc = ""

        slug = urlparse(url).path.strip("/").split("/")[-1]
        product_dir = os.path.join(OUT_DIR, slug)
        images_dir = os.path.join(product_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        with open(os.path.join(product_dir, "product.json"), "w", encoding="utf-8") as f:
            json.dump(
                {
                    "name": name,
                    "price": price,
                    "description": desc,
                    "url": url,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        soup = BeautifulSoup(page.content(), "html.parser")
        imgs = soup.find_all("img")

        seen = set()
        count = 0

        for img in imgs:
            if count >= 3:
                break

            src = img.get("src") or img.get("data-src")
            if not src:
                continue

            s = src.lower()
            if any(x in s for x in ["logo", "icon", "svg", "banner"]):
                continue
            if any(x in s for x in ["-150x", "-300x", "-100x"]):
                continue
            if s in seen:
                continue

            seen.add(s)

            try:
                data = requests.get(src, timeout=10).content
                with open(os.path.join(images_dir, f"img_{count}.jpg"), "wb") as f:
                    f.write(data)
                count += 1
            except:
                pass

        print("Saved:", name)

    browser.close()

print("\n DONE — ONLY BAMBU LAB 3D PRINTERS SCRAPED")
