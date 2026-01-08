import os
import json
import pandas as pd

BASE_DIR = os.path.join(
    os.path.dirname(__file__),
    "data",
    "amazon",
    "printers"
)

OUTPUT_FILE = "amazon_products.xlsx"


rows = []

if not os.path.exists(BASE_DIR):
    print(" Amazon printers folder not found:", BASE_DIR)
    exit()

for folder in os.listdir(BASE_DIR):
    product_dir = os.path.join(BASE_DIR, folder)
    product_file = os.path.join(product_dir, "product.json")

    if not os.path.isfile(product_file):
        continue

    try:
        with open(product_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        images_dir = os.path.join(product_dir, "images")
        images = []

        if os.path.exists(images_dir):
            images = [
                os.path.join(images_dir, img)
                for img in os.listdir(images_dir)
                if img.lower().endswith((".jpg", ".png", ".jpeg"))
            ]

        rows.append({
            "name": data.get("name", ""),
            "price": data.get("price", "N/A"),
            "description": data.get("description", ""),
            "url": data.get("url", ""),
            "images": ", ".join(images)
        })

    except Exception as e:
        print(f" Error reading {product_file}: {e}")

if not rows:
    print(" No Amazon products found")
else:
    df = pd.DataFrame(rows)
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Amazon Excel created: {OUTPUT_FILE}")
