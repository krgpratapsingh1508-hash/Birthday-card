"""
🎂 Birthday Studio  —  Admin panel + User panel
-------------------------------------------------
* Har user ka apna ID (login) — apna Birthday Card, Birthday Album aur Birthday Video banata hai.
* Admin ID me sab users ki jankari, unki creations, birthdays, export, reset password, etc.

Run:  streamlit run app.py
Pehla admin login:  admin / admin123   (turant badal lena — Admin > Settings)
"""
import csv
import hashlib
import hmac
import io
import math
import os
import random
import re
import secrets
import shutil
import sqlite3
import subprocess
import tempfile
import urllib.parse
import wave
import zipfile
from datetime import date, datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

try:  # engines headless bhi chal sakein (testing) — UI ke liye streamlit chahiye
    import streamlit as st
except ImportError:  # pragma: no cover
    st = None

# =====================================================================
# 1. THEMES
# =====================================================================
THEMES = {
    "👑 Royal Purple": dict(
        bg=("#2b0a5e", "#7c3aed"), title="#fde68a", text="#f5f3ff", accent="#fbbf24",
        ring="#ffffff", glow="#c4b5fd", badge_text="#3b0764",
        balloons=["#f472b6", "#fbbf24", "#60a5fa", "#34d399", "#fb7185", "#a78bfa"],
        confetti=["#fbbf24", "#f472b6", "#60a5fa", "#ffffff", "#34d399"],
    ),
    "🌸 Rose Pink": dict(
        bg=("#fff1f2", "#fda4af"), title="#be123c", text="#881337", accent="#e11d48",
        ring="#ffffff", glow="#ffffff", badge_text="#ffffff",
        balloons=["#e11d48", "#f97316", "#a855f7", "#ec4899", "#f43f5e", "#fb923c"],
        confetti=["#e11d48", "#f59e0b", "#a855f7", "#ffffff", "#ec4899"],
    ),
    "✨ Midnight Gold": dict(
        bg=("#050816", "#1e2a5a"), title="#fcd34d", text="#e2e8f0", accent="#f5c542",
        ring="#fde68a", glow="#f5c542", badge_text="#0b1020",
        balloons=["#f5c542", "#38bdf8", "#f472b6", "#fbbf24", "#818cf8", "#34d399"],
        confetti=["#f5c542", "#ffffff", "#38bdf8", "#f472b6", "#818cf8"],
    ),
    "🌿 Mint Fresh": dict(
        bg=("#ecfeff", "#6ee7b7"), title="#047857", text="#064e3b", accent="#059669",
        ring="#ffffff", glow="#ffffff", badge_text="#ffffff",
        balloons=["#f97316", "#facc15", "#3b82f6", "#ec4899", "#10b981", "#8b5cf6"],
        confetti=["#f97316", "#facc15", "#3b82f6", "#ec4899", "#ffffff"],
    ),
}

WISHES = {
    "Dil se (Hinglish)": "Tumhara har sapna sach ho aur ye saal khushiyon se bhara ho. Janamdin mubarak!",
    "Classic": "May your special day be filled with love, laughter and beautiful memories.",
    "Short & sweet": "Another year older, another year more amazing. Have the best day ever!",
    "Blessings": "Wishing you good health, endless happiness and success in everything you do. Stay blessed always!",
    "Funny": "You're not old, you're just a classic edition. Eat extra cake today!",
    "✍️ Apna khud ka likhein": "",
}

W, H, S = 1080, 1440, 2  # card size (px) and supersampling factor (anti-aliasing)


# =====================================================================
# 2. CARD ENGINE (Pillow)
# =====================================================================
FONT_DIRS = [Path(__file__).parent / "fonts", Path("/usr/share/fonts/truetype/dejavu"),
             Path("/usr/share/fonts/truetype/liberation"), Path("/usr/share/fonts/truetype/freefont"),
             Path("/usr/share/fonts/truetype/noto"), Path("/usr/share/fonts/opentype/noto"),
             Path("/Library/Fonts"), Path("C:/Windows/Fonts")]

FONT_FILES = {
    "title": ["PlayfairDisplay-BoldItalic.ttf", "PlayfairDisplay-Bold.ttf", "DejaVuSerif-BoldItalic.ttf",
              "DejaVuSerif-Bold.ttf", "georgiaz.ttf", "LiberationSerif-BoldItalic.ttf"],
    "name": ["PlayfairDisplay-Bold.ttf", "DejaVuSerif-Bold.ttf", "georgiab.ttf", "LiberationSerif-Bold.ttf"],
    "body": ["DejaVuSerif-Italic.ttf", "LiberationSerif-Italic.ttf", "georgiai.ttf", "DejaVuSans.ttf"],
    "sans": ["Poppins-SemiBold.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "arialbd.ttf"],
    "deva": ["NotoSansDevanagari-Bold.ttf", "FreeSerifBold.ttf", "Nirmala.ttf", "mangal.ttf"],
}
_font_cache = {}


def get_font(role, size):
    size = int(size)
    key = (role, size)
    if key in _font_cache:
        return _font_cache[key]
    font = None
    for fname in FONT_FILES[role]:
        for d in FONT_DIRS:
            p = d / fname
            if p.exists():
                try:
                    font = ImageFont.truetype(str(p), size)
                    break
                except Exception:
                    pass
        if font:
            break
    if font is None:
        font = ImageFont.load_default(size)
    _font_cache[key] = font
    return font


def has_devanagari(text):
    return bool(re.search(r"[\u0900-\u097F]", text or ""))


def pick_role(role, text):
    return "deva" if has_devanagari(text) else role


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def s(v):
    return int(round(v * S))


def gradient(size, c1, c2):
    grad = Image.linear_gradient("L").resize(size)  # black(top) -> white(bottom)
    return Image.composite(Image.new("RGB", size, hex_rgb(c2)), Image.new("RGB", size, hex_rgb(c1)), grad)


def fit_font(draw, text, role, start, max_w, min_size=28):
    size = start
    while size > min_size:
        f = get_font(role, s(size))
        if draw.textlength(text, font=f) <= s(max_w):
            return f, size
        size -= 4
    return get_font(role, s(min_size)), min_size


def wrap(draw, text, font, max_w):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split():
            t = (cur + " " + word).strip()
            if draw.textlength(t, font=font) <= s(max_w) or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def spaced_text(draw, cx, cy, text, font, fill, spacing):
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, cy), ch, font=font, fill=fill, anchor="lm")
        x += w + spacing


def sparkle(d, cx, cy, r, fill):
    pts = []
    for i in range(8):
        ang = math.pi / 4 * i - math.pi / 2
        rad = r if i % 2 == 0 else r * 0.28
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=fill)


def balloon(d, cx, cy, r, color):
    c = hex_rgb(color)
    rx, ry = r, r * 1.22
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=c + (255,))
    # soft shade on the lower right + highlight on the upper left
    d.pieslice([cx - rx, cy - ry, cx + rx, cy + ry], 20, 110, fill=(0, 0, 0, 38))
    d.ellipse([cx - rx * 0.55, cy - ry * 0.68, cx - rx * 0.12, cy - ry * 0.28], fill=(255, 255, 255, 120))
    # knot
    ky = cy + ry
    d.polygon([(cx, ky - s(2)), (cx - r * 0.13, ky + r * 0.2), (cx + r * 0.13, ky + r * 0.2)], fill=c + (255,))


def balloon_string(d, x0, y0, x1, y1, color=(255, 255, 255, 170), width=3):
    pts = []
    for i in range(25):
        t = i / 24
        pts.append((x0 + (x1 - x0) * t + math.sin(t * math.pi * 2) * s(10) * (1 - t), y0 + (y1 - y0) * t))
    d.line(pts, fill=color, width=s(width), joint="curve")


def balloon_cluster(d, anchor, specs, colors, mirror=False):
    ax, ay = anchor
    for i, (dx, dy, r) in enumerate(specs):
        x = ax + (-dx if mirror else dx)
        y = ay + dy
        rr = s(r)
        balloon_string(d, s(x), s(y) + rr * 1.22 + rr * 0.2, s(ax), s(ay))
        balloon(d, s(x), s(y), rr, colors[i % len(colors)])


