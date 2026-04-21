#!/usr/bin/env python3
"""Upload Frank 愛車顧問 Rich Menu — single menu, 3 tap areas."""
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

BASE_DIR = Path(__file__).parent
IMG_PATH = BASE_DIR / "rich_menu.jpg"

W, H = 2500, 1686
CELL_W = W // 3                   # 833
CELL_BAND_TOP = 1100
CELL_BAND_H = H - CELL_BAND_TOP   # 586

PHONE = "0910693710"

MENU_DEF = {
    "size": {"width": W, "height": H},
    "selected": True,
    "name": "Frank 愛車顧問",
    "chatBarText": "開啟選單",
    "areas": [
        # Banner area → no action (tap does nothing; whole banner is photo)
        # Cell 1: 預約試乘
        {"bounds": {"x": 0, "y": CELL_BAND_TOP, "width": CELL_W, "height": CELL_BAND_H},
         "action": {"type": "message", "text": "預約試乘"}},
        # Cell 2: 預約賞車
        {"bounds": {"x": CELL_W, "y": CELL_BAND_TOP, "width": CELL_W, "height": CELL_BAND_H},
         "action": {"type": "message", "text": "預約賞車"}},
        # Cell 3: 聯絡顧問 → tel: URI, jumps to phone dialer
        {"bounds": {"x": 2 * CELL_W, "y": CELL_BAND_TOP, "width": W - 2 * CELL_W, "height": CELL_BAND_H},
         "action": {"type": "uri", "uri": f"tel:{PHONE}"}},
    ],
}


def delete_all_menus():
    r = requests.get("https://api.line.me/v2/bot/richmenu/list", headers=HEADERS)
    r.raise_for_status()
    for m in r.json().get("richmenus", []):
        mid = m["richMenuId"]
        requests.delete(f"https://api.line.me/v2/bot/richmenu/{mid}", headers=HEADERS)
        print(f"  Deleted: {mid}")


def create_menu(definition):
    r = requests.post(
        "https://api.line.me/v2/bot/richmenu",
        headers={**HEADERS, "Content-Type": "application/json"},
        data=json.dumps(definition),
    )
    r.raise_for_status()
    mid = r.json()["richMenuId"]
    print(f"  Created: {mid}")
    return mid


def upload_image(menu_id, img_path):
    content_type = "image/jpeg" if img_path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    with open(img_path, "rb") as f:
        r = requests.post(
            f"https://api-data.line.me/v2/bot/richmenu/{menu_id}/content",
            headers={**HEADERS, "Content-Type": content_type},
            data=f,
        )
    r.raise_for_status()
    print(f"  Image uploaded ({img_path.name})")


def set_default(menu_id):
    r = requests.post(
        f"https://api.line.me/v2/bot/user/all/richmenu/{menu_id}",
        headers=HEADERS,
    )
    r.raise_for_status()
    print(f"  Set as default")


if __name__ == "__main__":
    print("1. Deleting old menus...")
    delete_all_menus()

    print("2. Creating Frank menu...")
    mid = create_menu(MENU_DEF)
    upload_image(mid, IMG_PATH)

    print("3. Setting as default...")
    set_default(mid)

    print(f"\nDone! Menu ID: {mid}")
