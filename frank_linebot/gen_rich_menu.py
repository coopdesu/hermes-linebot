#!/usr/bin/env python3
"""Frank 愛車顧問 Rich Menu — full-bleed CSL photo + 3 cells."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

W, H = 2500, 1686
CELL_W = W // 3                  # 833
CELL_BAND_TOP = 1100             # where cells sit (on dark road area)
CELL_BAND_H = H - CELL_BAND_TOP  # 586

CSL_SRC = Path("/tmp/csl_fullh.png")   # 2995 x 1686
OUT = Path(__file__).parent / "rich_menu.jpg"

FONT_ZH = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FONT_EN = "/System/Library/Fonts/Supplemental/Arial.ttf"

ACCENT = "#C9A96E"   # champagne gold
CREAM  = "#F3EEE4"

CELLS = [
    ("APT",  "預約試乘", "TEST DRIVE"),
    ("VIEW", "預約賞車", "VIEWING"),
    ("TEL",  "聯絡顧問", "CONTACT"),
]


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def draw_spaced(draw, text, font, fill, cx, y, spacing=14):
    widths = [draw.textbbox((0, 0), c, font=font)[2] - draw.textbbox((0, 0), c, font=font)[0]
              for c in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total // 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + spacing


def make_background():
    """Crop 2995x1686 photo to 2500x1686 (center horizontal)."""
    src = Image.open(CSL_SRC).convert("RGB")
    sw, sh = src.size
    left = (sw - W) // 2
    bg = src.crop((left, 0, left + W, H))
    return bg


def main():
    img = make_background().convert("RGBA")

    # Subtle gradient darkening on bottom band for text legibility
    # (keeps photo visible but darkens enough for gold/cream text to pop)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    fade_start = CELL_BAND_TOP - 140
    for y in range(fade_start, H):
        # Ramp from 0 alpha at fade_start to ~130 at CELL_BAND_TOP, hold
        if y < CELL_BAND_TOP:
            a = int(130 * (y - fade_start) / (CELL_BAND_TOP - fade_start))
        else:
            a = 140
        od.rectangle([0, y, W, y + 1], fill=(0, 0, 0, a))
    img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)

    # Brand lockup — top-left on sky area (light side, use dark text? no, gold works on sky too)
    f_brand_en = ImageFont.truetype(FONT_EN, 54)
    f_brand_zh = ImageFont.truetype(FONT_ZH, 60)
    # Soft shadow for legibility on variable sky
    shadow = (0, 0, 0, 160)
    for dx, dy in [(2, 2)]:
        draw.text((90 + dx, 80 + dy), "FRANK", font=f_brand_en, fill=shadow)
        draw.text((90 + dx, 145 + dy), "愛車顧問", font=f_brand_zh, fill=shadow)
    draw.text((90, 80), "FRANK", font=f_brand_en, fill=hex2rgb(ACCENT))
    draw.text((90, 145), "愛車顧問", font=f_brand_zh, fill=hex2rgb(CREAM))
    draw.rectangle([90, 230, 260, 232], fill=hex2rgb(ACCENT))

    # Cells — no bg, no frame, just icon + text
    f_zh = ImageFont.truetype(FONT_ZH, 82)
    f_en = ImageFont.truetype(FONT_EN, 36)
    f_ico = ImageFont.truetype(FONT_EN, 30)

    for idx, (icon, zh, en) in enumerate(CELLS):
        x0 = idx * CELL_W
        cx = x0 + CELL_W // 2
        cy = CELL_BAND_TOP + CELL_BAND_H // 2

        # Circle icon
        r = 60
        iy = cy - 145
        draw.ellipse([cx - r, iy - r, cx + r, iy + r],
                     outline=hex2rgb(ACCENT), width=3)
        bb = draw.textbbox((0, 0), icon, font=f_ico)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        draw.text((cx - tw // 2, iy - th // 2 - 2), icon,
                  font=f_ico, fill=hex2rgb(ACCENT))

        # Chinese with drop shadow
        for dx, dy in [(2, 2)]:
            draw_spaced(draw, zh, f_zh, (0, 0, 0, 180), cx + dx, cy - 25 + dy, spacing=18)
        draw_spaced(draw, zh, f_zh, hex2rgb(CREAM), cx, cy - 25, spacing=18)

        # English sublabel
        draw_spaced(draw, en, f_en, hex2rgb(ACCENT), cx, cy + 80, spacing=10)

        # Underline
        draw.rectangle([cx - 38, cy + 138, cx + 38, cy + 140], fill=hex2rgb(ACCENT))

    # Hairline vertical dividers between cells (subtle, gold at 35% alpha)
    div = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(div)
    for i in (1, 2):
        x = i * CELL_W
        dd.rectangle([x - 1, CELL_BAND_TOP + 60, x + 1, H - 60],
                     fill=(*hex2rgb(ACCENT), 90))
    img = Image.alpha_composite(img, div)

    img.convert("RGB").save(OUT, "JPEG", quality=88, optimize=True)
    size_kb = OUT.stat().st_size / 1024
    print(f"Saved: {OUT} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
