import os
import json
import pandas as pd

BASE_DIR = "data/wol3d/printers"
OUTPUT_FILE = "data/wol3d/wol3d_products.xlsx"

rows = []

if not os.path.exists(BASE_DIR):
    print(f" Wol3D printers folder not found: {BASE_DIR}")
    exit()

for folder in os.listdir(BASE_DIR):
    product_dir = os.path.join(BASE_DIR, folder)
    product_file = os.path.join(product_dir, "product.json")
    images_dir = os.path.join(product_dir, "images")

    if not os.path.isfile(product_file):
        continue

    try:
        with open(product_file, "r", encoding="utf-8") as f:
            data = json.load(f)

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
            "images": ", ".join(images),
            "source": "wol3d"
        })

    except Exception as e:
        print(f"Error reading {folder}: {e}")

if not rows:
    print(" No Wol3D products found")
else:
    df = pd.DataFrame(rows)
    df.to_excel(OUTPUT_FILE, index=False)
    print(f" Wol3D Excel created: {OUTPUT_FILE}")
