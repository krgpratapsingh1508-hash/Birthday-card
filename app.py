import streamlit as st
import base64
from PIL import Image

# 1. Page Configuration & Aesthetic Layout
st.set_page_config(page_title="AI Birthday Studio Pro", page_icon="🎬", layout="wide")

# Theme Engineering (Pro Dark Video Editor Look)
st.markdown("""
    <style>
    .main { background-color: #0b0c10; color: #c5c6c7; }
    h1, h2, h3 { color: #66fcf1 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stButton>button { background-color: #45f3ff; color: black; font-weight: bold; border-radius: 8px; width: 100%; border: none;}
    .stButton>button:hover { background-color: #1f9c9c; color: white; }
    .card-output { background-color: #1f2833; padding: 30px; border-radius: 15px; text-align: center; border: 3px solid #66fcf1; box-shadow: 0px 10px 30px rgba(102, 252, 241, 0.3); }
    .share-box { background-color: #000000; padding: 15px; border-radius: 10px; border: 1px dashed #45f3ff; margin-top: 15px; text-align: center;}
    </style>
""", unsafe_allow_html=True)

# 2. Application Engine Memory (Session State Setup)
if "master_name" not in st.session_state:
    st.session_state.master_name = "Sunita"
if "master_msg" not in st.session_state:
    st.session_state.master_msg = "Wishing you a cinematic year ahead full of love and super-hits!"
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#1f2833"

st.title("⚡ AI Lyrical Birthday Studio & Card Engine")
st.markdown("---")

# 3. Sidebar Authorization Control Room
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
        st.sidebar.error("❌ Invalid System Credentials")

# 4. Multi-Panel Studio Workspace
tab1, tab2, tab3 = st.tabs(["⚙️ PANEL 1: Admin Configuration", "🖼️ PANEL 2: Photo Card Render Engine", "🎬 PANEL 3: 4-Photo Video & Music Mixer"])

# =====================================================================
# PANEL 1: ADMIN WORKSPACE (Edits Panel 2 and 3)
# =====================================================================
with tab1:
    st.header("⚙️ Master Administrative Console")
    if is_master_admin:
        st.write("Modify core configurations for Client view globally:")
        
        adm_name = st.text_input("Set Default/Lock Name:", st.session_state.master_name)
        adm_msg = st.text_area("Set Default/Lock Birthday Message:", st.session_state.master_msg)
        adm_col = st.color_picker("Override Default Card Canvas Color:", st.session_state.bg_color)
        
        if st.button("💾 Apply Configuration & Sync Across System"):
            st.session_state.master_name = adm_name
            st.session_state.master_msg = adm_msg
            st.session_state.bg_color = adm_col
            st.success("🎉 Global settings synchronised successfully! Check Panel 2 & 3.")
    else:
        st.warning("⚠️ Access Restricted. Unlock using the sidebar Master Panel credentials.")

