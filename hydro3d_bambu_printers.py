from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os, json, requests
from urllib.parse import urlparse

START_URL = "https://www.hydrotech3dchennai.com/category/3d-printers-bambulab"
OUT_DIR = "data/hydro3d/printers"

os.makedirs(OUT_DIR, exist_ok=True)

def is_bambu_printer(url: str) -> bool:
    return "/product-page/" in url and "bambu-lab" in url.lower()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(START_URL, timeout=60000)
    page.wait_for_timeout(5000)

    product_links = set()
    anchors = page.locator("a")

    for i in range(anchors.count()):
        href = anchors.nth(i).get_attribute("href")
        if href and is_bambu_printer(href):
            product_links.add(href)

    print(f"Found {len(product_links)} Hydro3D Bambu products")

    for url in sorted(product_links):
        print("\n🖨 Scraping:", url)

        page.goto(url, timeout=60000)
        page.wait_for_timeout(4000)

        try:
            name = page.locator("h1").inner_text().strip()
        except:
            continue

        try:
            price = page.locator(
                'span[data-hook="formatted-primary-price"]'
            ).inner_text().strip()
        except:
            price = "N/A"

        try:
            description = page.locator(
                'div[data-hook="product-description"]'
            ).inner_text().strip()
        except:
            description = ""

        slug = urlparse(url).path.strip("/").split("/")[-1]
        product_dir = os.path.join(OUT_DIR, slug)
        images_dir = os.path.join(product_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        with open(os.path.join(product_dir, "product.json"), "w", encoding="utf-8") as f:
            json.dump(
                {
                    "name": name,
                    "price": price,
                    "description": description,
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
            if any(x in s for x in ["logo", "icon", "badge"]):
                continue
            if any(x in s for x in ["-100x", "-150x", "-300x"]):
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

        print(" Saved:", name)

    browser.close()

print("\n HYDRO3D SCRAPING DONE — PRICE & DESCRIPTION FIXED")
