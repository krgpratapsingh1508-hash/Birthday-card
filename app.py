import streamlit as st

# 1. Page Config and Setup
st.set_page_config(page_title="Birthday Studio", page_icon="🎂", layout="wide")

# Theme Styling (Clean Dark UI)
st.markdown("""
    <style>
    .main { background-color: #121212; color: #ffffff; }
    h1, h2, h3 { color: #FF4B4B !important; font-family: 'Arial', sans-serif; }
    .card-frame {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0px 10px 25px rgba(255, 75, 75, 0.3);
        margin-top: 15px;
    }
    .video-info-box {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Application Data Initialize (Session State)
if "name" not in st.session_state:
    st.session_state.name = "Best Friend"
if "msg" not in st.session_state:
    st.session_state.msg = "Wishing you a fantastic year ahead full of success and joy!"
if "url" not in st.session_state:
    st.session_state.url = "https://youtube.com"

st.title("🎬 3-Panel Birthday Creator App")
st.markdown("---")

# 2. Sidebar Login Panel
st.sidebar.title("🔐 Authorization")
role = st.sidebar.selectbox("Chunein kaunsa panel dekhna hai:", ["👤 Guest / User View", "🛠️ Admin Control Panel"])

is_admin = False
if role == "🛠️ Admin Control Panel":
    st.sidebar.subheader("Admin Login Details")
    admin_id = st.sidebar.text_input("Admin ID", value="", placeholder="e.g. admin")
    admin_pw = st.sidebar.text_input("Password", type="password", placeholder="e.g. birthday123")
    
    if admin_id == "admin" and admin_pw == "birthday123":
        st.sidebar.success("✅ Admin Access Approved!")
        is_admin = True
    elif admin_id != "" or admin_pw != "":
        st.sidebar.error("❌ Galat ID ya Password!")

st.sidebar.markdown("---")
st.sidebar.info("💡 Default Login:\nID: admin\nPassword: birthday123")

# 3. Core Panels (3 Tabs System)
p1, p2, p3 = st.tabs(["⚙️ PANEL 1: Admin Configuration", "🖼️ PANEL 2: Image Card Maker", "📺 PANEL 3: Video Card Player"])

# =====================================================================
# PANEL 1: ADMIN CONFIGURATION
# =====================================================================
with p1:
    st.subheader("⚙️ System Control Dashboard")
    if is_admin:
        st.write("Yahan se aap Panel 2 aur Panel 3 ka data live change kar sakte hain:")
        
        # Admin Forms for Updates
        adm_name = st.text_input("Birthday Name Badlein:", st.session_state.name)
        adm_msg = st.text_area("Birthday Message Badlein:", st.session_state.msg)
        adm_url = st.text_input("Video URL (YouTube Link) Badlein:", st.session_state.url)
        
        if st.button("💾 Save Settings & Deploy Changes"):
            st.session_state.name = adm_name
            st.session_state.msg = adm_msg
            st.session_state.url = adm_url
            st.success("🎉 Data successfully update ho gaya! Ab Panel 2 ya Panel 3 check karein.")
    else:
        st.warning("⚠️ Yeh panel locked hai. Pehle sidebar me sahi Admin ID aur Password dalein.")

# =====================================================================
# PANEL 2: IMAGE CARD MAKER
# =====================================================================
with p2:
    st.subheader("🖼️ Interactive Birthday Image Card")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎨 Design Setup")
        bg_col = st.color_picker("Card Background Color Chunein:", "#FFF0F5")
        txt_col = st.color_picker("Text Color Chunein:", "#C71585")
        user_photo = st.file_uploader("Birthday Person ki Photo Upload karein:", type=["png", "jpg", "jpeg"])
        render_image_card = st.button("✨ Render Custom Card")
        
    with col2:
        st.markdown("### 👀 Output Card Preview")
        if render_image_card:
            st.balloons()
            
            # HTML Layout block for the card
            st.markdown(f"""
                <div style="background-color: {bg_col}; padding: 25px; border-radius: 15px; text-align: center; border: 2px dashed {txt_col};">
                    <h1 style="color: {txt_col} !important; font-size: 32px; margin-bottom: 5px;">🎉 Happy Birthday! 🎉</h1>
                    <h2 style="color: #333333 !important; font-weight: bold;">✨ {st.session_state.name} ✨</h2>
                    <p style="color: #555555; font-size: 16px; font-style: italic;">"{st.session_state.msg}"</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Display uploaded photo inside the preview area smoothly
            if user_photo is not None:
                st.markdown("<br>", unsafe_allow_html=True)
                st.image(user_photo, caption=f"Celebrant: {st.session_state.name}", use_container_width=True)
        else:
            st.info("Balloons animation aur design dekhne ke liye '✨ Render Custom Card' button par click karein.")

# =====================================================================
# PANEL 3: VIDEO CARD PLAYER
# =====================================================================
with p3:
    st.subheader("📺 Video Player Control Room")
    
    v_col1, v_col2 = st.columns([1, 1])
    
    with v_col1:
        st.markdown("### 🎬 Media Options")
        fx_effect = st.selectbox("Video FX Filter Applied:", ["Cinematic Master", "Vintage 90s Tone", "Vibrant Digital Pop"])
        render_video_card = st.button("🚀 Render & Play Media")
        
    with v_col2:
        st.markdown("### 🍿 Monitor Display")
        # Displaying the synchronized video
        st.video(st.session_state.url)
        
        if render_video_card:
            st.snow()
            st.markdown(f"""
                <div class="video-info-box">
                    <h3 style="margin:0;">🎬 Video Playing for: {st.session_state.name}</h3>
                    <p style="color: #888; font-size: 14px; margin: 5px 0;">Filter Mode: <b>{fx_effect}</b></p>
                    <p style="font-size: 16px; color: #FF4B4B; font-style: italic; margin-top: 10px;">"{st.session_state.msg}"</p>
                </div>
            """, unsafe_allow_html=True)
            
