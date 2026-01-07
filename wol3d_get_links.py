from playwright.sync_api import sync_playwright
import os

OUT_FILE = "data/wol3d/wol3d_links.txt"
BASE_URL = "https://wol3d.com/product-category/brand/bambu-lab/3d-printer/"

os.makedirs("data/wol3d", exist_ok=True)

BAMBU_PRINTER_KEYWORDS = [
    "x1-carbon",
    "p1s",
    "p1p",
    "a1",
    "a1-mini",
    "3d-printer"
]

def is_bambu_printer(url: str) -> bool:
    h = url.lower()
    return (
        "/product/" in h
        and "bambu-lab" in h
        and "3d-printer" in h
        and any(k in h for k in BAMBU_PRINTER_KEYWORDS)
    )

links = set()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page_no = 1

    while True:
        url = BASE_URL if page_no == 1 else f"{BASE_URL}page/{page_no}/"
        print(f" Scanning page {page_no}: {url}")

        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        anchors = page.locator("a")
        found_any = False

        for i in range(anchors.count()):
            href = anchors.nth(i).get_attribute("href")
            if not href:
                continue

            if is_bambu_printer(href):
                links.add(href)
                found_any = True

        if not found_any:
            break

        page_no += 1

    browser.close()

with open(OUT_FILE, "w", encoding="utf-8") as f:
    for l in sorted(links):
        f.write(l + "\n")

print("\n TOTAL BAMBU LAB PRINTER LINKS:", len(links))

