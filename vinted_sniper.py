import requests
import time
import hashlib
import os

# === CONFIG ===
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SEARCH_KEYWORD = "Nike Dunks"
MAX_PRICE = 40
REFRESH_INTERVAL = 3  # seconds
VINTED_DOMAIN = "vinted.co.uk"  # change if needed

# === TRACK SEEN ITEMS TO AVOID DUPLICATES ===
seen_ids = set()

def generate_item_hash(item):
    return hashlib.md5(str(item["id"]).encode()).hexdigest()

def send_to_discord(item):
    if not WEBHOOK_URL:
        print("No webhook URL set!")
        return

    title = item["title"]
    price = item["price"]
    url = f"https://www.{VINTED_DOMAIN}/items/{item['id']}"
    image_url = item["photo"]["url"]

    embed = {
        "title": f"{title} - £{price}",
        "url": url,
        "color": 0x00ff90,
        "thumbnail": {"url": image_url},
        "fields": [
            {"name": "Size", "value": item.get("size_title", "N/A"), "inline": True},
            {"name": "Brand", "value": item.get("brand_title", "N/A"), "inline": True},
        ]
    }

    payload = {
        "username": "Vinted Sniper",
        "embeds": [embed]
    }

    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code != 204:
        print("Failed to send Discord message:", response.status_code, response.text)

def fetch_items():
    url = f"https://www.{VINTED_DOMAIN}/api/v2/catalog/items"
    params = {
        "search_text": SEARCH_KEYWORD,
        "price_to": MAX_PRICE,
        "order": "newest_first",
        "currency": "GBP",
        "per_page": 10
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        print("Error fetching items:", response.status_code)
        return []

def main():
    print(f"Sniper started! Watching for '{SEARCH_KEYWORD}' under £{MAX_PRICE}...")
    while True:
        try:
            items = fetch_items()
            for item in items:
                item_hash = generate_item_hash(item)
                if item_hash not in seen_ids:
                    seen_ids.add(item_hash)
                    send_to_discord(item)
        except Exception as e:
            print("Error:", e)

        time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    main()
