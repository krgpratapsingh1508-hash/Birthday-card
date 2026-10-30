"""
🎂 Birthday Card Studio
Photo + naam + wish daalo -> real PNG birthday card banao, download karo, WhatsApp pe bhejo.
"""
import io
import math
import random
import re
import urllib.parse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

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
# 3. STREAMLIT UI
# =====================================================================
def main():
    import streamlit as st

    st.set_page_config(page_title="Birthday Card Studio", page_icon="🎂", layout="wide")

    st.markdown("""
        <style>
        #MainMenu, footer {visibility: hidden;}
        .block-container {padding-top: 1.6rem; max-width: 1150px;}
        .hero {text-align:center; padding: 6px 0 18px 0;}
        .hero h1 {font-size: 2.3rem; margin: 0; background: linear-gradient(90deg,#f472b6,#a78bfa,#fbbf24);
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;}
        .hero p {color:#94a3b8; margin: 4px 0 0 0;}
        .stDownloadButton button, .stLinkButton a {width:100%; border-radius: 12px; font-weight: 600;}
        </style>
        <div class="hero"><h1>🎂 Birthday Card Studio</h1>
        <p>Photo, naam aur wish daalo — card turant ban jayega</p></div>
    """, unsafe_allow_html=True)

    if "seed" not in st.session_state:
        st.session_state.seed = 7

    form, preview = st.columns([1, 1.05], gap="large")

    with form:
        st.subheader("1️⃣  Kiske liye?")
        name = st.text_input("Naam", "Sunita")
        c1, c2 = st.columns(2)
        age = c1.number_input("Umar", 1, 120, 22)
        show_age = c2.checkbox("Card pe umar dikhao", True)
        relation = st.text_input("Rishta (optional)", "Best Friend")

        st.subheader("2️⃣  Wish")
        choice = st.selectbox("Wish chuno", list(WISHES.keys()))
        if WISHES[choice]:
            wish = st.text_area("Wish edit kar sakte ho", WISHES[choice], height=95)
        else:
            wish = st.text_area("Apni wish likho", "", height=95, placeholder="Yahan apna message likho…")
        sender = st.text_input("Kisne bheja? (optional)", "")

        st.subheader("3️⃣  Style & Photo")
        theme = st.radio("Theme", list(THEMES.keys()), horizontal=True, label_visibility="collapsed")
        photo = st.file_uploader("Photo upload karo (gol frame me auto-fit hogi)", type=["jpg", "jpeg", "png", "webp"])
        focus_y = 0.4
        if photo:
            focus_y = st.slider("Photo upar ↔ neeche adjust karo", 0.0, 1.0, 0.4, 0.05,
                                help="Face frame me sahi na aaye to isse adjust karo")
        if st.button("🎊 Confetti naya karo"):
            st.session_state.seed += 1

    @st.cache_data(show_spinner=False, max_entries=24)
    def cached_render(*args):
        return to_bytes(render_card(*args))

    photo_bytes = photo.getvalue() if photo else None
    png = cached_render(theme, name, int(age), show_age, relation, wish, sender,
                        photo_bytes, focus_y, st.session_state.seed)

    with preview:
        st.image(png, use_container_width=True)
        safe = re.sub(r"[^\w\-]+", "_", name.strip() or "card")
        d1, d2 = st.columns(2)
        d1.download_button("⬇️ PNG download (HD)", png, f"{safe}_birthday_card.png", "image/png")
        jpg = to_bytes(Image.open(io.BytesIO(png)), "JPEG")
        d2.download_button("⬇️ JPG (chhoti file)", jpg, f"{safe}_birthday_card.jpg", "image/jpeg")
        msg = f"Happy Birthday {name.strip()}! 🎂🎉 Ye card sirf tumhare liye ❤️"
        st.link_button("📲 WhatsApp pe bhejo", "https://wa.me/?text=" + urllib.parse.quote(msg))
        st.caption("Pehle card download karo, phir WhatsApp me attach karke bhej do.")


if __name__ == "__main__":
    main()