# =====================================================================
# PANEL 2: PHOTO CARD RENDER ENGINE
# =====================================================================
with tab2:
    st.header("🖼️ High-Definition Image Card Maker")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🎨 Aesthetic Overlays")
        target_name = st.text_input("Enter Celebrant Name:", st.session_state.master_name, key="p2_name")
        custom_wish = st.text_area("Custom Wish Message:", st.session_state.master_msg, key="p2_wish")
        card_theme = st.color_picker("Pick Individual Backdrop Hue:", st.session_state.bg_color, key="p2_color")
        txt_hue = st.color_picker("Pick Typography Font Color:", "#66fcf1")
        card_photo = st.file_uploader("Upload Main Portrait Photo:", type=["jpg","png","jpeg"], key="p2_img")
        process_card = st.button("✨ Render Custom High-Res Card")
        
    with c2:
        st.markdown("### 🍿 Output Canvas Screen")
        if process_card:
            st.balloons()
            st.markdown(f"""
                <div style="background-color: {card_theme}; padding: 35px; border-radius: 15px; text-align: center; border: 3px solid {txt_hue};">
                    <h1 style="color: {txt_hue} !important; font-size: 38px; margin-bottom: 5px;">🎉 HAPPY BIRTHDAY 🎉</h1>
                    <h2 style="color: #ffffff !important; font-weight: bold; letter-spacing: 2px;">👑 {target_name} 👑</h2>
                    <hr style="border-color: {txt_hue};">
                    <p style="color: #e5e5e5; font-size: 18px; font-style: italic;">"{custom_wish}"</p>
                </div>
            """, unsafe_allow_html=True)
            
            if card_photo:
                st.markdown("<br>", unsafe_allow_html=True)
                st.image(card_photo, caption=f"Celebrant: {target_name}", use_container_width=True)
                
            # --- Link Generation System ---
            st.markdown("<div class='share-box'>", unsafe_allow_html=True)
            st.subheader("🔗 Shareable Card Node Generated!")
            # Browser page url fetching simulation
            mock_url = f"https://streamlit.app{target_name.replace(' ', '%20')}"
            st.code(mock_url, language="text")
            
            # Direct Action Link
            whatsapp_api = f"https://whatsapp.com{target_name}!%20👉%20{mock_url}"
            st.markdown(f'<a href="{whatsapp_api}" target="_blank"><button style="background-color:#25D366; color:white; border-radius:8px; padding:10px; width:100%; border:none; font-weight:bold; cursor:pointer;">📲 Send Card Via WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Adjust details and trigger 'Render Custom High-Res Card' to activate live engine workflow.")

# =====================================================================
# PANEL 3: 4-PHOTO VIDEO & MUSIC MIXER
# =====================================================================
with tab3:
    st.header("🎬 4-Photo Lyrical Video & Name Mixer")
    
    v1, v2 = st.columns(2)
    with v1:
        st.markdown("### 🎛️ Multi-Track Video Timeline Mixer")
        vid_name = st.text_input("Type Name to inject into Personalized Song Track:", st.session_state.master_name, key="p3_name")
        
        # Personalized Track Selection Box
        song_track = st.selectbox("🎵 Select Name-Injected Birthday Track:", [
            f"Happy Birthday to You ({vid_name} Customized Edition)", 
            f"DJ Remix Birthday Beats (Dedicated to {vid_name})", 
            f"Retro Jazz Special Classic (For {vid_name})"
        ])
        
        fx_filter = st.selectbox("🎆 Select Cinematic VFX Overlays:", ["4K Ultra-Vibrant Pop", "Cyberpunk Neon Flare", "Golden Vintage Glow"])
        
        # 4 Photos Uploader Slots
        st.markdown("#### 📸 Upload Assets (Select 2 to 4 Images)")
        uploaded_photos = st.file_uploader("Drop images here for cinematic slideshow timing:", type=["jpg","png","jpeg"], accept_multiple_files=True)
        
        process_video = st.button("🚀 Compile & Render Birthday Video")
        
    with v2:
        st.markdown("### 📺 Master Monitor Playback")
        if process_video:
            if uploaded_photos and len(uploaded_photos) >= 2:
                if len(uploaded_photos) > 4:
                    st.warning("⚠️ Maximum 4 pictures supported. Processing first 4 images.")
                    uploaded_photos = uploaded_photos[:4]
                
                st.snow()
                st.success(f"🎵 Audio Synthesizer Node matched successfully! Playing: '{song_track}'")
                
                # Mock AI Lyrical Audio player depending on chosen name
                st.audio("https://soundhelix.com", format="audio/mp3")
                
                # Loop through images to simulate Video Canvas Render
                st.markdown(f"<div class='card-output'><h4>🎞️ Live Frame Render Feed [{fx_filter} mode]</h4><br>", unsafe_allow_html=True)
                
                # Dynamic Multi-grid image slider structure
                img_cols = st.columns(len(uploaded_photos))
                for idx, img_file in enumerate(uploaded_photos):
                    with img_cols[idx]:
                        st.image(img_file, caption=f"Scene Frame {idx+1}", use_container_width=True)
                        
                st.markdown(f"<h2 style='color:#45f3ff !important;'>🎉 Happy Birthday to {vid_name}! 🎉</h2></div>", unsafe_allow_html=True)
                
                # --- Link Generation System ---
                st.markdown("<div class='share-box'>", unsafe_allow_html=True)
                st.subheader("🔗 Shareable Lyrical Video Link Generated!")
                video_mock_url = f"https://streamlit.app{vid_name.replace(' ', '%20')}"
                st.code(video_mock_url, language="text")
                
                vid_whatsapp = f"https://whatsapp.com{vid_name}!%20🍿👉%20{video_mock_url}"
            st.markdown(f'📲 Send Video Song Via 
            WhatsApp', unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            else:
            st.error("❌ Video compiled failed! Please 
            upload at least 2 to 4 photos to generate 
            timelines.")
            else:
            st.info("Upload your pictures, type the name for 
            the lyrical track song alignment, and click 
            'Compile & Render'.")
