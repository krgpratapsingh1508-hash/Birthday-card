"""
🎂 Birthday Studio  —  Admin panel + User panel
User: apni ID se Birthday Card, Album (PDF) aur Video banata hai.
Admin: sare users ki jankari, unki banayi cheezein, ID band/chalu, password reset.

Run:  streamlit run app.py
Pehla admin login:  admin / admin123   (login ke baad turant password badal do)
"""
import io
import re
import urllib.parse
import zipfile
from datetime import date

import pandas as pd
import streamlit as st
from PIL import Image

import card_engine as ce
import db
import media

st.set_page_config(page_title="Birthday Studio", page_icon="🎂", layout="wide")
db.init_db()

st.markdown("""
<style>
#MainMenu, footer {visibility: hidden;}
.block-container {padding-top: 1.4rem; max-width: 1200px;}
.hero {text-align:center; padding: 4px 0 14px 0;}
.hero h1 {font-size: 2.4rem; margin: 0; background: linear-gradient(90deg,#f472b6,#a78bfa,#fbbf24);
          -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;}
.hero p {color:#94a3b8; margin: 4px 0 0 0;}
.stDownloadButton button, .stLinkButton a {width:100%; border-radius: 12px; font-weight: 600;}
.stButton button {border-radius: 12px; font-weight: 600;}
.badge {display:inline-block; padding:2px 10px; border-radius:999px; font-size:.78rem; font-weight:700;}
.b-admin {background:#fde68a; color:#78350f;} .b-user {background:#c4b5fd; color:#3b0764;}
.card-box {border:1px solid rgba(148,163,184,.3); border-radius:16px; padding:14px 16px; margin-bottom:10px;}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- helpers
def ss(key, default=None):
    return st.session_state.get(key, default)


def hero(sub):
    st.markdown(f'<div class="hero"><h1>🎂 Birthday Studio</h1><p>{sub}</p></div>', unsafe_allow_html=True)


def safe_name(txt, fallback="file"):
    return re.sub(r"[^\w\-]+", "_", (txt or "").strip()) or fallback


def split_lines(txt):
    return [l.strip() for l in (txt or "").split("\n")]


def logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()


# ---------------------------------------------------------------- AUTH PAGE
def auth_page():
    hero("Apni ID banao — Card, Album aur Video sab ek jagah")
    _, mid, _ = st.columns([1, 1.3, 1])
    with mid:
        t_login, t_reg = st.tabs(["🔐 Login", "✨ Naya Account"])
        with t_login:
            who = st.radio("Kaun?", ["👤 User", "🛡️ Admin"], horizontal=True, label_visibility="collapsed")
            with st.form("login_form"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                go = st.form_submit_button("Login", use_container_width=True, type="primary")
            if go:
                user, err = db.login(u, p)
                if err:
                    st.error(err)
                elif who.endswith("Admin") and user["role"] != "admin":
                    st.error("Ye Admin ID nahi hai. 'User' chuno.")
                elif who.endswith("User") and user["role"] == "admin":
                    st.error("Ye Admin ID hai. 'Admin' chuno.")
                else:
                    st.session_state.user = user
                    st.rerun()
        with t_reg:
            with st.form("reg_form"):
                c1, c2 = st.columns(2)
                ru = c1.text_input("Username *", help="3-30 akshar: A-Z, 0-9, _ .")
                rp = c2.text_input("Password * (min 6)", type="password")
                fn = st.text_input("Poora naam *")
                c3, c4 = st.columns(2)
                ph = c3.text_input("Mobile number")
                em = c4.text_input("Email")
                c5, c6 = st.columns(2)
                city = c5.text_input("Sheher")
                dob = c6.date_input("Janamdin", value=date(2000, 1, 1), min_value=date(1920, 1, 1),
                                    max_value=date.today())
                go = st.form_submit_button("Account banao", use_container_width=True, type="primary")
            if go:
                if not fn.strip():
                    st.error("Naam zaroori hai.")
                else:
                    ok, msg = db.register(ru, rp, fn, ph, em, city, dob.isoformat())
                    (st.success if ok else st.error)(msg)


# ---------------------------------------------------------------- SIDEBAR
def sidebar(user):
    with st.sidebar:
        role = user["role"]
        st.markdown(f"### {user['full_name'] or user['username']}")
        st.markdown(f'<span class="badge b-{role}">{role.upper()}</span> &nbsp; @{user["username"]}',
                    unsafe_allow_html=True)
        st.divider()
        with st.expander("🔑 Password badlo"):
            with st.form("pw_form", clear_on_submit=True):
                old = st.text_input("Purana password", type="password")
                new = st.text_input("Naya password", type="password")
                go = st.form_submit_button("Badlo")
            if go:
                chk, _ = db.login(user["username"], old)
                if not chk:
                    st.error("Purana password galat hai.")
                else:
                    ok, msg = db.set_password(user["id"], new)
                    (st.success if ok else st.error)(msg)
        if st.button("🚪 Logout", use_container_width=True):
            logout()


# ---------------------------------------------------------------- USER: pieces
def theme_and_basics(prefix, user):
    c1, c2 = st.columns(2)
    name = c1.text_input("Kiske liye? (Naam)", user["full_name"].split(" ")[0] if user["full_name"] else "",
                         key=f"{prefix}_name")
    age = c2.number_input("Umar", 1, 120, 22, key=f"{prefix}_age")
    theme = st.radio("Theme", list(ce.THEMES.keys()), horizontal=True, key=f"{prefix}_theme")
    choice = st.selectbox("Wish chuno", list(ce.WISHES.keys()), key=f"{prefix}_wc")
    wish = st.text_area("Wish (edit kar sakte ho)", ce.WISHES[choice], height=90, key=f"{prefix}_wish_{choice}",
                        placeholder="Yahan apna message likho…")
    sender = st.text_input("Kisne bheja?", user["full_name"] or "", key=f"{prefix}_sender")
    return name, int(age), theme, wish, sender


def user_card_tab(user):
    form, prev = st.columns([1, 1.05], gap="large")
    with form:
        name, age, theme, wish, sender = theme_and_basics("card", user)
        relation = st.text_input("Rishta (optional)", "Best Friend", key="card_rel")
        show_age = st.checkbox("Card pe umar dikhao", True, key="card_showage")
        photo = st.file_uploader("Photo (gol frame me auto-fit)", type=["jpg", "jpeg", "png", "webp"], key="card_photo")
        focus = st.slider("Photo upar ↔ neeche", 0.0, 1.0, 0.4, 0.05, key="card_focus") if photo else 0.4
        if st.button("🎊 Confetti naya karo", key="card_seed"):
            st.session_state.seed = ss("seed", 7) + 1

    @st.cache_data(show_spinner=False, max_entries=20)
    def cached(*a):
        return ce.to_bytes(ce.render_card(*a))

    png = cached(theme, name, age, show_age, relation, wish, sender, photo.getvalue() if photo else None,
                 focus, ss("seed", 7))
    with prev:
        st.image(png, use_container_width=True)
        sn = safe_name(name, "card")
        a, b = st.columns(2)
        a.download_button("⬇️ PNG (HD)", png, f"{sn}_birthday_card.png", "image/png", key="card_dl_png")
        jpg = ce.to_bytes(Image.open(io.BytesIO(png)), "JPEG")
        b.download_button("⬇️ JPG (chhoti)", jpg, f"{sn}_birthday_card.jpg", "image/jpeg", key="card_dl_jpg")
        if st.button("💾 Meri Gallery me save karo", use_container_width=True, key="card_save"):
            db.save_creation(user["id"], "card", f"{name} - Card", png, "png")
            st.success("Gallery me save ho gaya ✅")
        msg = f"Happy Birthday {name.strip()}! 🎂🎉 Ye card sirf tumhare liye ❤️"
        st.link_button("📲 WhatsApp pe bhejo", "https://wa.me/?text=" + urllib.parse.quote(msg))


def user_album_tab(user):
    st.caption("Kai photos daalo — khoobsurat polaroid pages wala Birthday Album + PDF ban jayega.")
    form, prev = st.columns([1, 1.2], gap="large")
    with form:
        name, age, theme, wish, sender = theme_and_basics("alb", user)
        files = st.file_uploader("Photos (2 se 40)", type=["jpg", "jpeg", "png", "webp"],
                                 accept_multiple_files=True, key="alb_files")
        caps = st.text_area("Photo ke neeche likhna ho to (har line = ek photo, optional)", height=80, key="alb_caps")
        go = st.button("📖 Album banao", type="primary", use_container_width=True, key="alb_go",
                       disabled=not files)
        if go:
            if len(files) > 40:
                st.warning("Pehli 40 photos hi li gayi.")
            bar = st.progress(0.0, "Shuru...")
            pages = media.render_album(theme, name, age, [f.getvalue() for f in files[:40]], wish, sender,
                                       split_lines(caps), progress=lambda p, m: bar.progress(min(p, 1.0), m))
            bar.empty()
            st.session_state.album = dict(pages=pages, pdf=media.pages_to_pdf(pages), name=name)
    with prev:
        res = ss("album")
        if not res:
            st.info("Photos daalo aur 'Album banao' dabao. Yahan preview dikhega.")
            return
        pdf, pages, nm = res["pdf"], res["pages"], res["name"]
        a, b = st.columns(2)
        a.download_button("⬇️ Album PDF", pdf, f"{safe_name(nm)}_album.pdf", "application/pdf", key="alb_dl_pdf")
        zbuf = io.BytesIO()
        with zipfile.ZipFile(zbuf, "w") as z:
            for i, p in enumerate(pages, 1):
                pb = io.BytesIO()
                p.save(pb, "JPEG", quality=92)
                z.writestr(f"page_{i:02d}.jpg", pb.getvalue())
        b.download_button("⬇️ Sab pages (ZIP)", zbuf.getvalue(), f"{safe_name(nm)}_album_pages.zip",
                          "application/zip", key="alb_dl_zip")
        if st.button("💾 Meri Gallery me save karo", use_container_width=True, key="alb_save"):
            cover = io.BytesIO()
            pages[0].save(cover, "JPEG", quality=88)
            db.save_creation(user["id"], "album", f"{nm} - Album ({len(pages)} pages)", cover.getvalue(), "jpg",
                             pdf, "pdf")
            st.success("Gallery me save ho gaya ✅")
        cols = st.columns(2)
        for i, p in enumerate(pages):
            cols[i % 2].image(p, caption=("Cover" if i == 0 else f"Page {i + 1}"), use_container_width=True)


def user_video_tab(user):
    st.caption("Photos se vertical (WhatsApp Status / Reels size) Birthday Video — animation, transitions aur music ke saath.")
    form, prev = st.columns([1, 1], gap="large")
    with form:
        name, age, theme, wish, sender = theme_and_basics("vid", user)
        files = st.file_uploader("Photos (1 se 15)", type=["jpg", "jpeg", "png", "webp"],
                                 accept_multiple_files=True, key="vid_files")
        caps = st.text_area("Har photo par likhna ho to (har line = ek photo, optional)", height=80, key="vid_caps")
        secs = st.slider("Ek photo kitni der (seconds)", 2.0, 6.0, 3.2, 0.2, key="vid_secs")
        mus = st.radio("Music", ["🎵 Built-in khushi wali dhun", "📁 Apna MP3/audio", "🔇 Bina music"], key="vid_mus")
        audio = st.file_uploader("Audio file", type=["mp3", "wav", "m4a", "aac"], key="vid_audio") \
            if mus.startswith("📁") else None
        est = 4.2 + 5.5 + max(1, len(files) if files else 1) * (secs - 0.7)
        st.caption(f"Video lagbhag {est:.0f} second ki banegi. Render me {max(1, int(est / 3))}-{max(2, int(est / 1.5))} second lag sakte hain.")
        go = st.button("🎬 Video banao", type="primary", use_container_width=True, key="vid_go", disabled=not files)
        if go:
            if len(files) > 15:
                st.warning("Pehli 15 photos hi li gayi.")
            bar = st.progress(0.0, "Shuru...")
            music = "builtin" if mus.startswith("🎵") else ("upload" if audio else "none")
            data = media.render_video(theme, name, age, [f.getvalue() for f in files[:15]], wish, sender,
                                      split_lines(caps), secs, music, audio.getvalue() if audio else None,
                                      progress=lambda p, m: bar.progress(min(p, 1.0), m))
            bar.empty()
            st.session_state.video = dict(data=data, name=name)
    with prev:
        res = ss("video")
        if not res:
            st.info("Photos daalo aur 'Video banao' dabao. Video yahan chalega.")
            return
        st.video(res["data"])
        st.download_button("⬇️ Video download (MP4)", res["data"], f"{safe_name(res['name'])}_birthday_video.mp4",
                           "video/mp4", key="vid_dl")
        if st.button("💾 Meri Gallery me save karo", use_container_width=True, key="vid_save"):
            db.save_creation(user["id"], "video", f"{res['name']} - Video", res["data"], "mp4")
            st.success("Gallery me save ho gaya ✅")
        st.caption("WhatsApp: download karke Status ya chat me attach kar do.")


def gallery_view(items, can_delete_uid=None, key_prefix="g"):
    if not items:
        st.info("Abhi kuch nahi hai.")
        return
    icon = {"card": "🎂 Card", "album": "📖 Album", "video": "🎬 Video"}
    cols = st.columns(3)
    for i, it in enumerate(items):
        with cols[i % 3]:
            st.markdown('<div class="card-box">', unsafe_allow_html=True)
            st.markdown(f"**{icon[it['kind']]}** — {it['title']}")
            st.caption(f"{it.get('username', '')} · {it['created_at']}")
            data = db.read_file(it["path"])
            if it["kind"] == "video":
                st.video(data)
                st.download_button("⬇️ Video", data, f"video_{it['id']}.mp4", "video/mp4", key=f"{key_prefix}_dl{it['id']}")
            elif it["kind"] == "album":
                st.image(data, use_container_width=True)
                st.download_button("⬇️ PDF", db.read_file(it["extra_path"]), f"album_{it['id']}.pdf",
                                   "application/pdf", key=f"{key_prefix}_dl{it['id']}")
            else:
                st.image(data, use_container_width=True)
                st.download_button("⬇️ PNG", data, f"card_{it['id']}.png", "image/png", key=f"{key_prefix}_dl{it['id']}")
            if can_delete_uid is not None or key_prefix.startswith("adm"):
                if st.button("🗑️ Delete", key=f"{key_prefix}_del{it['id']}"):
                    db.delete_creation(it["id"], can_delete_uid)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


def user_profile_tab(user):
    st.subheader("Meri jankari")
    with st.form("prof"):
        c1, c2 = st.columns(2)
        fn = c1.text_input("Poora naam", user["full_name"])
        ph = c2.text_input("Mobile", user["phone"])
        c3, c4 = st.columns(2)
        em = c3.text_input("Email", user["email"])
        city = c4.text_input("Sheher", user["city"])
        try:
            dv = date.fromisoformat(user["dob"]) if user["dob"] else date(2000, 1, 1)
        except ValueError:
            dv = date(2000, 1, 1)
        dob = st.date_input("Janamdin", dv, min_value=date(1920, 1, 1), max_value=date.today())
        go = st.form_submit_button("Save karo", type="primary")
    if go:
        db.update_profile(user["id"], fn.strip(), ph.strip(), em.strip(), city.strip(), dob.isoformat())
        st.session_state.user = db.get_user(user["id"])
        st.success("Jankari update ho gayi ✅")
        st.rerun()
    mine = db.list_creations(user["id"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Cards", sum(m["kind"] == "card" for m in mine))
    c2.metric("Albums", sum(m["kind"] == "album" for m in mine))
    c3.metric("Videos", sum(m["kind"] == "video" for m in mine))


def user_panel(user):
    hero(f"Namaste {user['full_name'] or user['username']}! Aaj kya banana hai?")
    t0, t1, t2, t3, t4 = st.tabs(["🎂 Card", "📖 Album", "🎬 Video", "🗂️ Meri Gallery", "👤 Profile"])
    with t0:
        user_card_tab(user)
    with t1:
        user_album_tab(user)
    with t2:
        user_video_tab(user)
    with t3:
        kind = st.radio("Dikhao", ["Sab", "card", "album", "video"], horizontal=True, key="gal_kind")
        gallery_view(db.list_creations(user["id"], None if kind == "Sab" else kind), can_delete_uid=user["id"], key_prefix="ug")
    with t4:
        user_profile_tab(user)


# ---------------------------------------------------------------- ADMIN
def users_frame(users):
    rows = [{
        "ID": u["id"], "Username": u["username"], "Naam": u["full_name"], "Mobile": u["phone"],
        "Email": u["email"], "Sheher": u["city"], "Janamdin": u["dob"],
        "Cards": u["cards"], "Albums": u["albums"], "Videos": u["videos"],
        "Status": "Active" if u["active"] else "Band", "Bana": u["created_at"], "Last login": u["last_login"],
    } for u in users]
    return pd.DataFrame(rows)


def admin_dashboard():
    s = db.stats()
    c = st.columns(5)
    c[0].metric("Total Users", s["users"])
    c[1].metric("Active", s["active"])
    c[2].metric("Cards", s["cards"])
    c[3].metric("Albums", s["albums"])
    c[4].metric("Videos", s["videos"])
    st.subheader("Naye users")
    df = users_frame(db.list_users())
    if df.empty:
        st.info("Abhi koi user nahi hai.")
    else:
        st.dataframe(df.head(8), use_container_width=True, hide_index=True)


def admin_users():
    users = db.list_users()
    q = st.text_input("🔎 Search (naam / username / mobile / sheher)", key="adm_q")
    if q:
        ql = q.lower()
        users = [u for u in users if ql in " ".join(str(u[k]) for k in ("username", "full_name", "phone", "email", "city")).lower()]
    df = users_frame(users)
    st.dataframe(df, use_container_width=True, hide_index=True)
    if not df.empty:
        st.download_button("⬇️ Users list (CSV/Excel me khulega)", df.to_csv(index=False).encode("utf-8-sig"),
                           "users.csv", "text/csv", key="adm_csv")


def admin_user_detail():
    users = db.list_users()
    if not users:
        st.info("Abhi koi user nahi hai.")
        return
    opts = {f"{u['full_name'] or '-'}  (@{u['username']})": u["id"] for u in users}
    pick = st.selectbox("User chuno", list(opts.keys()), key="adm_pick")
    u = db.get_user(opts[pick])
    left, right = st.columns([1, 1.4], gap="large")
    with left:
        st.markdown(f"#### {u['full_name'] or u['username']}")
        st.write(f"**Username:** {u['username']}")
        st.write(f"**Mobile:** {u['phone'] or '-'}")
        st.write(f"**Email:** {u['email'] or '-'}")
        st.write(f"**Sheher:** {u['city'] or '-'}")
        st.write(f"**Janamdin:** {u['dob'] or '-'}")
        st.write(f"**Account bana:** {u['created_at']}")
        st.write(f"**Last login:** {u['last_login'] or '-'}")
        st.write(f"**Status:** {'🟢 Active' if u['active'] else '🔴 Band'}")
        if u["active"]:
            if st.button("🚫 ID band karo", key="adm_off"):
                db.set_active(u["id"], False)
                st.rerun()
        else:
            if st.button("✅ ID chalu karo", key="adm_on"):
                db.set_active(u["id"], True)
                st.rerun()
        with st.expander("🔑 Password reset"):
            npw = st.text_input("Naya password", type="password", key="adm_npw")
            if st.button("Reset karo", key="adm_reset"):
                ok, msg = db.set_password(u["id"], npw)
                (st.success if ok else st.error)(msg)
        with st.expander("🗑️ User delete karo (wapas nahi aayega)"):
            sure = st.checkbox("Haan, is user aur uski sari files delete karo", key="adm_sure")
            if st.button("Delete", disabled=not sure, key="adm_delu"):
                db.delete_user(u["id"])
                st.rerun()
    with right:
        st.markdown("#### Is user ki banayi cheezein")
        gallery_view(db.list_creations(u["id"]), key_prefix="adm_u")


def admin_all_creations():
    kind = st.radio("Dikhao", ["Sab", "card", "album", "video"], horizontal=True, key="adm_kind")
    gallery_view(db.list_creations(None, None if kind == "Sab" else kind)[:60], key_prefix="adm_all")
    st.caption("Sabse naye 60 dikhaye gaye.")


def admin_add_user():
    with st.form("adm_add", clear_on_submit=True):
        c1, c2 = st.columns(2)
        u = c1.text_input("Username *")
        p = c2.text_input("Password * (min 6)", type="password")
        fn = st.text_input("Poora naam *")
        c3, c4, c5 = st.columns(3)
        ph = c3.text_input("Mobile")
        em = c4.text_input("Email")
        city = c5.text_input("Sheher")
        go = st.form_submit_button("User banao", type="primary")
    if go:
        if not fn.strip():
            st.error("Naam zaroori hai.")
        else:
            ok, msg = db.register(u, p, fn, ph, em, city, "")
            (st.success if ok else st.error)(msg)


def admin_panel(user):
    hero("Admin Panel — poora control aapke haath me")
    if db.check_pw(db.DEFAULT_ADMIN_PASS, db.get_user(user["id"])["password"]):
        st.warning("⚠️ Abhi default password (admin123) chal raha hai. Sidebar me '🔑 Password badlo' se turant badlo.")
    t = st.tabs(["📊 Dashboard", "👥 Sare Users", "🔍 User ki detail", "🗂️ Sab creations", "➕ User jodo"])
    with t[0]:
        admin_dashboard()
    with t[1]:
        admin_users()
    with t[2]:
        admin_user_detail()
    with t[3]:
        admin_all_creations()
    with t[4]:
        admin_add_user()


# ---------------------------------------------------------------- ROUTER
def main():
    user = ss("user")
    if not user:
        auth_page()
        return
    fresh = db.get_user(user["id"])
    if not fresh or not fresh["active"]:
        st.session_state.clear()
        st.error("Ye ID ab chalu nahi hai.")
        st.rerun()
    st.session_state.user = user = fresh
    sidebar(user)
    (admin_panel if user["role"] == "admin" else user_panel)(user)


main()
