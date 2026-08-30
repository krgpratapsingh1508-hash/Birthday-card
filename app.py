import streamlit as st
import time

# 1. Page Configuration & Ultra-Modern Cyberpunk-Gold Theme
st.set_page_config(page_title="VFX Birthday Studio Pro", page_icon="🎂", layout="wide")

# Advanced Premium UI/UX Custom Engine Styling (CSS)
st.markdown("""
    <style>
    .main { background-color: #0d0d11; color: #e2e8f0; }
    h1, h2, h3 { font-family: 'Poppins', sans-serif; font-weight: 800; text-align: center; }
    
    /* Premium Neon & Gold Card Template Design */
    .premium-card {
        background: linear-gradient(135px, #1e1b4b 0%, #311042 100%);
        padding: 40px;
        border-radius: 24px;
        text-align: center;
        border: 3px solid #fbbf24;
        box-shadow: 0px 20px 40px rgba(251, 191, 36, 0.2);
        margin: 20px auto;
        max-width: 600px;
    }
    .card-title { color: #fbbf24 !important; font-size: 42px; text-shadow: 0px 4px 10px rgba(251,191,36,0.5); font-weight: bold; margin-bottom: 10px; }
    .card-name { color: #ffffff !important; font-size: 34px; letter-spacing: 3px; margin: 15px 0; font-weight: bold; text-transform: uppercase; }
    .card-text { color: #cbd5e1; font-size: 18px; font-style: italic; line-height: 1.6; }

    /* Video Studio Monitor Simulation */
    .video-monitor {
        background-color: #020617;
        border: 4px solid #38bdf8;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0px 15px 35px rgba(56, 189, 248, 0.25);
        text-align: center;
    }
    
    /* Interactive WhatsApp Share Box */
    .share-node {
        background: #1e293b;
        padding: 20px;
        border-radius: 16px;
        border: 2px dashed #38bdf8;
        margin-top: 25px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Global Memory Initialization
if "master_name" not in st.session_state:
    st.session_state.master_name = "Sunita"
if "master_msg" not in st.session_state:
    st.session_state.master_msg = "May your special day be packed with cinematic moments, endless laughter, and boundless joy!"
if "global_audio" not in st.session_state:
    st.session_state.global_audio = "Modern Pop Birthday Remix"

# 3. Sidebar Panel Router
st.sidebar.markdown("## 👑 STUDIO CONTROL CENTER")
workspace = st.sidebar.selectbox("Switch Dashboard View", ["👤 Client Live Experience", "⚙️ Admin Control Panel"])

is_authenticated = False
if workspace == "⚙️ Admin Control Panel":
    st.sidebar.subheader("Security Override")
    user_id = st.sidebar.text_input("System ID", placeholder="admin")
    user_pw = st.sidebar.text_input("Security Key", type="password", placeholder="birthday123")
    if user_id == "admin" and user_pw == "birthday123":
        st.sidebar.success("⚡ Access Granted! Master System Mode Active.")
        is_authenticated = True
    elif user_id != "" or user_pw != "":
        st.sidebar.error("❌ Invalid Admin Credentials")

st.title("🚀 Advanced Lyrical Birthday Studio Engine")
st.markdown("<p style='text-align:center; color:#94a3b8;'>Create premium customized animated cards and slideshow video tracks instantly</p>", unsafe_allow_html=True)
st.markdown("---")

# 3 Tabs Navigation Panel Layout
tab1, tab2, tab3 = st.tabs(["⚙️ PANEL 1: Admin Configuration", "🖼️ PANEL 2: Premium Card Renderer", "🎬 PANEL 3: Cinematic Video Studio"])

# =====================================================================
# PANEL 1: ADMIN CONTROL TOOLS
# =====================================================================
with tab1:
    st.subheader("⚙️ Global Variable Control Panel")
    if is_authenticated:
        st.info("Admin changes yahan save karte hi Panel 2 aur Panel 3 me real-time update ho jayenge.")
        adm_name = st.text_input("Override Default Celebrant Name:", st.session_state.master_name)
        adm_msg = st.text_area("Override Default Greeting Text:", st.session_state.master_msg)
        
        if st.button("💾 Push Settings Live & Update Core"):
            st.session_state.master_name = adm_name
            st.session_state.master_msg = adm_msg
            st.success("⚡ Global synchronization successfully deployed!")
    else:
        st.warning("⚠️ Access Denied. Dashboard restricted. Sidebar se Admin ID ('admin') aur Password ('birthday123') enter karein.")

# =====================================================================
# PANEL 2: PREMIUM CARD RENDERER
# =====================================================================
with tab2:
    st.subheader("🖼️ High-Fidelity Custom Invitation & Greeting Card Maker")
    c1, c2 = st.columns([1, 1.2])
    
    with c1:
        st.markdown("### 🎨 Content Editor Controls")
        card_name = st.text_input("Celebrant Name (Text Overlay):", st.session_state.master_name, key="p2_name_input")
        card_wish = st.text_area("Custom Wish Message Body:", st.session_state.master_msg, key="p2_wish_input")
        uploaded_portrait = st.file_uploader("Upload Portrait Picture (Centered Fit):", type=["jpg","png","jpeg"], key="p2_img_upload")
        render_trigger = st.button("✨ Compile & Generate Premium Card")
        
    with c2:
        st.markdown("### 🍿 Real-Time Master Canvas Preview")
        if render_trigger:
            st.balloons()
            
            # Premium Visual Card Box Template Layout
            st.markdown(f"""
                <div class="premium-card">
                    <div class="card-title">🎉 HAPPY BIRTHDAY 🎉</div>
                    <div class="card-name">👑 {card_name} 👑</div>
                    <div class="card-text">"{card_wish}"</div>
                </div>
            """, unsafe_allow_html=True)
            
            if uploaded_portrait:
                st.image(uploaded_portrait, caption=f"Celebrant Mirror Frame: {card_name}", use_container_width=True)
                
            # Instant Export & Share Node Setup
            st.markdown("<div class='share-node'>", unsafe_allow_html=True)
            st.markdown("### 🔗 Shareable Link Generated Successfully!")
            web_node_url = f"https://streamlit.app{card_name.replace(' ', '%20')}"
            st.code(web_node_url, language="text")
            
            wa_share_api = f"https://whatsapp.com{card_name}!%20Check%20it%20out%20here%20👉%20{web_node_url}"
            st.markdown(f'<a href="{wa_share_api}" target="_blank"><button style="background-color:#25D366; color:white; border-radius:12px; padding:12px; width:100%; border:none; font-weight:bold; font-size:16px; cursor:pointer;">📲 Share Card on WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Design adjust karein aur high-definition mockup preview dekhne ke liye 'Compile & Generate Premium Card' par click karein.")

# =====================================================================
# PANEL 3: CINEMATIC VIDEO STUDIO & REAL AUDIO TRACKS (ONLY PANEL 3)
# =====================================================================
with tab3:
    st.subheader("🎬 Premium Multitrack Photo Slideshow Video Editor")
    v1, v2 = st.columns([1, 1.2])
    
    with v1:
        st.markdown("### 🎛️ Timeline Mixer Elements")
        # User dropdown se ya text input se naam customize kar sakta hai
        video_target_name = st.text_input("Name For Customized Song Alignment:", st.session_state.master_name, key="p3_name_input")
        
        # Real Premium Streaming Audio Tracks Selection
        selected_track = st.selectbox("🎵 Track Studio Audio Remixer:", [
            "🔊 Upbeat Electro Pop Birthday Beats (High Energy)",
            "🔊 Acoustic Cinematic Birthday Guitar Tone (Soft/Deep)",
            "🔊 Modern Dance Party Club Remix (Dance Base)"
        ])
        
        # Audio tracks URLs selection logic
        if "Electro Pop" in selected_track:
            audio_stream_url = "https://soundhelix.com"
        elif "Acoustic Cinematic" in selected_track:
            audio_stream_url = "https://soundhelix.com"
        else:
            audio_stream_url = "https://soundhelix.com"
            
        st.markdown("#### 📸 Photo Timeline Assets (Upload 2 to 4 Images)")
        bulk_photos = st.file_uploader("Drop images to create automatic fading slides:", type=["jpg","png","jpeg"], accept_multiple_files=True, key="p3_bulk_upload")
        compile_video_trigger = st.button("🚀 Process Timeline & Render Video")
        
    with v2:
        st.markdown("### 📺 Main Program Monitor Display")
        if compile_video_trigger:
            if bulk_photos and len(bulk_photos) >= 2:
                # Sirf 4 photos optimize karne ke liye restriction box
                if len(bulk_photos) > 4:
                    st.warning("⚠️ Maximum 4 photos optimized. Rendering first 4 images.")
                    bulk_photos = bulk_photos[:4]
                
                # Mock Processing buffer time
                with st.spinner("Compiling audio waveform track..."):
                    time.sleep(1.5)
                st.snow()
                
                # Main Video Monitor Frame
                st.markdown("<div class='video-monitor'>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='color:#38bdf8 !important; margin-bottom:20px;'>🎬 NOW PLAYING: {video_target_name.upper()}_BBDAY_VFX.mp4</h3>", unsafe_allow_html=True)
                
                # Audio Engine Activation (Autoplay feature enables instant music play)
                st.write("🎵 **Audio Stream Track Status: ONLINE & SYNCED**")
                st.audio(audio_stream_url, format="audio/mp3", autoplay=True)
                
                # Image Canvas Grid Render
                grid_cols = st.columns(len(bulk_photos))
                for index, element_photo in enumerate(bulk_photos):
                    with grid_cols[index]:
                        st.image(element_photo, caption=f"Scene Frame 0{index+1}", use_container_width=True)
                        
                st.markdown(f"<h2 style='color:#fbbf24 !important; font-weight:bold; margin-top:20px;'>🎉 Happy Birthday to You, {video_target_name}! 🎉</h2>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:#94a3b8; font-style:italic;'>\"{st.session_state.master_msg}\"</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Shareable Node Link Generation 
                st.markdown("<div class='share-node'>", unsafe_allow_html=True)
                st.markdown("### 🔗 Shareable HD Video Link Active!")
                v_node_url = f"https://streamlit.app{video_target_name.replace(' ', '%20')}"
                st.code(v_node_url, language="text")
                
                v_wa_api = f"https://whatsapp.com{video_target_name}!%20👉%20{v_node_url}"
                st.markdown(f'<a href="{v_wa_api}" target="_blank"><button style="background-color:#25D366; color:white; border-radius:12px; padding:12px; width:100%; border:none; font-weight:bold; font-size:16px;">📲 Share Video on WhatsApp</button></a>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("❌ Kam se kam 2 se 4 photos upload karein!")
        else:
            st.info("Photos upload karein aur 'Process Timeline & Render Video' par click karein.")
