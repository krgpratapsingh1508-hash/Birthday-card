import streamlit as st

# 1. Page Configuration & Setup
st.set_page_config(page_title="Ultimate Birthday Hub", page_icon="🎬", layout="wide")

# Persistent State Setup (Admin Editing Ke Liye)
if "bday_name" not in st.session_state:
    st.session_state.bday_name = "Best Friend"
if "custom_msg" not in st.session_state:
    st.session_state.custom_msg = "May your year be full of happiness and zero buffering!"
if "video_url" not in st.session_state:
    st.session_state.video_url = "https://youtube.com"

# Dark Mode Cinema Styling (CSS)
st.markdown("""
    <style>
    body { background-color: #121212; color: #ffffff; }
    .stApp { background-color: #121212; }
    h1 { color: #FF4B4B; font-family: 'Helvetica', sans-serif; font-weight: bold; }
    .card-box { background-color: #1E1E1E; padding: 25px; border-radius: 15px; border: 2px solid #FF4B4B; text-align: center; box-shadow: 0 4px 15px rgba(255, 75, 75, 0.2); }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN SYSTEM (Sidebar)
st.sidebar.title("🔐 Access Control")
user_role = st.sidebar.selectbox("Select Panel / Role", ["👤 Guest / User View", "🛠️ Admin Panel"])

# Password Check for Admin
is_admin = False
if user_role == "🛠️ Admin Panel":
    admin_user = st.sidebar.text_input("Username", value="", placeholder="Enter Admin ID")
    admin_pass = st.sidebar.text_input("Password", type="password", placeholder="Enter Password")
    
    # ID & Password Settings
    if admin_user == "admin" and admin_pass == "birthday123":
        st.sidebar.success("✅ Admin Access Granted!")
        is_admin = True
    elif admin_user != "" or admin_pass != "":
        st.sidebar.error("❌ Wrong ID or Password!")

st.sidebar.markdown("---")

# 3. PANELS NAVIGATION (Sirf tabhi jab Admin logged in ho ya Guest view ho)
st.title("🎬 Multi-Panel Birthday Creator Engine")

# Tabs for 3 Panels
tab1, tab2, tab3 = st.tabs(["⚙️ PANEL 1: Admin Control", "🖼️ PANEL 2: Image Card Maker", "📺 PANEL 3: Video Editor Card"])

# =====================================================================
# PANEL 1: ADMIN CONTROL
# =====================================================================
with tab1:
    st.header("⚙️ Admin Dashboard")
    if is_admin:
        st.subheader("Edit Content for Panel 2 & Panel 3")
        
        # Admin inputs to modify state
        new_name = st.text_input("Change Birthday Person Name", st.session_state.bday_name)
        new_msg = st.text_area("Change Birthday Message / Wish", st.session_state.custom_msg)
        new_video = st.text_input("Change Video URL (YouTube)", st.session_state.video_url)
        
        if st.button("💾 Save & Update Changes Across App"):
            st.session_state.bday_name = new_name
            st.session_state.custom_msg = new_msg
            st.session_state.video_url = new_video
            st.success("🎉 Changes applied successfully! Go check Panel 2 and Panel 3.")
    else:
        st.warning("⚠️ Access Denied! Please enter correct Admin ID & Password in the sidebar to unlock editing.")

# =====================================================================
# PANEL 2: IMAGE CARD MAKER
# =====================================================================
with tab2:
    st.header("🖼️ Birthday Image Card Generator")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🛠️ Card Customizer")
        card_bg = st.color_picker("Choose Card Background Color", "#FFD1DC")
        text_color = st.color_picker("Choose Text Color", "#D2143A")
        uploaded_img = st.file_uploader("Upload Birthday Person's Photo", type=["jpg", "png", "jpeg"])
        generate_card = st.button("🎨 Render Photo Card")

    with col2:
        st.markdown("### 🖼️ Live Card Preview")
        if generate_card:
            st.balloons()
            # Custom styled HTML Card
            st.markdown(f"""
                <div style="background-color: {card_bg}; padding: 30px; border-radius: 20px; text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.15);">
                    <h1 style="color: {text_color}; font-size: 40px; margin-bottom: 5px;">🎉 Happy Birthday! 🎉</h1>
                    <h2 style="color: #333333;">✨ {st.session_state.bday_name} ✨</h2>
                    <p style="color: #555555; font-size: 18px; font-style: italic; padding: 10px;">"{st.session_state.custom_msg}"</p>
                </div>
            """, unsafe_allow_html=True)
            
            if uploaded_img:
                st.image(uploaded_img, caption=f"Birthday Star: {st.session_state.bday_name}", use_container_width=True)
        else:
            st.info("Click 'Render Photo Card' to view the generated image card.")

# =====================================================================
# PANEL 3: VIDEO CARD EDITOR
# =====================================================================
with tab3:
    st.header("📺 Professional Video Card Panel")
    
    col_v1, col_v2 = st.columns([1, 2])
    
    with col_v1:
        st.markdown("### 🎬 Video FX controls")
        video_speed = st.slider("Playback Speed Preview", 0.5, 2.0, 1.0, 0.1)
        video_theme = st.selectbox("Video Filter Effect", ["Original Cinema", "Vibrant Pop", "Vintage Retro"])
        render_vid = st.button("🚀 Render & Play Video")
        
    with col_v2:
        st.markdown("### 📺 Player Viewport")
        # Video link updated by Admin
        st.video(st.session_state.video_url)
        
        if render_vid:
            st.snow()
            st.markdown(f"""
                <div class="card-box">
                    <h2 style="color: #FF4B4B; margin: 0;">🎬 Now Playing: For {st.session_state.bday_name}</h2>
                    <p style="margin: 5px 0 0 0; color: #bbb;">Filter: {video_theme} | Speed: {video_speed}x</p>
                    <p style="font-size: 18px; color: #fff; margin-top: 15px;">🌟 "{st.session_state.custom_msg}" 🌟</p>
                </div>
            """, unsafe_allow_html=True)
            
