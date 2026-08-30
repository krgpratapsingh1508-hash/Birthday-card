import streamlit as st

# 1. Page Configuration
st.set_page_config(page_title="AI Birthday Studio Pro", page_icon="🎬", layout="wide")

# Theme CSS
st.markdown("""
    <style>
    .main { background-color: #0b0c10; color: #c5c6c7; }
    h1, h2, h3 { color: #66fcf1 !important; font-family: 'Arial', sans-serif; }
    .stButton>button { background-color: #45f3ff; color: black; font-weight: bold; border-radius: 8px; width: 100%; }
    .card-output { background-color: #1f2833; padding: 30px; border-radius: 15px; text-align: center; border: 3px solid #66fcf1; }
    .share-box { background-color: #000000; padding: 15px; border-radius: 10px; border: 1px dashed #45f3ff; margin-top: 15px; text-align: center;}
    </style>
""", unsafe_allow_html=True)

# 2. Session State Memory
if "master_name" not in st.session_state:
    st.session_state.master_name = "Sunita"
if "master_msg" not in st.session_state:
    st.session_state.master_msg = "Wishing you a fantastic year ahead!"
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#1f2833"

# 3. Sidebar Control
st.sidebar.title("🔐 Control Center")
current_role = st.sidebar.selectbox("Choose Workspace", ["👤 Client Live View", "⚙️ Admin Control Panel"])

is_master_admin = False
if current_role == "⚙️ Admin Control Panel":
    st.sidebar.subheader("Master Verification")
    adm_user = st.sidebar.text_input("Admin ID", placeholder="Username")
    adm_pass = st.sidebar.text_input("Password", type="password", placeholder="Password")
    if adm_user == "admin" and adm_pass == "birthday123":
        st.sidebar.success("🔑 Admin Override: Enabled!")
        is_master_admin = True
    elif adm_user != "" or adm_pass != "":
        st.sidebar.error("❌ Invalid Credentials")

st.title("⚡ AI Birthday Studio & Card Engine")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["⚙️ PANEL 1: Admin Control", "🖼️ PANEL 2: Image Card Maker", "🎬 PANEL 3: 4-Photo Video Mixer"])

# =====================================================================
# PANEL 1: ADMIN WORKSPACE
# =====================================================================
with tab1:
    st.header("⚙️ Master Administrative Console")
    if is_master_admin:
        adm_name = st.text_input("Set Default Name:", st.session_state.master_name)
        adm_msg = st.text_area("Set Default Message:", st.session_state.master_msg)
        adm_col = st.color_picker("Override Card Color:", st.session_state.bg_color)
        if st.button("💾 Apply Configuration"):
            st.session_state.master_name = adm_name
            st.session_state.master_msg = adm_msg
            st.session_state.bg_color = adm_col
            st.success("🎉 Global settings updated successfully!")
    else:
        st.warning("⚠️ Access Restricted. Please log in from the sidebar.")

# =====================================================================
# PANEL 2: PHOTO CARD RENDER
# =====================================================================
with tab2:
    st.header("🖼️ Image Card Maker")
    c1, c2 = st.columns(2)
    with c1:
        target_name = st.text_input("Enter Name:", st.session_state.master_name, key="p2_name")
        custom_wish = st.text_area("Custom Wish Message:", st.session_state.master_msg, key="p2_wish")
        card_theme = st.color_picker("Pick Backdrop Color:", st.session_state.bg_color, key="p2_color")
        card_photo = st.file_uploader("Upload Portrait Photo:", type=["jpg","png","jpeg"], key="p2_img")
        process_card = st.button("✨ Render Custom Card")
        
    with c2:
        if process_card:
            st.balloons()
            st.markdown(f"""
                <div style="background-color: {card_theme}; padding: 35px; border-radius: 15px; text-align: center; border: 3px solid #66fcf1;">
                    <h1 style="color: #66fcf1 !important; font-size: 38px;">🎉 HAPPY BIRTHDAY 🎉</h1>
                    <h2 style="color: #ffffff !important;">👑 {target_name} 👑</h2>
                    <p style="color: #e5e5e5; font-size: 18px;">"{custom_wish}"</p>
                </div>
            """, unsafe_allow_html=True)
            if card_photo:
                st.image(card_photo, use_container_width=True)
                
            st.markdown("<div class='share-box'>", unsafe_allow_html=True)
            st.subheader("🔗 Shareable Card Link Generated!")
            mock_url = f"https://streamlit.app{target_name.replace(' ', '%20')}"
            st.code(mock_url, language="text")
            
            # Fixed HTML button structure
            wa_link = f"https://whatsapp.com{target_name}!%20👉%20{mock_url}"
            st.markdown(f'<a href="{wa_link}" target="_blank"><button style="background-color:#25D366; color:white; border-radius:8px; padding:10px; width:100%; border:none; font-weight:bold;">📲 Send Card Via WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# PANEL 3: 4-PHOTO VIDEO MIXER
# =====================================================================
with tab3:
    st.header("🎬 4-Photo Video & Music Mixer")
    v1, v2 = st.columns(2)
    with v1:
        vid_name = st.text_input("Type Name for Custom Song Track:", st.session_state.master_name, key="p3_name")
        song_track = st.selectbox("🎵 Select Birthday Track:", [
            f"Happy Birthday to You ({vid_name} Edition)", 
            f"DJ Remix Birthday Beats ({vid_name} Mix)"
        ])
        uploaded_photos = st.file_uploader("Upload 2 to 4 Images for Slideshow:", type=["jpg","png","jpeg"], accept_multiple_files=True)
        process_video = st.button("🚀 Compile & Render Video")
        
    with v2:
        if process_video:
            if uploaded_photos and len(uploaded_photos) >= 2:
                if len(uploaded_photos) > 4:
                    uploaded_photos = uploaded_photos[:4]
                st.snow()
                st.success(f"🎵 Song Synced: '{song_track}'")
                st.audio("https://soundhelix.com", format="audio/mp3")
                
                st.markdown("<div class='card-output'><h4>🎞️ Slideshow Preview Feed</h4><br>", unsafe_allow_html=True)
                img_cols = st.columns(len(uploaded_photos))
                for idx, img_file in enumerate(uploaded_photos):
                    with img_cols[idx]:
                        st.image(img_file, use_container_width=True)
                st.markdown(f"<h2 style='color:#45f3ff !important;'>🎉 Happy Birthday to {vid_name}! 🎉</h2></div>", unsafe_allow_html=True)
                
                st.markdown("<div class='share-box'>", unsafe_allow_html=True)
                st.subheader("🔗 Shareable Video Link Generated!")
                video_mock_url = f"https://streamlit.app{vid_name.replace(' ', '%20')}"
                st.code(video_mock_url, language="text")
                
                # Fixed HTML button structure
                vid_wa = f"https://whatsapp.com{vid_name}!%20👉%20{video_mock_url}"
                st.markdown(f'<a href="{vid_wa}" target="_blank"><button style="background-color:#25D366; color:white; border-radius:8px; padding:10px; width:100%; border:none; font-weight:bold;">📲 Send Video Song Via WhatsApp</button></a>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("❌ Kam se kam 2 se 4 photos upload karein!")
            