def bunting(d, colors):
    n = 14
    pts = [(W * i / n, 34 + 30 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    d.line([(s(x), s(y)) for x, y in pts], fill=(255, 255, 255, 200), width=s(3))
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        mx = (x0 + x1) / 2
        d.polygon([(s(x0 + 6), s(y0)), (s(x1 - 6), s(y1)), (s(mx), s((y0 + y1) / 2 + 62))],
                  fill=hex_rgb(colors[i % len(colors)]) + (255,))


def confetti(d, rng, colors, keep_out, n=150):
    for _ in range(n):
        x, y = rng.uniform(10, W - 10), rng.uniform(100, H - 20)
        if math.hypot(x - keep_out[0], y - keep_out[1]) < keep_out[2]:
            continue
        col = hex_rgb(rng.choice(colors)) + (rng.randint(130, 230),)
        sz = rng.uniform(5, 13)
        if rng.random() < 0.5:
            d.ellipse([s(x - sz / 2), s(y - sz / 2), s(x + sz / 2), s(y + sz / 2)], fill=col)
        else:
            ang = rng.uniform(0, math.pi)
            dx, dy = math.cos(ang) * sz, math.sin(ang) * sz
            d.line([(s(x - dx), s(y - dy)), (s(x + dx), s(y + dy))], fill=col, width=s(4))


def circular_photo(photo_bytes, diameter, focus_y):
    img = Image.open(io.BytesIO(photo_bytes))
    img = ImageOps.exif_transpose(img).convert("RGB")
    img = ImageOps.fit(img, (diameter, diameter), Image.Resampling.LANCZOS, centering=(0.5, focus_y))
    mask = Image.new("L", (diameter * 4, diameter * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, diameter * 4 - 1, diameter * 4 - 1), fill=255)
    mask = mask.resize((diameter, diameter), Image.Resampling.LANCZOS)
    img.putalpha(mask)
    return img


def render_card(theme_name, name, age, show_age, relation, wish, sender, photo_bytes, focus_y, seed):
    th = THEMES[theme_name]
    rng = random.Random(seed)

    img = gradient((W * S, H * S), *th["bg"])
    d = ImageDraw.Draw(img, "RGBA")

    photo_c = (540, 575)
    photo_r = 205

    # soft glow behind the photo
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gr = s(photo_r + 70)
    gd.ellipse([s(photo_c[0]) - gr, s(photo_c[1]) - gr, s(photo_c[0]) + gr, s(photo_c[1]) + gr],
               fill=hex_rgb(th["glow"]) + (150,))
    glow = glow.filter(ImageFilter.GaussianBlur(s(45)))
    img.paste(glow, (0, 0), glow)
    d = ImageDraw.Draw(img, "RGBA")

    # decorations
    confetti(d, rng, th["confetti"], (photo_c[0], photo_c[1], photo_r + 40))
    bunting(d, th["balloons"])
    specs = [(0, 0, 66), (-62, 100, 58), (66, 108, 56)]
    balloon_cluster(d, (140, 820), [(x, y - 250, r) for x, y, r in specs], th["balloons"])
    balloon_cluster(d, (940, 820), [(x, y - 250, r) for x, y, r in specs], th["balloons"][::-1], mirror=True)
    for (x, y, r) in [(300, 330, 20), (800, 345, 24), (250, 790, 16), (840, 800, 18), (960, 150, 14), (110, 160, 16)]:
        sparkle(d, s(x), s(y), s(r), hex_rgb(th["accent"]) + (230,))

    # heading
    f_tag = get_font("sans", s(26))
    spaced_text(d, s(540), s(128), "W I S H I N G   Y O U   A", f_tag, hex_rgb(th["accent"]) + (255,), s(2))
    f_title, _ = fit_font(d, "Happy Birthday", "title", 128, 900)
    d.text((s(540) + s(3), s(215) + s(4)), "Happy Birthday", font=f_title, fill=(0, 0, 0, 70), anchor="mm")
    d.text((s(540), s(215)), "Happy Birthday", font=f_title, fill=hex_rgb(th["title"]), anchor="mm")

    # photo with double ring
    cx, cy, r = s(photo_c[0]), s(photo_c[1]), s(photo_r)
    d.ellipse([cx - r - s(26), cy - r - s(26), cx + r + s(26), cy + r + s(26)], outline=hex_rgb(th["accent"]) + (255,), width=s(8))
    d.ellipse([cx - r - s(10), cy - r - s(10), cx + r + s(10), cy + r + s(10)], fill=hex_rgb(th["ring"]) + (255,))
    if photo_bytes:
        pic = circular_photo(photo_bytes, r * 2, focus_y)
        img.paste(pic, (cx - r, cy - r), pic)
    else:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hex_rgb(th["accent"]) + (255,))
        initial = (name.strip()[:1] or "★").upper()
        d.text((cx, cy), initial, font=get_font(pick_role("title", initial), s(260)),
               fill=hex_rgb(th["badge_text"]), anchor="mm")
    d = ImageDraw.Draw(img, "RGBA")

    # age badge
    if show_age and age:
        bx, by, br = s(photo_c[0] + 165), s(photo_c[1] + 170), s(66)
        d.ellipse([bx - br - s(7), by - br - s(7), bx + br + s(7), by + br + s(7)], fill=hex_rgb(th["ring"]) + (255,))
        d.ellipse([bx - br, by - br, bx + br, by + br], fill=hex_rgb(th["accent"]) + (255,))
        d.text((bx, by - s(6)), str(age), font=get_font("sans", s(60 if age < 100 else 44)),
               fill=hex_rgb(th["badge_text"]), anchor="mm")
        d.text((bx, by + s(36)), "YEARS", font=get_font("sans", s(15)), fill=hex_rgb(th["badge_text"]), anchor="mm")

    # name
    name_txt = (name.strip() or "Your Name")
    name_txt = name_txt.upper() if not has_devanagari(name_txt) else name_txt
    f_name, _ = fit_font(d, name_txt, pick_role("name", name_txt), 104, 860)
    d.text((s(540) + s(2), s(895) + s(3)), name_txt, font=f_name, fill=(0, 0, 0, 60), anchor="mm")
    d.text((s(540), s(895)), name_txt, font=f_name, fill=hex_rgb(th["text"]), anchor="mm")

    y = 965
    if relation.strip():
        f_rel = get_font(pick_role("sans", relation), s(28))
        spaced_text(d, s(540), s(y), relation.strip().upper(), f_rel, hex_rgb(th["accent"]) + (255,), s(5))
        y += 50

    # divider
    y += 8
    d.line([(s(300), s(y)), (s(500), s(y))], fill=hex_rgb(th["accent"]) + (255,), width=s(3))
    d.line([(s(580), s(y)), (s(780), s(y))], fill=hex_rgb(th["accent"]) + (255,), width=s(3))
    sparkle(d, s(540), s(y), s(15), hex_rgb(th["accent"]) + (255,))
    y += 55

    # wish
    wish = wish.strip() or WISHES["Classic"]
    wrole = pick_role("body", wish)
    size = 40
    while size > 26:
        f_w = get_font(wrole, s(size))
        lines = wrap(d, wish, f_w, 800)
        if len(lines) <= 5:
            break
        size -= 2
    lh = size * 1.45
    for i, line in enumerate(lines[:6]):
        d.text((s(540), s(y + i * lh)), line, font=f_w, fill=hex_rgb(th["text"]) + (240,), anchor="mm")
    y_end = y + len(lines[:6]) * lh

    # sender
    if sender.strip():
        f_s = get_font(pick_role("name", sender), s(36))
        d.text((s(540), s(max(y_end + 40, 1320))), f"With love, {sender.strip()}", font=f_s,
               fill=hex_rgb(th["title"]), anchor="mm")

    return img.resize((W, H), Image.Resampling.LANCZOS)


def to_bytes(img, fmt="PNG"):
    buf = io.BytesIO()
    if fmt == "JPEG":
        img.convert("RGB").save(buf, "JPEG", quality=95)
    else:
        img.save(buf, "PNG")
    return buf.getvalue()


# =====================================================================
# 3. ALBUM ENGINE  (polaroid pages -> PNG + PDF)
# =====================================================================
def load_img(photo_bytes):
    img = Image.open(io.BytesIO(photo_bytes))
    return ImageOps.exif_transpose(img).convert("RGB")


def new_page(th, rng, confetti_n=90):
    img = gradient((W * S, H * S), *th["bg"])
    d = ImageDraw.Draw(img, "RGBA")
    confetti(d, rng, th["confetti"], (540, 700, 0), n=confetti_n)
    bunting(d, th["balloons"])
    return img, ImageDraw.Draw(img, "RGBA")


def paste_polaroid(img, center, width, photo, caption, th, angle, aspect=1.0):
    """Polaroid-style photo (white frame + soft shadow + tilt)."""
    w = s(width)
    pad = int(w * 0.06)
    ph = int((w - 2 * pad) * aspect)
    bottom = int(w * 0.2)
    card = Image.new("RGBA", (w, pad + ph + bottom), (255, 255, 255, 255))
    pic = ImageOps.fit(photo, (w - 2 * pad, ph), Image.Resampling.LANCZOS, centering=(0.5, 0.4))
    card.paste(pic, (pad, pad))
    if caption:
        cd = ImageDraw.Draw(card)
        role = pick_role("body", caption)
        size = 34
        f = get_font(role, s(size))
        while cd.textlength(caption, font=f) > w - 2 * pad and size > 16:
            size -= 2
            f = get_font(role, s(size))
        cd.text((w // 2, pad + ph + bottom // 2), caption, font=f, fill=(55, 55, 70, 255), anchor="mm")
    # thin accent line on the bottom edge
    ImageDraw.Draw(card).rectangle([0, card.height - s(6), w, card.height], fill=hex_rgb(th["accent"]) + (255,))

    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 120), (0, 0, card.width, card.height))
    pad_sh = s(40)
    sh_big = Image.new("RGBA", (card.width + 2 * pad_sh, card.height + 2 * pad_sh), (0, 0, 0, 0))
    sh_big.paste(shadow, (pad_sh, pad_sh))
    sh_big = sh_big.filter(ImageFilter.GaussianBlur(s(14)))
    card = card.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    sh_big = sh_big.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)

    cx, cy = s(center[0]), s(center[1])
    img.paste(sh_big, (cx - sh_big.width // 2 + s(8), cy - sh_big.height // 2 + s(14)), sh_big)
    img.paste(card, (cx - card.width // 2, cy - card.height // 2), card)


LAYOUTS = {
    1: [((540, 770), 760, -2, 1.1)],
    2: [((430, 530), 560, -5, 1.0), ((650, 1040), 560, 4, 1.0)],
    3: [((380, 470), 470, -6, 1.0), ((700, 740), 470, 5, 1.0), ((400, 1040), 470, -3, 1.0)],
    4: [((310, 450), 440, -4, 1.0), ((770, 470), 440, 4, 1.0), ((310, 990), 440, 3, 1.0), ((770, 1010), 440, -3, 1.0)],
}


def album_cover(th, title, name, age, show_age, photo, seed):
    rng = random.Random(seed)
    img, d = new_page(th, rng, 120)
    spaced_text(d, s(540), s(150), "M E M O R Y   A L B U M", get_font("sans", s(28)),
                hex_rgb(th["accent"]) + (255,), s(2))
    f_t, _ = fit_font(d, title, pick_role("title", title), 120, 900)
    d.text((s(543), s(264)), title, font=f_t, fill=(0, 0, 0, 70), anchor="mm")
    d.text((s(540), s(260)), title, font=f_t, fill=hex_rgb(th["title"]), anchor="mm")

    cx, cy, r = s(540), s(660), s(230)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([cx - r - s(60), cy - r - s(60), cx + r + s(60), cy + r + s(60)],
                                 fill=hex_rgb(th["glow"]) + (150,))
    glow = glow.filter(ImageFilter.GaussianBlur(s(45)))
    img.paste(glow, (0, 0), glow)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([cx - r - s(26), cy - r - s(26), cx + r + s(26), cy + r + s(26)],
              outline=hex_rgb(th["accent"]) + (255,), width=s(8))
    d.ellipse([cx - r - s(10), cy - r - s(10), cx + r + s(10), cy + r + s(10)], fill=hex_rgb(th["ring"]) + (255,))
    pic = circular_photo(to_bytes(photo, "JPEG"), r * 2, 0.4)
    img.paste(pic, (cx - r, cy - r), pic)
    d = ImageDraw.Draw(img, "RGBA")
    for (x, y, rr) in [(250, 400, 22), (840, 420, 26), (200, 930, 18), (890, 950, 20)]:
        sparkle(d, s(x), s(y), s(rr), hex_rgb(th["accent"]) + (230,))

    nm = name.strip() or "Your Name"
    nm = nm.upper() if not has_devanagari(nm) else nm
    f_n, _ = fit_font(d, nm, pick_role("name", nm), 110, 880)
    d.text((s(542), s(1038)), nm, font=f_n, fill=(0, 0, 0, 60), anchor="mm")
    d.text((s(540), s(1035)), nm, font=f_n, fill=hex_rgb(th["text"]), anchor="mm")
    if show_age and age:
        spaced_text(d, s(540), s(1130), f"T U R N I N G   {age}", get_font("sans", s(34)),
                    hex_rgb(th["accent"]) + (255,), s(2))
    d.line([(s(300), s(1215)), (s(500), s(1215))], fill=hex_rgb(th["accent"]) + (255,), width=s(3))
    d.line([(s(580), s(1215)), (s(780), s(1215))], fill=hex_rgb(th["accent"]) + (255,), width=s(3))
    sparkle(d, s(540), s(1215), s(15), hex_rgb(th["accent"]) + (255,))
    return img.resize((W, H), Image.Resampling.LANCZOS)


def album_photo_page(th, photos, captions, page_no, total_pages, seed):
    rng = random.Random(seed)
    img, d = new_page(th, rng, 70)
    spaced_text(d, s(540), s(135), "S W E E T   M E M O R I E S", get_font("sans", s(24)),
                hex_rgb(th["accent"]) + (255,), s(2))
    for ph, cap, (center, width, angle, aspect) in zip(photos, captions, LAYOUTS[len(photos)]):
        paste_polaroid(img, center, width, ph, cap, th, angle, aspect)
    d = ImageDraw.Draw(img, "RGBA")
    spaced_text(d, s(540), s(1395), f"{page_no}  /  {total_pages}", get_font("sans", s(22)),
                hex_rgb(th["text"]) + (220,), s(3))
    return img.resize((W, H), Image.Resampling.LANCZOS)


def album_end(th, name, wish, sender, seed):
    rng = random.Random(seed)
    img, d = new_page(th, rng, 130)
    for (x, y, r) in [(300, 330, 26), (800, 400, 30), (220, 1050, 20), (880, 1010, 24), (540, 250, 18)]:
        sparkle(d, s(x), s(y), s(r), hex_rgb(th["accent"]) + (230,))
    spaced_text(d, s(540), s(330), "W I S H I N G   Y O U   A", get_font("sans", s(28)),
                hex_rgb(th["accent"]) + (255,), s(2))
    f_t, _ = fit_font(d, "Happy Birthday", "title", 128, 900)
    d.text((s(543), s(449)), "Happy Birthday", font=f_t, fill=(0, 0, 0, 70), anchor="mm")
    d.text((s(540), s(445)), "Happy Birthday", font=f_t, fill=hex_rgb(th["title"]), anchor="mm")
    nm = name.strip() or "Your Name"
    nm = nm.upper() if not has_devanagari(nm) else nm
    f_n, _ = fit_font(d, nm, pick_role("name", nm), 100, 860)
    d.text((s(540), s(590)), nm, font=f_n, fill=hex_rgb(th["text"]), anchor="mm")
    d.line([(s(300), s(690)), (s(500), s(690))], fill=hex_rgb(th["accent"]) + (255,), width=s(3))
    d.line([(s(580), s(690)), (s(780), s(690))], fill=hex_rgb(th["accent"]) + (255,), width=s(3))
    sparkle(d, s(540), s(690), s(15), hex_rgb(th["accent"]) + (255,))
    wish = wish.strip() or WISHES["Classic"]
    size = 42
    while size > 26:
        f_w = get_font(pick_role("body", wish), s(size))
        lines = wrap(d, wish, f_w, 800)
        if len(lines) <= 6:
            break
        size -= 2
    lh = size * 1.5
    for i, line in enumerate(lines[:7]):
        d.text((s(540), s(780 + i * lh)), line, font=f_w, fill=hex_rgb(th["text"]) + (240,), anchor="mm")
    if sender.strip():
        d.text((s(540), s(1240)), f"With love, {sender.strip()}", font=get_font(pick_role("name", sender), s(40)),
               fill=hex_rgb(th["title"]), anchor="mm")
    return img.resize((W, H), Image.Resampling.LANCZOS)


def build_album(theme_name, title, name, age, show_age, wish, sender, photo_list, captions, per_page, seed=7):
    """photo_list: list of bytes. returns list of PIL pages (cover, photo pages..., end)."""
    th = THEMES[theme_name]
    photos = [load_img(b) for b in photo_list]
    caps = list(captions) + [""] * (len(photos) - len(captions))
    chunks = [(photos[i:i + per_page], caps[i:i + per_page]) for i in range(0, len(photos), per_page)]
    total = len(chunks) + 2
    pages = [album_cover(th, title, name, age, show_age, photos[0], seed)]
    for n, (ph, cp) in enumerate(chunks, start=2):
        pages.append(album_photo_page(th, ph, cp, n, total, seed + n))
    pages.append(album_end(th, name, wish, sender, seed + 99))
    return pages


def pages_to_pdf(pages):
    buf = io.BytesIO()
    rgb = [p.convert("RGB") for p in pages]
    rgb[0].save(buf, "PDF", save_all=True, append_images=rgb[1:], resolution=150)
    return buf.getvalue()


def pages_to_zip(pages, base="album"):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as z:
        for i, p in enumerate(pages, 1):
            z.writestr(f"{base}_page_{i:02d}.png", to_bytes(p))
    return buf.getvalue()


# =====================================================================
# 4. VIDEO ENGINE  (vertical 720x1280 slideshow + Happy Birthday tune)
# =====================================================================
VW, VH, FPS = 720, 1280, 24
OVERLAP = 0.6


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def font_px(text, role, size):
    return get_font(pick_role(role, text), size)


def fit_px(d, text, role, start, max_w, min_size=24):
    size = start
    while size > min_size:
        f = font_px(text, role, size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 4
    return font_px(text, role, min_size)


def wrap_px(d, text, font, max_w):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split():
            t = (cur + " " + word).strip()
            if d.textlength(t, font=font) <= max_w or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def video_bg(th):
    img = gradient((VW, VH), *th["bg"])
    d = ImageDraw.Draw(img, "RGBA")
    n = 10
    pts = [(VW * i / n, 22 + 22 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    d.line(pts, fill=(255, 255, 255, 200), width=2)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        d.polygon([(x0 + 4, y0), (x1 - 4, y1), ((x0 + x1) / 2, (y0 + y1) / 2 + 44)],
                  fill=hex_rgb(th["balloons"][i % len(th["balloons"])]) + (255,))
    return img


class Confetti:
    """Falling confetti — deterministic for a given time t."""

    def __init__(self, colors, seed, n=60):
        r = random.Random(seed)
        self.p = [(r.uniform(0, VW), r.uniform(0, VH + 60), r.uniform(60, 190), r.uniform(5, 12),
                   hex_rgb(r.choice(colors)), r.uniform(0, 6.28), r.random() < 0.5) for _ in range(n)]

    def draw(self, frame, t):
        d = ImageDraw.Draw(frame, "RGBA")
        for x0, y0, v, sz, col, ph, circle in self.p:
            y = (y0 + v * t) % (VH + 60) - 30
            x = x0 + math.sin(t * 2 + ph) * 18
            if circle:
                d.ellipse([x - sz / 2, y - sz / 2, x + sz / 2, y + sz / 2], fill=col + (215,))
            else:
                a = t * 3 + ph
                dx, dy = math.cos(a) * sz, math.sin(a) * sz
                d.line([(x - dx, y - dy), (x + dx, y + dy)], fill=col + (215,), width=4)


def rising_balloons(frame, th, t, seed, n=5, base_r=46):
    r = random.Random(seed)
    d = ImageDraw.Draw(frame, "RGBA")
    for i in range(n):
        x = r.uniform(70, VW - 70)
        v = r.uniform(110, 190)
        rad = base_r * r.uniform(0.8, 1.15)
        y = VH + 120 + i * 140 - v * (t + 1.2) + math.sin(t * 1.5 + i) * 6
        if -150 < y < VH + 150:
            d.line([(x, y + rad * 1.45), (x + math.sin(t + i) * 8, y + rad * 1.45 + 110)],
                   fill=(255, 255, 255, 150), width=2)
            balloon(d, x, y, rad, th["balloons"][i % len(th["balloons"])])


def ring_photo(photo, diameter, th):
    """Circular photo + white ring + accent ring as one RGBA sprite."""
    pad = 34
    size = diameter + pad * 2
    sprite = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(sprite)
    c = size
    r = diameter  # at 2x scale radius == diameter
    d.ellipse([c - r - 52, c - r - 52, c + r + 52, c + r + 52], outline=hex_rgb(th["accent"]) + (255,), width=14)
    d.ellipse([c - r - 18, c - r - 18, c + r + 18, c + r + 18], fill=hex_rgb(th["ring"]) + (255,))
    pic = circular_photo(to_bytes(photo, "JPEG"), r * 2, 0.4)
    sprite.paste(pic, (c - r, c - r), pic)
    return sprite.resize((size, size), Image.Resampling.LANCZOS)


def make_intro(th, name, age, show_age, relation, first_photo, seed):
    bg = video_bg(th)
    conf = Confetti(th["confetti"], seed)
    sprite = ring_photo(first_photo, 340, th)
    nm = name.strip() or "Your Name"
    nm = nm.upper() if not has_devanagari(nm) else nm
    probe = ImageDraw.Draw(bg)
    f_name = fit_px(probe, nm, "name", 84, 640)
    f_tag = font_px("x", "sans", 24)
    f_rel = font_px(relation, "sans", 28)
    title = "Happy Birthday"
    max_title = 100
    while max_title > 40 and probe.textlength(title, font=font_px(title, "title", max_title)) > 640:
        max_title -= 4
    sizes = {sz: font_px(title, "title", sz) for sz in range(40, max_title + 1, 4)}

    def render(t):
        fr = bg.copy()
        conf.draw(fr, t)
        d = ImageDraw.Draw(fr, "RGBA")
        e1 = ease((t - 0.1) / 0.9)
        e2 = ease((t - 0.5) / 0.8)
        e3 = ease((t - 0.9) / 0.8)
        spaced_text(d, VW // 2, 205, "W I S H I N G   Y O U   A", f_tag,
                    hex_rgb(th["accent"]) + (int(255 * e1),), 2)
        size = max(40, min(max_title, int((0.55 + 0.45 * e1) * max_title) // 4 * 4))
        f_t = sizes[size]
        ty = 290 - (1 - e1) * 70
        d.text((VW // 2 + 3, ty + 4), title, font=f_t, fill=(0, 0, 0, int(70 * e1)), anchor="mm")
        d.text((VW // 2, ty), title, font=f_t, fill=hex_rgb(th["title"]) + (int(255 * e1),), anchor="mm")
        k = 0.45 + 0.55 * e2
        sw = max(2, int(sprite.width * k))
        sp = sprite.resize((sw, sw), Image.Resampling.BILINEAR)
        fr.paste(sp, (VW // 2 - sw // 2, 640 - sw // 2), sp)
        d = ImageDraw.Draw(fr, "RGBA")
        ny = 985 + (1 - e3) * 80
        d.text((VW // 2, ny), nm, font=f_name, fill=hex_rgb(th["text"]) + (int(255 * e3),), anchor="mm")
        if relation.strip():
            spaced_text(d, VW // 2, ny + 62, relation.strip().upper(), f_rel,
                        hex_rgb(th["accent"]) + (int(255 * e3),), 5)
        if show_age and age:
            spaced_text(d, VW // 2, ny + 130, f"T U R N I N G   {age}", font_px("x", "sans", 30),
                        hex_rgb(th["title"]) + (int(255 * e3),), 2)
        rising_balloons(fr, th, t, seed + 1)
        return fr

    return render


def make_photo_scene(th, idx, total, img, caption, dur, seed):
    bg = video_bg(th)
    conf = Confetti(th["confetti"], seed, n=45)
    fw, fh = 600, 760
    big = ImageOps.fit(img, (int(fw * 1.3), int(fh * 1.3)), Image.Resampling.LANCZOS, centering=(0.5, 0.4))
    # static base: shadow + white frame + header + caption
    base = bg.copy()
    sh = Image.new("RGBA", (fw + 120, fh + 120), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([60, 60, fw + 60 + 28, fh + 60 + 28], fill=(0, 0, 0, 140))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    fx, fy = (VW - fw) // 2, 250
    base.paste(sh, (fx - 74, fy - 60), sh)
    d = ImageDraw.Draw(base, "RGBA")
    d.rectangle([fx - 14, fy - 14, fx + fw + 14, fy + fh + 14], fill=(255, 255, 255, 255))
    spaced_text(d, VW // 2, 160, f"M E M O R Y   {idx} / {total}", font_px("x", "sans", 24),
                hex_rgb(th["accent"]) + (255,), 2)
    if caption.strip():
        f_c = font_px(caption, "body", 40)
        lines = wrap_px(d, caption.strip(), f_c, 600)[:3]
        for i, ln in enumerate(lines):
            d.text((VW // 2, 1090 + i * 58), ln, font=f_c, fill=hex_rgb(th["text"]) + (255,), anchor="mm")
    zoom_in = idx % 2 == 1
    pan_dir = 1 if idx % 3 else -1

    def render(t):
        p = t / dur
        z = 1.0 + 0.12 * (p if zoom_in else 1 - p)
        cw, ch = big.width / z, big.height / z
        cx = big.width / 2 + pan_dir * (p - 0.5) * (big.width - cw)
        cy = big.height / 2
        box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
        pic = big.resize((fw, fh), Image.Resampling.BILINEAR, box=box)
        fr = base.copy()
        fr.paste(pic, (fx, fy))
        conf.draw(fr, t)
        return fr

    return render


def make_outro(th, name, wish, sender, seed):
    bg = video_bg(th)
    conf = Confetti(th["confetti"], seed, n=80)
    nm = name.strip() or "Your Name"
    nm = nm.upper() if not has_devanagari(nm) else nm
    probe = ImageDraw.Draw(bg)
    f_name = fit_px(probe, nm, "name", 88, 640)
    wish = wish.strip() or WISHES["Classic"]
    size = 40
    while size > 24:
        f_w = font_px(wish, "body", size)
        lines = wrap_px(probe, wish, f_w, 600)
        if len(lines) <= 6:
            break
        size -= 2
    f_h = fit_px(probe, "Happy Birthday", "title", 90, 640)
    f_s = font_px(sender, "name", 40)
    twinkle = [(120, 260, 18), (600, 330, 22), (90, 1000, 16), (630, 1060, 20), (360, 200, 14)]

    def render(t):
        fr = bg.copy()
        rising_balloons(fr, th, t, seed + 5, n=7, base_r=52)
        conf.draw(fr, t)
        d = ImageDraw.Draw(fr, "RGBA")
        e1 = ease(t / 0.9)
        e2 = ease((t - 0.5) / 0.9)
        e3 = ease((t - 1.1) / 0.9)
        for i, (x, y, r) in enumerate(twinkle):
            k = 0.6 + 0.4 * math.sin(t * 3 + i * 1.3)
            sparkle(d, x, y, r * k, hex_rgb(th["accent"]) + (230,))
        d.text((VW // 2, 300 - (1 - e1) * 60), "Happy Birthday", font=f_h,
               fill=hex_rgb(th["title"]) + (int(255 * e1),), anchor="mm")
        d.text((VW // 2, 420 - (1 - e1) * 40), nm, font=f_name,
               fill=hex_rgb(th["text"]) + (int(255 * e1),), anchor="mm")
        d.line([(190, 520), (320, 520)], fill=hex_rgb(th["accent"]) + (int(255 * e2),), width=3)
        d.line([(400, 520), (530, 520)], fill=hex_rgb(th["accent"]) + (int(255 * e2),), width=3)
        sparkle(d, 360, 520, 13, hex_rgb(th["accent"]) + (int(255 * e2),))
        for i, ln in enumerate(lines[:7]):
            d.text((VW // 2, 620 + i * size * 1.5 + (1 - e2) * 30), ln, font=f_w,
                   fill=hex_rgb(th["text"]) + (int(240 * e2),), anchor="mm")
        if sender.strip():
            d.text((VW // 2, 1000 + (1 - e3) * 30), f"With love, {sender.strip()}", font=f_s,
                   fill=hex_rgb(th["title"]) + (int(255 * e3),), anchor="mm")
        return fr

    return render


# ---------- audio ----------
def happy_birthday_wav(duration, sr=44100, bpm=104):
    """Public-domain 'Happy Birthday' tune, music-box style, looped to `duration` seconds."""
    lines = [
        ([0, 0, 2, 0, 5, 4], [.75, .25, 1, 1, 1, 2]),
        ([0, 0, 2, 0, 7, 5], [.75, .25, 1, 1, 1, 2]),
        ([0, 12, 9, 5, 4, 2], [.75, .25, 1, 1, 1, 2]),
        ([10, 10, 9, 5, 7, 5], [.75, .25, 1, 1, 1, 2]),
    ]
    beat = 60.0 / bpm
    notes = []
    t = 0.0
    for semis, durs in lines:
        for sm, du in zip(semis, durs):
            notes.append((t, du * beat, 261.63 * 2 ** (sm / 12)))
            t += du * beat
    tune_len = t + 1.0
    n_total = int(duration * sr)
    out = np.zeros(n_total + sr * 4, dtype=np.float64)
    start = 0.0
    while start < duration:
        for t0, du, f in notes:
            i0 = int((start + t0) * sr)
            if i0 >= n_total:
                break
            ln = int((du + 0.55) * sr)
            tt = np.arange(ln) / sr
            env = np.minimum(tt / 0.008, 1.0) * np.exp(-tt * 3.2)
            wave_ = (np.sin(2 * np.pi * f * tt) + 0.45 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 5)
                     + 0.2 * np.sin(2 * np.pi * 3 * f * tt) * np.exp(-tt * 8))
            out[i0:i0 + ln] += 0.33 * env * wave_
            # soft low octave for warmth
            out[i0:i0 + ln] += 0.12 * env * np.sin(2 * np.pi * f / 2 * tt)
        start += tune_len
    out = out[:n_total]
    fade = int(1.8 * sr)
    out[-fade:] *= np.linspace(1, 0, fade)
    peak = np.max(np.abs(out)) or 1.0
    pcm = (out / peak * 0.8 * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    return buf.getvalue()


def ffmpeg_exe():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        exe = shutil.which("ffmpeg")
        if exe:
            return exe
    raise RuntimeError("ffmpeg nahi mila. `pip install imageio-ffmpeg` karo (ya server pe ffmpeg install karo).")


def build_video(theme_name, name, age, show_age, relation, wish, sender, photo_list, captions, per_photo,
                music="builtin", music_bytes=None, progress=None, seed=7):
    """returns (mp4_bytes, thumb_jpg_bytes)."""
    th = THEMES[theme_name]
    exe = ffmpeg_exe()
    imgs = [load_img(b) for b in photo_list]
    caps = list(captions) + [""] * (len(imgs) - len(captions))
    n = len(imgs)

    scenes = [(4.0, make_intro(th, name, age, show_age, relation, imgs[0], seed))]
    for i, (im, cp) in enumerate(zip(imgs, caps), start=1):
        scenes.append((per_photo, make_photo_scene(th, i, n, im, cp, per_photo, seed + i)))
    scenes.append((5.5, make_outro(th, name, wish, sender, seed + 50)))

    starts, t = [], 0.0
    for du, _ in scenes:
        starts.append(t)
        t += du - OVERLAP
    total = starts[-1] + scenes[-1][0]
    nframes = int(total * FPS)

    tmp = Path(tempfile.mkdtemp(prefix="bdayvid_"))
    try:
        silent = tmp / "silent.mp4"
        cmd = [exe, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}",
               "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
               "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(silent)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=open(tmp / "ffmpeg.log", "wb"))
        thumb = None
        for f in range(nframes):
            tt = f / FPS
            active = [i for i, (du, _) in enumerate(scenes) if starts[i] <= tt < starts[i] + du]
            if not active:
                active = [len(scenes) - 1]
            a = active[0]
            fr = scenes[a][1](tt - starts[a])
            if len(active) > 1:
                b = active[1]
                alpha = min(1.0, (tt - starts[b]) / OVERLAP)
                fr = Image.blend(fr, scenes[b][1](tt - starts[b]), alpha)
            if thumb is None and tt >= 1.8:
                thumb = to_bytes(fr, "JPEG")
            proc.stdin.write(fr.convert("RGB").tobytes())
            if progress and f % 6 == 0:
                progress(min(0.97, f / nframes))
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("Video encode fail: " + (tmp / "ffmpeg.log").read_text(errors="ignore")[-400:])

        final = tmp / "final.mp4"
        if music == "none":
            shutil.copy(silent, final)
        else:
            if music == "upload" and music_bytes:
                audio = tmp / "music.bin"
                audio.write_bytes(music_bytes)
                a_in = ["-stream_loop", "-1", "-i", str(audio)]
            else:
                audio = tmp / "tune.wav"
                audio.write_bytes(happy_birthday_wav(total + 1))
                a_in = ["-i", str(audio)]
            mux = [exe, "-y", "-loglevel", "error", "-i", str(silent)] + a_in + [
                "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                "-af", f"afade=t=out:st={max(0.0, total - 1.8):.2f}:d=1.8", "-t", f"{total:.2f}", str(final)]
            r = subprocess.run(mux, capture_output=True)
            if r.returncode != 0:
                shutil.copy(silent, final)  # music fail -> bina music wala video
        if progress:
            progress(1.0)
        return final.read_bytes(), thumb
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# =====================================================================
# 5. DATABASE + LOGIN
# =====================================================================
BASE_DIR = Path(__file__).parent if "__file__" in globals() else Path.cwd()
DATA_DIR = BASE_DIR / "data"
FILES_DIR = DATA_DIR / "files"
DB_PATH = DATA_DIR / "studio.db"
DATA_DIR.mkdir(exist_ok=True)
FILES_DIR.mkdir(exist_ok=True)

KIND_LABEL = {"card": "🎴 Card", "album": "📖 Album", "video": "🎬 Video"}


def _secret(key, default):
    v = os.environ.get(key)
    if v:
        return v
    try:
        return st.secrets[key]
    except Exception:
        return default


def q(sql, args=(), one=False, commit=False):
    con = sqlite3.connect(DB_PATH, timeout=15)
    con.row_factory = sqlite3.Row
    try:
        cur = con.execute(sql, args)
        if commit:
            con.commit()
            return cur.lastrowid
        rows = cur.fetchall()
        return (rows[0] if rows else None) if one else rows
    finally:
        con.close()


def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 200_000).hex()
    return h, salt


def check_pw(pw, h, salt):
    return hmac.compare_digest(hash_pw(pw, salt)[0], h)


def init_db():
    con = sqlite3.connect(DB_PATH)
    con.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL, pw_hash TEXT NOT NULL, salt TEXT NOT NULL,
            full_name TEXT, dob TEXT, phone TEXT, email TEXT,
            role TEXT NOT NULL DEFAULT 'user', active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT, last_login TEXT);
        CREATE TABLE IF NOT EXISTS creations(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            kind TEXT NOT NULL, title TEXT, path TEXT NOT NULL, thumb TEXT, created_at TEXT);
    """)
    con.commit()
    con.close()
    if not q("SELECT 1 FROM users WHERE role='admin'", one=True):
        create_user(_secret("ADMIN_USER", "admin"), _secret("ADMIN_PASSWORD", "admin123"),
                    "Administrator", "", "", "", role="admin")


def create_user(username, password, full_name, dob, phone, email, role="user"):
    username = (username or "").strip().lower()
    if not re.fullmatch(r"[a-z0-9_.]{3,24}", username):
        return False, "Username 3-24 characters ka ho (a-z, 0-9, _ , .)."
    if len(password or "") < 6:
        return False, "Password kam se kam 6 characters ka rakho."
    if not (full_name or "").strip():
        return False, "Poora naam likho."
    if q("SELECT 1 FROM users WHERE username=?", (username,), one=True):
        return False, "Ye username pehle se hai, doosra chuno."
    h, salt = hash_pw(password)
    q("INSERT INTO users(username,pw_hash,salt,full_name,dob,phone,email,role,active,created_at) "
      "VALUES(?,?,?,?,?,?,?,?,1,?)",
      (username, h, salt, full_name.strip(), dob or "", (phone or "").strip(), (email or "").strip(),
       role, datetime.now().isoformat(timespec="seconds")), commit=True)
    return True, "Account ban gaya!"


def authenticate(username, password):
    row = q("SELECT * FROM users WHERE username=?", ((username or "").strip().lower(),), one=True)
    if not row or not check_pw(password or "", row["pw_hash"], row["salt"]):
        return None, "Username ya password galat hai."
    if not row["active"]:
        return None, "Ye ID band (deactivate) hai. Admin se baat karo."
    q("UPDATE users SET last_login=? WHERE id=?", (datetime.now().isoformat(timespec="seconds"), row["id"]), commit=True)
    return row, ""


def get_user(uid):
    return q("SELECT * FROM users WHERE id=?", (uid,), one=True)


def calc_age(dob):
    try:
        b = date.fromisoformat(dob)
    except Exception:
        return None
    t = date.today()
    return t.year - b.year - ((t.month, t.day) < (b.month, b.day))


def days_to_birthday(dob):
    try:
        b = date.fromisoformat(dob)
    except Exception:
        return None
    t = date.today()
    for yr in (t.year, t.year + 1):
        try:
            nb = b.replace(year=yr)
        except ValueError:  # 29 Feb
            nb = date(yr, 3, 1)
        if nb >= t:
            return (nb - t).days


# ---------- creations storage ----------
def save_creation(uid, kind, title, data, ext, thumb_bytes=None):
    folder = FILES_DIR / str(uid)
    folder.mkdir(parents=True, exist_ok=True)
    stem = f"{kind}_{datetime.now():%Y%m%d_%H%M%S}_{secrets.token_hex(2)}"
    (folder / f"{stem}.{ext}").write_bytes(data)
    rel_t = None
    if thumb_bytes:
        (folder / f"{stem}_thumb.jpg").write_bytes(thumb_bytes)
        rel_t = f"{uid}/{stem}_thumb.jpg"
    return q("INSERT INTO creations(user_id,kind,title,path,thumb,created_at) VALUES(?,?,?,?,?,?)",
             (uid, kind, title, f"{uid}/{stem}.{ext}", rel_t, datetime.now().isoformat(timespec="seconds")),
             commit=True)


def delete_creation(cid):
    row = q("SELECT * FROM creations WHERE id=?", (cid,), one=True)
    if row:
        for rel in (row["path"], row["thumb"]):
            if rel:
                try:
                    (FILES_DIR / rel).unlink()
                except OSError:
                    pass
        q("DELETE FROM creations WHERE id=?", (cid,), commit=True)


def delete_user(uid):
    shutil.rmtree(FILES_DIR / str(uid), ignore_errors=True)
    remove_profile_photo(uid)
    q("DELETE FROM creations WHERE user_id=?", (uid,), commit=True)
    q("DELETE FROM users WHERE id=?", (uid,), commit=True)


# ---------- profile photo ----------
def profile_path(uid):
    return FILES_DIR / "profiles" / f"{uid}.jpg"


def set_profile_photo(uid, data):
    try:
        img = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
    except Exception:
        return False
    img = ImageOps.fit(img, (512, 512), Image.Resampling.LANCZOS, centering=(0.5, 0.4))
    p = profile_path(uid)
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p, "JPEG", quality=92)
    return True


def get_profile_photo(uid):
    p = profile_path(uid)
    return p.read_bytes() if p.exists() else None


def remove_profile_photo(uid):
    try:
        profile_path(uid).unlink()
    except OSError:
        pass


def photo_uri(uid, size=96):
    data = get_profile_photo(uid)
    if not data:
        return None
    import base64
    im = Image.open(io.BytesIO(data)).resize((size, size), Image.Resampling.LANCZOS)
    return "data:image/jpeg;base64," + base64.b64encode(to_bytes(im, "JPEG")).decode()


def avatar_html(user):
    uri = photo_uri(user["id"], 96)
    if uri:
        return f'<div class="avatar"><img src="{uri}"></div>'
    return f'<div class="avatar">{(user["full_name"] or user["username"])[:1].upper()}</div>'


MIME = {"png": "image/png", "jpg": "image/jpeg", "pdf": "application/pdf", "mp4": "video/mp4", "zip": "application/zip"}


def render_gallery(rows, prefix, cols=3, show_owner=False):
    if not rows:
        st.info("Abhi kuch nahi bana hai.")
        return
    for i in range(0, len(rows), cols):
        cs = st.columns(cols)
        for c, row in zip(cs, rows[i:i + cols]):
            main = FILES_DIR / row["path"]
            if not main.exists():
                continue
            ext = main.suffix.lstrip(".")
            with c.container(border=True):
                head = f"**{KIND_LABEL.get(row['kind'], row['kind'])}** · {row['title'] or ''}"
                st.markdown(head)
                owner = f" · {row['full_name']} (@{row['username']})" if show_owner and "username" in row.keys() else ""
                st.caption(f"{row['created_at'].replace('T', ' ')}{owner}")
                thumb = FILES_DIR / row["thumb"] if row["thumb"] else None
                if ext in ("png", "jpg"):
                    st.image(main.read_bytes(), use_container_width=True)
                elif thumb and thumb.exists():
                    st.image(thumb.read_bytes(), use_container_width=True)
                if ext == "mp4":
                    with st.expander("▶ Video dekho"):
                        st.video(main.read_bytes())
                b1, b2 = st.columns(2)
                b1.download_button("⬇️ Download", main.read_bytes(), main.name, MIME.get(ext, "application/octet-stream"),
                                   key=f"{prefix}_dl_{row['id']}", use_container_width=True)
                if b2.button("🗑️ Delete", key=f"{prefix}_del_{row['id']}", use_container_width=True):
                    delete_creation(row["id"])
                    st.rerun()


def user_creations(uid, kind=None):
    sql = "SELECT * FROM creations WHERE user_id=?"
    args = [uid]
    if kind:
        sql += " AND kind=?"
        args.append(kind)
    return q(sql + " ORDER BY id DESC", tuple(args))



def page_header(title, sub=""):
    st.markdown(f'<div class="ph"><h2>{title}</h2><p>{sub}</p></div>', unsafe_allow_html=True)


def stat_cards(items, cls="g3"):
    html = "".join(f'<div class="stat"><div class="ic">{ic}</div><div class="v">{v}</div><div class="l">{lb}</div></div>'
                   for ic, lb, v in items)
    st.markdown(f'<div class="grid {cls}">{html}</div>', unsafe_allow_html=True)


def feature_cards(items):
    html = "".join(f'<div class="feat"><div class="ic">{ic}</div><h4>{t}</h4><p>{d}</p></div>' for ic, t, d in items)
    st.markdown(f'<div class="grid g3">{html}</div>', unsafe_allow_html=True)


# =====================================================================
# 6. USER PANEL
# =====================================================================
def photo_captions_box(n, key):
    txt = st.text_area("Captions (optional — ek line me ek, photo ke order me)", key=key, height=110,
                       placeholder="Goa trip\nCollege days\nMummy ke saath …")
    return [ln.strip() for ln in txt.split("\n")][:n]


def prefill(user):
    return (user["full_name"] or ""), (calc_age(user["dob"]) or 18)


def page_card(user):
    page_header("🎴 Birthday Card", "Photo, naam aur wish daalo — HD card turant tayyar")
    name0, age0 = prefill(user)
    form, preview = st.columns([1, 1.05], gap="large")
    if "seed" not in st.session_state:
        st.session_state.seed = 7
    with form:
        name = st.text_input("Naam", name0, key="c_name")
        c1, c2 = st.columns(2)
        age = c1.number_input("Umar", 1, 120, int(min(max(age0, 1), 120)), key="c_age")
        show_age = c2.checkbox("Card pe umar dikhao", True, key="c_showage")
        relation = st.text_input("Rishta (optional)", "Best Friend", key="c_rel")
        choice = st.selectbox("Wish chuno", list(WISHES.keys()), key="c_choice")
        if WISHES[choice]:
            wish = st.text_area("Wish edit kar sakte ho", WISHES[choice], height=95, key=f"c_wish_{choice}")
        else:
            wish = st.text_area("Apni wish likho", "", height=95, placeholder="Yahan apna message likho…", key="c_wish_own")
        sender = st.text_input("Kisne bheja? (optional)", user["full_name"] or "", key="c_sender")
        theme = st.radio("Theme", list(THEMES.keys()), horizontal=True, key="c_theme")
        photo = st.file_uploader("Photo (gol frame me auto-fit)", type=["jpg", "jpeg", "png", "webp"], key="c_photo")
        prof = get_profile_photo(user["id"])
        use_prof = bool(prof) and not photo and st.checkbox("📸 Meri profile photo use karo", True, key="c_useprof")
        focus_y = 0.4
        if photo or use_prof:
            focus_y = st.slider("Photo upar ↔ neeche", 0.0, 1.0, 0.4, 0.05, key="c_focus")
        if st.button("🎊 Confetti naya karo", key="c_conf"):
            st.session_state.seed += 1

    @st.cache_data(show_spinner=False, max_entries=24)
    def cached_render(*args):
        return to_bytes(render_card(*args))

    photo_bytes = photo.getvalue() if photo else (prof if use_prof else None)
    png = cached_render(theme, name, int(age), show_age, relation, wish, sender, photo_bytes, focus_y,
                        st.session_state.seed)
    with preview:
        st.image(png, use_container_width=True)
        safe = re.sub(r"[^\w\-]+", "_", name.strip() or "card")
        d1, d2 = st.columns(2)
        d1.download_button("⬇️ PNG (HD)", png, f"{safe}_birthday_card.png", "image/png", key="c_dl_png")
        d2.download_button("⬇️ JPG (chhoti file)", to_bytes(Image.open(io.BytesIO(png)), "JPEG"),
                           f"{safe}_birthday_card.jpg", "image/jpeg", key="c_dl_jpg")
        if st.button("💾 Meri gallery me save karo", key="c_save", use_container_width=True, type="primary"):
            save_creation(user["id"], "card", f"{name.strip() or 'Card'}", png, "png")
            st.success("Card gallery me save ho gaya ✅")
        msg = f"Happy Birthday {name.strip()}! 🎂🎉 Ye card sirf tumhare liye ❤️"
        st.link_button("📲 WhatsApp pe bhejo", "https://wa.me/?text=" + urllib.parse.quote(msg), use_container_width=True)
        st.caption("Pehle card download karo, phir WhatsApp me attach karke bhej do.")


def page_album(user):
    page_header("📖 Birthday Album", "Photos se polaroid-style album — PDF aur PNG dono me")
    st.caption("Photos daalo — cover, polaroid pages aur last wish page wala poora album ban jayega (PDF + PNG).")
    name0, age0 = prefill(user)
    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        title = st.text_input("Album ka title", "Happy Birthday", key="a_title")
        name = st.text_input("Naam", name0, key="a_name")
        c11, c12 = st.columns(2)
        age = c11.number_input("Umar", 1, 120, int(min(max(age0, 1), 120)), key="a_age")
        show_age = c12.checkbox("Cover pe umar", True, key="a_showage")
        theme = st.radio("Theme", list(THEMES.keys()), horizontal=True, key="a_theme")
        per_page = st.select_slider("Ek page pe kitni photos", [1, 2, 3, 4], value=3, key="a_per")
    with c2:
        wish = st.text_area("Last page ki wish", WISHES["Dil se (Hinglish)"], height=100, key="a_wish")
        sender = st.text_input("Kisne bheja?", user["full_name"] or "", key="a_sender")
        files = st.file_uploader("Photos (1 se 24)", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True,
                                 key="a_files")
    prof = get_profile_photo(user["id"])
    inc = bool(prof) and st.checkbox("📸 Meri profile photo bhi shamil karo (pehli photo)", True, key="a_incprof")
    caps = photo_captions_box(24, "a_caps")
    if files and len(files) > 24:
        st.warning("Sirf pehli 24 photos li jayengi.")
    blobs = ([prof] if inc else []) + [f.getvalue() for f in (files or [])]
    blobs = blobs[:24]
    if inc:
        caps = [""] + caps
    if st.button("📖 Album banao", type="primary", disabled=not blobs, key="a_go"):
        with st.spinner("Album ban raha hai…"):
            pages = build_album(theme, title.strip() or "Happy Birthday", name, int(age), show_age, wish, sender,
                                blobs, caps, per_page)
            pdf = pages_to_pdf(pages)
            safe = re.sub(r"[^\w\-]+", "_", name.strip() or "album")
            st.session_state["album_res"] = dict(pages=[to_bytes(p) for p in pages], pdf=pdf,
                                                 zip=pages_to_zip(pages, safe), safe=safe)
            save_creation(user["id"], "album", f"{name.strip() or 'Album'} ({len(blobs)} photos)", pdf, "pdf",
                          thumb_bytes=to_bytes(pages[0], "JPEG"))
        st.success("Album ban gaya aur gallery me save ho gaya ✅")
    res = st.session_state.get("album_res")
    if res:
        d1, d2 = st.columns(2)
        d1.download_button("⬇️ Album PDF", res["pdf"], f"{res['safe']}_album.pdf", "application/pdf", key="a_dl_pdf",
                           use_container_width=True)
        d2.download_button("⬇️ Sab pages (ZIP of PNG)", res["zip"], f"{res['safe']}_album_pages.zip", "application/zip",
                           key="a_dl_zip", use_container_width=True)
        cols = st.columns(3)
        for i, pg in enumerate(res["pages"]):
            cols[i % 3].image(pg, caption=f"Page {i + 1}", use_container_width=True)


def page_video(user):
    page_header("🎬 Birthday Video", "Photos se vertical video — music, zoom, confetti aur balloons ke saath")
    st.caption("Photos se vertical (WhatsApp/Reels size) video — intro, Ken-Burns zoom, confetti, balloons aur Happy Birthday tune.")
    name0, age0 = prefill(user)
    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        name = st.text_input("Naam", name0, key="v_name")
        c11, c12 = st.columns(2)
        age = c11.number_input("Umar", 1, 120, int(min(max(age0, 1), 120)), key="v_age")
        show_age = c12.checkbox("Umar dikhao", True, key="v_showage")
        relation = st.text_input("Rishta (optional)", "", key="v_rel")
        theme = st.radio("Theme", list(THEMES.keys()), horizontal=True, key="v_theme")
        per_photo = st.slider("Har photo kitni der (seconds)", 2.0, 6.0, 3.5, 0.5, key="v_per")
    with c2:
        wish = st.text_area("Wish (last scene)", WISHES["Dil se (Hinglish)"], height=100, key="v_wish")
        sender = st.text_input("Kisne bheja?", user["full_name"] or "", key="v_sender")
        music = st.radio("Music", ["builtin", "upload", "none"], horizontal=True, key="v_music",
                         format_func={"builtin": "🎵 Happy Birthday tune", "upload": "📁 Apna music", "none": "🔇 Bina music"}.get)
        music_bytes = None
        if music == "upload":
            m = st.file_uploader("Music file (mp3/wav/m4a)", type=["mp3", "wav", "m4a", "aac", "ogg"], key="v_mfile")
            music_bytes = m.getvalue() if m else None
        files = st.file_uploader("Photos (1 se 12)", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True,
                                 key="v_files")
    prof = get_profile_photo(user["id"])
    inc = bool(prof) and st.checkbox("📸 Meri profile photo bhi shamil karo (pehli photo)", True, key="v_incprof")
    caps = photo_captions_box(12, "v_caps")
    if files and len(files) > 12:
        st.warning("Sirf pehli 12 photos li jayengi.")
    blobs = ([prof] if inc else []) + [f.getvalue() for f in (files or [])]
    blobs = blobs[:12]
    if inc:
        caps = [""] + caps
    if blobs:
        est = 4 + len(blobs) * (per_photo - 0.6) + 5.5 - 0.6
        st.caption(f"Video lagbhag **{est:.0f} second** ka banega. Banane me 30-90 second lag sakte hain.")
    if st.button("🎬 Video banao", type="primary", disabled=not blobs, key="v_go"):
        bar = st.progress(0.0, text="Video ban raha hai…")
        try:
            mp4, thumb = build_video(theme, name, int(age), show_age, relation, wish, sender,
                                     blobs, caps, per_photo,
                                     music=music, music_bytes=music_bytes,
                                     progress=lambda p: bar.progress(p, text="Video ban raha hai…"))
            safe = re.sub(r"[^\w\-]+", "_", name.strip() or "video")
            st.session_state["video_res"] = dict(mp4=mp4, safe=safe)
            save_creation(user["id"], "video", f"{name.strip() or 'Video'} ({len(blobs)} photos)", mp4, "mp4",
                          thumb_bytes=thumb)
            bar.empty()
            st.success("Video ban gaya aur gallery me save ho gaya ✅")
        except Exception as e:
            bar.empty()
            st.error(f"Video nahi ban paya: {e}")
    res = st.session_state.get("video_res")
    if res:
        _, mid, _ = st.columns([1, 1, 1])
        with mid:
            st.video(res["mp4"])
        st.download_button("⬇️ Video download (MP4)", res["mp4"], f"{res['safe']}_birthday_video.mp4", "video/mp4",
                           key="v_dl", use_container_width=True)


def page_gallery(user):
    page_header("🗂️ Meri Gallery", "Aapki banayi sab cards, albums aur videos yahin hain")
    f = st.radio("Dikhao", ["all", "card", "album", "video"], horizontal=True, key="g_f",
                 format_func=lambda k: "Sab" if k == "all" else KIND_LABEL[k])
    render_gallery(user_creations(user["id"], None if f == "all" else f), "ug")


def profile_form(user):
    cur = get_profile_photo(user["id"])
    pc1, pc2 = st.columns([1, 4])
    with pc1:
        if cur:
            st.image(cur, width=130)
        else:
            st.caption("Abhi koi profile photo nahi hai.")
    with st.form("prof"):
        newphoto = st.file_uploader("📸 Profile photo upload / badlo", type=["jpg", "jpeg", "png", "webp"], key="pf_photo")
        delphoto = st.checkbox("Photo hata do", False) if cur else False
        name = st.text_input("Poora naam", user["full_name"] or "")
        try:
            dv = date.fromisoformat(user["dob"])
        except Exception:
            dv = date(2000, 1, 1)
        dob = st.date_input("Janamdin", dv, min_value=date(1920, 1, 1), max_value=date.today())
        phone = st.text_input("Phone", user["phone"] or "")
        email = st.text_input("Email", user["email"] or "")
        if st.form_submit_button("Save"):
            q("UPDATE users SET full_name=?, dob=?, phone=?, email=? WHERE id=?",
              (name.strip() or user["full_name"], dob.isoformat(), phone.strip(), email.strip(), user["id"]), commit=True)
            if newphoto:
                if not set_profile_photo(user["id"], newphoto.getvalue()):
                    st.error("Ye photo khul nahi payi, doosri try karo.")
            elif delphoto:
                remove_profile_photo(user["id"])
            st.success("Profile update ho gaya ✅")
            st.rerun()


def page_profile(user):
    page_header("👤 Mera Profile", "Apni jankari, photo aur password yahan badlo")
    profile_form(user)
    password_form(user, "u")


def password_form(user, key, expanded=False):
    with st.expander("🔒 Password badlo", expanded=expanded):
        with st.form(f"pw_{key}"):
            old = st.text_input("Purana password", type="password")
            new = st.text_input("Naya password (min 6)", type="password")
            if st.form_submit_button("Password badlo"):
                if not check_pw(old, user["pw_hash"], user["salt"]):
                    st.error("Purana password galat hai.")
                elif len(new) < 6:
                    st.error("Naya password kam se kam 6 characters ka ho.")
                else:
                    h, salt = hash_pw(new)
                    q("UPDATE users SET pw_hash=?, salt=? WHERE id=?", (h, salt, user["id"]), commit=True)
                    st.success("Password badal gaya ✅")


def page_home(user):
    first = (user["full_name"] or user["username"]).split()[0]
    dl = days_to_birthday(user["dob"])
    if dl == 0:
        st.balloons()
        count = '<div class="count"><b>🎉</b><span>Aaj aapka Birthday hai!</span></div>'
    elif dl is not None:
        count = f'<div class="count"><b>{dl}</b><span>din baaki aapke birthday me 🎂</span></div>'
    else:
        count = '<div class="count"><span>Profile me janamdin aur photo daalo — card/video me auto-use hongi</span></div>'
    uri = photo_uri(user["id"], 160)
    av = f'<img class="hero-av" src="{uri}">' if uri else ""
    st.markdown(f'<div class="hero-big">{av}<h1>Namaste, {first}! 👋</h1>'
                f'<p>Aaj kya banayein? Card, Album ya Video — sab yahin.</p>{count}</div>', unsafe_allow_html=True)
    feature_cards([("🎴", "Birthday Card", "Gol photo, balloons aur wish ke saath HD card. Left menu se 'Birthday Card' kholo."),
                   ("📖", "Birthday Album", "Polaroid pages ka poora album — PDF me download karo."),
                   ("🎬", "Birthday Video", "Photos + music + zoom effects — WhatsApp ke liye ready video.")])
    cnt = {k: len(user_creations(user["id"], k)) for k in KIND_LABEL}
    stat_cards([("🎴", "Cards banaye", cnt["card"]), ("📖", "Albums banaye", cnt["album"]),
                ("🎬", "Videos banaye", cnt["video"])])


def user_panel(user):
    pages = {"🏠 Home": page_home, "🎴 Birthday Card": page_card, "📖 Birthday Album": page_album,
             "🎬 Birthday Video": page_video, "🗂️ Meri Gallery": page_gallery, "👤 Profile": page_profile}
    choice = st.sidebar.radio("Menu", list(pages), key="nav_user")
    pages[choice](user)


# =====================================================================
# 7. ADMIN PANEL
# =====================================================================
def admin_users_rows():
    return q("""SELECT u.*,
        (SELECT COUNT(*) FROM creations c WHERE c.user_id=u.id AND c.kind='card')  AS cards,
        (SELECT COUNT(*) FROM creations c WHERE c.user_id=u.id AND c.kind='album') AS albums,
        (SELECT COUNT(*) FROM creations c WHERE c.user_id=u.id AND c.kind='video') AS videos
        FROM users u ORDER BY u.id ASC""")


def users_table(rows):
    out = []
    for n, r in enumerate(rows, start=1):
        out.append({"No.": n, "Photo": photo_uri(r["id"], 64), "Naam": r["full_name"], "Username": r["username"], "Role": r["role"],
                    "Janamdin": r["dob"], "Umar": calc_age(r["dob"]), "Phone": r["phone"], "Email": r["email"],
                    "Joined": (r["created_at"] or "")[:10], "Last login": (r["last_login"] or "")[:16].replace("T", " "),
                    "Active": "Haan" if r["active"] else "Nahi",
                    "Cards": r["cards"], "Albums": r["albums"], "Videos": r["videos"]})
    return out


def admin_dashboard():
    page_header("📊 Dashboard", "Poore studio ka ek nazar me haal")
    rows = admin_users_rows()
    users = [r for r in rows if r["role"] == "user"]
    today = date.today().isoformat()
    kinds = {k: q("SELECT COUNT(*) n FROM creations WHERE kind=?", (k,), one=True)["n"] for k in KIND_LABEL}
    stat_cards([("👥", "Total users", len(users)),
                ("🆕", "Aaj naye", sum(1 for r in users if (r["created_at"] or "").startswith(today))),
                ("🎴", "Cards", kinds["card"]), ("📖", "Albums", kinds["album"]), ("🎬", "Videos", kinds["video"])], "g5")

    up = sorted([(days_to_birthday(r["dob"]), r) for r in users if days_to_birthday(r["dob"]) is not None],
                key=lambda x: x[0])
    st.markdown("#### 🎂 Aane wale birthdays (30 din)")
    soon = [(d, r) for d, r in up if d <= 30]
    if soon:
        st.dataframe([{"Kitne din": "AAJ 🎉" if d == 0 else d, "Naam": r["full_name"], "Username": r["username"],
                       "Janamdin": r["dob"], "Phone": r["phone"]} for d, r in soon],
                     use_container_width=True, hide_index=True)
    else:
        st.caption("Agle 30 din me kisi ka birthday nahi.")
    st.markdown("#### 🕒 Haal ki creations")
    rec = q("""SELECT c.*, u.full_name, u.username FROM creations c JOIN users u ON u.id=c.user_id
               ORDER BY c.id DESC LIMIT 6""")
    render_gallery(rec, "ad", show_owner=True)


def admin_users():
    page_header("👥 Sab Users", "Sab users ki jankari, edit, reset aur export")
    rows = admin_users_rows()
    search = st.text_input("🔎 Search (naam / username / phone / email)", key="adm_search").strip().lower()
    if search:
        rows = [r for r in rows if search in " ".join(str(r[k] or "") for k in ("full_name", "username", "phone", "email")).lower()]
    table = users_table(rows)
    st.dataframe(table, use_container_width=True, hide_index=True,
                 column_config={"Photo": st.column_config.ImageColumn("Photo", width="small")})
    if table:
        buf = io.StringIO()
        plain = [{k: v for k, v in r.items() if k != "Photo"} for r in table]
        w = csv.DictWriter(buf, fieldnames=list(plain[0].keys()))
        w.writeheader()
        w.writerows(plain)
        st.download_button("⬇️ CSV export", buf.getvalue().encode("utf-8-sig"), "users.csv", "text/csv", key="adm_csv")

    st.divider()
    st.markdown("#### Ek user manage karo")
    if not rows:
        return
    opts = {f"{r['full_name']} (@{r['username']}) · #{r['id']}": r["id"] for r in rows}
    sel = st.selectbox("User chuno", list(opts), key="adm_sel")
    u = get_user(opts[sel])
    me = st.session_state.get("uid")
    pimg = get_profile_photo(u["id"])
    if pimg:
        pc1, pc2 = st.columns([1, 6])
        pc1.image(pimg, width=110)
        if pc2.button("🗑️ Is user ki profile photo hatao", key=f"adm_rmph_{u['id']}"):
            remove_profile_photo(u["id"])
            st.rerun()
    with st.form(f"adm_edit_{u['id']}"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Naam", u["full_name"] or "")
        try:
            dv = date.fromisoformat(u["dob"])
        except Exception:
            dv = date(2000, 1, 1)
        dob = c2.date_input("Janamdin", dv, min_value=date(1920, 1, 1), max_value=date.today())
        phone = c1.text_input("Phone", u["phone"] or "")
        email = c2.text_input("Email", u["email"] or "")
        role = c1.selectbox("Role", ["user", "admin"], index=0 if u["role"] == "user" else 1)
        active = c2.checkbox("ID active hai", bool(u["active"]))
        if st.form_submit_button("💾 Save changes"):
            if u["id"] == me and (role != "admin" or not active):
                st.error("Apni khud ki admin ID ko band/demote nahi kar sakte.")
            else:
                q("UPDATE users SET full_name=?, dob=?, phone=?, email=?, role=?, active=? WHERE id=?",
                  (name.strip(), dob.isoformat(), phone.strip(), email.strip(), role, int(active), u["id"]), commit=True)
                st.success("Update ho gaya ✅")
                st.rerun()
    c1, c2 = st.columns(2)
    with c1.form(f"adm_pw_{u['id']}"):
        newpw = st.text_input("Naya password set karo", type="password")
        if st.form_submit_button("🔑 Password reset"):
            if len(newpw) < 6:
                st.error("Min 6 characters.")
            else:
                h, salt = hash_pw(newpw)
                q("UPDATE users SET pw_hash=?, salt=? WHERE id=?", (h, salt, u["id"]), commit=True)
                st.success("Password badal diya ✅")
    with c2.form(f"adm_del_{u['id']}"):
        st.caption("User aur uski saari creations hamesha ke liye delete ho jayengi.")
        sure = st.checkbox("Haan, pakka delete karna hai")
        if st.form_submit_button("🗑️ User delete karo"):
            if u["id"] == me:
                st.error("Apni khud ki ID delete nahi kar sakte.")
            elif not sure:
                st.warning("Pehle checkbox tick karo.")
            else:
                delete_user(u["id"])
                st.success("User delete ho gaya.")
                st.rerun()
    st.markdown(f"##### {u['full_name']} ki creations")
    render_gallery(user_creations(u["id"]), f"au{u['id']}")


def admin_creations():
    page_header("🖼️ Sab Creations", "Har user ki banayi cards, albums aur videos")
    c1, c2 = st.columns(2)
    kind = c1.selectbox("Type", ["all", "card", "album", "video"], key="adm_kind",
                        format_func=lambda k: "Sab" if k == "all" else KIND_LABEL[k])
    who = c2.text_input("User (naam ya username)", key="adm_who").strip().lower()
    sql = """SELECT c.*, u.full_name, u.username FROM creations c JOIN users u ON u.id=c.user_id WHERE 1=1"""
    args = []
    if kind != "all":
        sql += " AND c.kind=?"
        args.append(kind)
    if who:
        sql += " AND (lower(u.username) LIKE ? OR lower(u.full_name) LIKE ?)"
        args += [f"%{who}%"] * 2
    rows = q(sql + " ORDER BY c.id DESC LIMIT 60", tuple(args))
    st.caption(f"{len(rows)} items (latest 60)")
    render_gallery(rows, "ac", show_owner=True)


def admin_new_user():
    page_header("➕ Naya user / admin banao", "Naya account seedha admin se banao")
    with st.form("adm_new", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Poora naam")
        uname = c2.text_input("Username")
        pw = c1.text_input("Password", type="password")
        role = c2.selectbox("Role", ["user", "admin"])
        dob = c1.date_input("Janamdin", date(2000, 1, 1), min_value=date(1920, 1, 1), max_value=date.today())
        phone = c2.text_input("Phone")
        email = c1.text_input("Email")
        nphoto = c2.file_uploader("📸 Profile photo (optional)", type=["jpg", "jpeg", "png", "webp"], key="adm_nphoto")
        if st.form_submit_button("Banao"):
            ok, msg = create_user(uname, pw, name, dob.isoformat(), phone, email, role)
            if ok and nphoto:
                new = q("SELECT id FROM users WHERE username=?", (uname.strip().lower(),), one=True)
                set_profile_photo(new["id"], nphoto.getvalue())
            (st.success if ok else st.error)(msg)


def admin_settings(user):
    page_header("⚙️ Settings & Profile", "Apni admin profile, password aur storage yahan sambhalo")
    t1, t2, t3 = st.tabs(["👤 Meri Profile", "🔒 Password", "💾 Storage"])
    with t1:
        profile_form(user)
    with t2:
        if check_pw("admin123", user["pw_hash"], user["salt"]):
            st.warning("⚠️ Aap abhi default password (admin123) use kar rahe ho. Neeche se turant badlo.")
        password_form(user, "a", expanded=True)
    with t3:
        st.caption(f"Database: `{DB_PATH}`")
        st.caption(f"Files: `{FILES_DIR}`")
        st.caption("Inka backup lete raho.")


def admin_panel(user):
    pages = {"📊 Dashboard": admin_dashboard, "👥 Users": admin_users, "🖼️ Sab Creations": admin_creations,
             "➕ Naya user": admin_new_user}
    choice = st.sidebar.radio("Admin menu", list(pages) + ["⚙️ Settings & Profile"], key="nav_admin")
    if choice == "⚙️ Settings & Profile":
        admin_settings(user)
    else:
        pages[choice]()


# =====================================================================
# 8. APP SHELL
# =====================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@1,700&display=swap');
:root{--pink:#f472b6;--violet:#a78bfa;--gold:#fbbf24;--ink:#f5f3ff;--mute:#a8a3c7;
      --card:rgba(255,255,255,.055);--line:rgba(255,255,255,.11);}
html, body, [class*="css"], .stApp, button, input, textarea {font-family:'Poppins',sans-serif !important;}
.stApp{background:radial-gradient(1100px 600px at 8% -5%,rgba(167,139,250,.28),transparent 60%),
       radial-gradient(900px 520px at 100% 0%,rgba(244,114,182,.20),transparent 55%),
       linear-gradient(180deg,#120a26 0%,#1a1038 55%,#0f0a1f 100%) !important;color:var(--ink);}
.stApp, .stApp p, .stApp label, .stApp span, .stApp li, .stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5
 {color:var(--ink);}
.stApp small, [data-testid="stCaptionContainer"], .stApp [data-testid="stCaptionContainer"] p {color:var(--mute) !important;}
#MainMenu, footer {visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;}
.block-container{padding-top:1.6rem;max-width:1220px;}

/* sidebar */
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#1b1040,#120a2a) !important;border-right:1px solid var(--line);}
section[data-testid="stSidebar"] .stRadio label{border-radius:12px;padding:.45rem .7rem;transition:.15s;}
section[data-testid="stSidebar"] .stRadio label:hover{background:rgba(255,255,255,.07);}
.brand{font-weight:800;font-size:1.25rem;background:linear-gradient(90deg,#f472b6,#a78bfa,#fbbf24);
       -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.4rem;}
.me{display:flex;gap:.7rem;align-items:center;padding:.7rem;border-radius:16px;background:var(--card);border:1px solid var(--line);}
.avatar{width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;
        background:linear-gradient(135deg,#f472b6,#a78bfa);color:#fff;font-size:1.05rem;flex:none;}
.avatar{overflow:hidden}.avatar img{width:100%;height:100%;object-fit:cover}
.hero-av{width:88px;height:88px;border-radius:50%;object-fit:cover;border:3px solid #fff;float:left;margin-right:1.2rem;
         box-shadow:0 8px 24px -8px rgba(0,0,0,.6)}
.me b{display:block;line-height:1.15}.me span.u{color:var(--mute);font-size:.78rem}
.role-chip{display:inline-block;padding:1px 9px;border-radius:999px;font-size:.66rem;font-weight:700;margin-left:6px;
           background:linear-gradient(90deg,#a78bfa,#f472b6);color:#fff;vertical-align:middle;}

/* page header */
.ph{margin:.1rem 0 1.1rem 0;padding-bottom:.8rem;border-bottom:1px solid var(--line);}
.ph h2{margin:0;font-size:1.75rem;font-weight:800;letter-spacing:-.01em;}
.ph p{margin:.25rem 0 0 0;color:var(--mute);font-size:.95rem;}

/* hero */
.hero-big{position:relative;overflow:hidden;border-radius:26px;padding:2rem 2.2rem;margin-bottom:1.2rem;
  background:linear-gradient(120deg,rgba(124,58,237,.75),rgba(244,114,182,.65));border:1px solid rgba(255,255,255,.18);
  box-shadow:0 20px 60px -20px rgba(124,58,237,.7);}
.hero-big:after{content:"🎈 🎉 ✨";position:absolute;right:1.6rem;top:.8rem;font-size:2.2rem;opacity:.9;letter-spacing:.3rem;}
.hero-big h1{margin:0;font-size:2.1rem;font-weight:800;color:#fff;}
.hero-big p{margin:.35rem 0 0 0;color:#ffeefa;font-size:1.02rem;}
.count{display:inline-flex;align-items:baseline;gap:.5rem;margin-top:1rem;padding:.55rem 1.1rem;border-radius:999px;
       background:rgba(0,0,0,.28);border:1px solid rgba(255,255,255,.25);}
.count b{font-size:1.9rem;color:var(--gold);line-height:1}.count span{color:#fff;font-size:.95rem}

/* stat + feature cards */
.grid{display:grid;gap:1rem;margin:.4rem 0 1.1rem 0;}
.g3{grid-template-columns:repeat(3,1fr)}.g5{grid-template-columns:repeat(5,1fr)}
@media(max-width:900px){.g3,.g5{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){.g3,.g5{grid-template-columns:1fr}}
.stat{padding:1.1rem 1.2rem;border-radius:20px;background:var(--card);border:1px solid var(--line);transition:.2s;}
.stat:hover{transform:translateY(-3px);border-color:rgba(244,114,182,.5);}
.stat .ic{font-size:1.5rem}.stat .v{font-size:2rem;font-weight:800;line-height:1.1;margin-top:.25rem;
       background:linear-gradient(90deg,#fff,#fbcfe8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.stat .l{color:var(--mute);font-size:.85rem}
.feat{padding:1.3rem;border-radius:22px;border:1px solid var(--line);min-height:150px;
      background:linear-gradient(160deg,rgba(255,255,255,.08),rgba(255,255,255,.025));transition:.2s;}
.feat:hover{transform:translateY(-4px);box-shadow:0 18px 40px -18px rgba(244,114,182,.55);}
.feat .ic{font-size:2.1rem}.feat h4{margin:.5rem 0 .2rem 0;font-size:1.1rem}.feat p{margin:0;color:var(--mute);font-size:.88rem}

/* auth */
.auth-left h1{font-size:3rem;line-height:1.05;margin:0;font-weight:800;
   background:linear-gradient(90deg,#f472b6,#a78bfa,#fbbf24);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.auth-left .tag{font-family:'Playfair Display',serif;font-style:italic;font-size:1.4rem;color:#fde68a;margin:.5rem 0 1.4rem 0}
.pill{display:flex;gap:.8rem;align-items:center;padding:.8rem 1rem;margin:.55rem 0;border-radius:16px;
      background:var(--card);border:1px solid var(--line);}
.pill .ic{font-size:1.6rem}.pill b{display:block}.pill span{color:var(--mute);font-size:.85rem}

/* widgets */
.stButton>button,.stDownloadButton>button,.stLinkButton>a,[data-testid="stFormSubmitButton"]>button{
  border-radius:12px !important;font-weight:600 !important;border:1px solid var(--line) !important;transition:.15s;}
.stButton>button:hover,.stDownloadButton>button:hover,.stLinkButton>a:hover{transform:translateY(-2px);border-color:var(--pink) !important;}
button[kind="primary"],button[data-testid="stBaseButton-primary"],[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"]{
  background:linear-gradient(90deg,#ec4899,#8b5cf6) !important;border:none !important;color:#fff !important;
  box-shadow:0 10px 24px -10px rgba(236,72,153,.8);}
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input,[data-baseweb="select"]>div{
  border-radius:12px !important;background:rgba(255,255,255,.06) !important;border:1px solid var(--line) !important;color:var(--ink) !important;}
.stTabs [data-baseweb="tab-list"]{gap:.4rem;background:var(--card);padding:.3rem;border-radius:14px;border:1px solid var(--line);}
.stTabs [data-baseweb="tab"]{border-radius:10px;padding:.4rem 1rem;height:auto;}
.stTabs [aria-selected="true"]{background:linear-gradient(90deg,#ec4899,#8b5cf6);color:#fff !important;}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none;}
[data-testid="stForm"]{border-radius:20px;background:var(--card);border:1px solid var(--line);padding:1.2rem;}
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] .stImage){border-radius:20px;}
[data-testid="stExpander"]{border-radius:14px;border:1px solid var(--line);background:var(--card);}
[data-testid="stFileUploaderDropzone"]{border-radius:16px;border:2px dashed rgba(244,114,182,.5);background:rgba(244,114,182,.05);}
[data-testid="stImage"] img,video{border-radius:16px;}
[data-testid="stDataFrame"]{border-radius:16px;overflow:hidden;border:1px solid var(--line);}
hr{border-color:var(--line) !important;}
.stProgress>div>div>div>div{background:linear-gradient(90deg,#ec4899,#8b5cf6);}

/* force dark look even without config.toml */
[data-baseweb="popover"],[data-baseweb="popover"] ul,[data-baseweb="menu"],ul[role="listbox"],[data-baseweb="calendar"]{
  background:#1f1245 !important;color:var(--ink) !important;}
[data-baseweb="popover"] *,[data-baseweb="select"] *,[data-baseweb="calendar"] *{color:var(--ink) !important;}
li[role="option"]:hover,[aria-selected="true"][role="option"]{background:rgba(167,139,250,.25) !important;}
[data-testid="stWidgetLabel"] p,[data-testid="stWidgetLabel"] label,.stRadio label p,.stCheckbox label p,
[data-testid="stExpander"] summary p,[data-testid="stFileUploaderDropzone"] *,[data-testid="stMarkdownContainer"] p,
[data-testid="stMetricValue"],[data-testid="stAlertContainer"] p{color:var(--ink) !important;}
[data-testid="stFileUploaderDropzone"] small{color:var(--mute) !important;}
.stButton>button,.stDownloadButton>button,.stLinkButton>a{background:rgba(255,255,255,.07) !important;color:var(--ink) !important;}
.stNumberInput button{background:rgba(255,255,255,.08) !important;color:var(--ink) !important;}
[data-testid="stToolbar"],[data-testid="stToolbar"] *{color:var(--ink) !important;}
</style>
"""


def auth_page():
    left, mid = st.columns([1.15, 1], gap="large")
    with left:
        st.markdown(
            '<div class="auth-left"><h1>Birthday<br>Studio</h1><div style="font-size:2.6rem;margin-top:-.2rem">🎂</div>'
            '<div class="tag">Har yaad, ek khoobsurat tohfa</div>'
            '<div class="pill"><div class="ic">🎴</div><div><b>Birthday Card</b><span>HD card, apni photo ke saath</span></div></div>'
            '<div class="pill"><div class="ic">📖</div><div><b>Birthday Album</b><span>Polaroid pages, PDF download</span></div></div>'
            '<div class="pill"><div class="ic">🎬</div><div><b>Birthday Video</b><span>Music + zoom + confetti wala video</span></div></div>'
            '</div>', unsafe_allow_html=True)
    with mid:
        t1, t2 = st.tabs(["🔑 Login", "✨ Naya account"])
        with t1:
            with st.form("login"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True, type="primary"):
                    row, err = authenticate(u, p)
                    if row:
                        st.session_state["uid"] = row["id"]
                        st.rerun()
                    else:
                        st.error(err)
            st.caption("Admin aur User dono yahin se login karte hain — role apne aap pehchan liya jata hai.")
        with t2:
            with st.form("signup"):
                name = st.text_input("Poora naam")
                uname = st.text_input("Username (a-z, 0-9, _ .)")
                c1, c2 = st.columns(2)
                pw = c1.text_input("Password (min 6)", type="password")
                pw2 = c2.text_input("Password dobara", type="password")
                dob = st.date_input("Janamdin", date(2000, 1, 1), min_value=date(1920, 1, 1), max_value=date.today())
                phone = st.text_input("Phone (optional)")
                email = st.text_input("Email (optional)")
                sphoto = st.file_uploader("📸 Profile photo (card, album, video me kaam aayegi)",
                                          type=["jpg", "jpeg", "png", "webp"], key="su_photo")
                if st.form_submit_button("Account banao", use_container_width=True, type="primary"):
                    if pw != pw2:
                        st.error("Dono password same nahi hain.")
                    else:
                        ok, msg = create_user(uname, pw, name, dob.isoformat(), phone, email, "user")
                        if ok:
                            row, _ = authenticate(uname, pw)
                            if sphoto:
                                set_profile_photo(row["id"], sphoto.getvalue())
                            st.session_state["uid"] = row["id"]
                            st.rerun()
                        else:
                            st.error(msg)


def ensure_theme_config():
    """Dark theme config khud bana do (agle restart se pakka lagta hai). CSS is ke bina bhi dark look deta hai."""
    try:
        cfg = Path.cwd() / ".streamlit" / "config.toml"
        if not cfg.exists():
            cfg.parent.mkdir(exist_ok=True)
            cfg.write_text('[theme]\nbase = "dark"\nprimaryColor = "#ec4899"\nbackgroundColor = "#140b2b"\n'
                           'secondaryBackgroundColor = "#1f1245"\ntextColor = "#f5f3ff"\n')
    except Exception:
        pass


def main():
    ensure_theme_config()
    st.set_page_config(page_title="Birthday Studio", page_icon="🎂", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    init_db()
    uid = st.session_state.get("uid")
    user = get_user(uid) if uid else None
    if user is not None and not user["active"]:
        user = None
    if user is None:
        st.session_state.pop("uid", None)
        auth_page()
        return
    with st.sidebar:
        st.markdown('<div class="brand">🎂 Birthday Studio</div>', unsafe_allow_html=True)
        chip = "ADMIN" if user["role"] == "admin" else "USER"
        st.markdown(f'<div class="me">{avatar_html(user)}<div><b>{user["full_name"]}'
                    f'<span class="role-chip">{chip}</span></b><span class="u">@{user["username"]}</span></div></div>',
                    unsafe_allow_html=True)
        st.write("")
    if user["role"] == "admin":
        admin_panel(user)
    else:
        user_panel(user)
    with st.sidebar:
        st.divider()
        if st.button("🚪 Logout", use_container_width=True, key="logout"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


if __name__ == "__main__":
    main()
