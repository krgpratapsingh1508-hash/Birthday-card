import streamlit as st
import time
from PIL import Image

# =====================================================================
# 1. PAGE SETUP & PREMIUM CSS THEME
# =====================================================================
st.set_page_config(page_title="AI Dynamic Birthday Studio", page_icon="🎂", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0c10; color: #c5c6c7; }
    h1, h2, h3, h4 { color: #66fcf1 !important; font-family: 'Poppins', sans-serif; font-weight: bold; text-align: center; }
    
    /* Premium Templates Styling */
    .template-gold { background: linear-gradient(135px, #1e1b4b 0%, #311042 100%); border: 3px solid #fbbf24; padding: 40px; border-radius: 20px; text-align: center; color: white; max-width: 600px; margin: 0 auto;}
    .template-neon { background: linear-gradient(135px, #0f172a 0%, #1e1b4b 100%); border: 3px solid #ec4899; padding: 40px; border-radius: 20px; text-align: center; color: white; max-width: 600px; margin: 0 auto;}
    .template-vintage { background: linear-gradient(135px, #451a03 0%, #78350f 100%); border: 3px solid #f59e0b; padding: 40px; border-radius: 20px; text-align: center; color: white; max-width: 600px; margin: 0 auto;}
    
    /* Video Studio Monitor Simulation */
    .video-monitor {
        background-color: #020617;
        border: 4px solid #45f3ff;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0px 15px 35px rgba(69, 243, 255, 0.25);
        text-align: center;
        margin-top: 15px;
        max-width: 800px;
        margin: 20px auto;
    }
    
    .share-box { background-color: #000000; padding: 15px; border-radius: 12px; border: 1px dashed #45f3ff; margin-top: 15px; text-align: center;}
    .stButton>button { background-color: #45f3ff; color: black; font-weight: bold; border-radius: 8px; width: 100%;}
    .lock-style { background-color: #1a1a24; padding: 20px; border-radius: 10px; border: 1px solid #ff4b4b; text-align: center; margin-bottom: 20px;}
    .forgot-box { background-color: #111115; padding: 10px; border-radius: 8px; border: 1px dashed #66fcf1; margin-top: 10px; text-align: center; color: #a7f3d0;}
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. MASTER MEMORY SYNC ENGINE (SESSION STATE)
# =====================================================================
if "bday_name" not in st.session_state:
    st.session_state.bday_name = "Sunita"
if "bday_gender" not in st.session_state:
    st.session_state.bday_gender = "Girl"
if "bday_age" not in st.session_state:
    st.session_state.bday_age = 22
if "bday_relation" not in st.session_state:
    st.session_state.bday_relation = "Best Friend"

# =====================================================================
# 3. URL GENERATED LINK DETECTOR (DYNAMIC ROUTING)
# =====================================================================
query_params = st.query_params

if "view" in query_params:
    view_type = query_params["view"]
    name_param = query_params.get("name", "Best Friend")
    age_param = query_params.get("age", "22")
    relation_param = query_params.get("relation", "Friend")
    
    st.balloons()
    
    if view_type == "card":
        template_param = query_params.get("template", "gold")
        wish_index = int(query_params.get("wish", "0"))
        
        wishes_bank = [
            f"Happy Birthday to my wonderful {relation_param}! May your {age_param}th year bring endless laughter!",
            f"Cheers to another gorgeous year! Happy Birthday {name_param}, the best {relation_param} ever.",
            f"Wishing a magnificent {age_param}rd birthday to the most awesome person in the world!"
        ]
        
        template_css = "template-gold"
        title_color = "#fbbf24"
        if template_param == "neon":
            template_css = "template-neon"
            title_color = "#ec4899"
        elif template_param == "vintage":
            template_css = "template-vintage"
            title_color = "#f59e0b"
            
        st.markdown(f"""
            <div class="{template_css}">
                <h1 style="color: {title_color} !important; font-size:42px; margin:0;">🎉 HAPPY BIRTHDAY 🎉</h1>
                <h2 style="color:#ffffff !important; letter-spacing:2px; margin:15px 0;">👑 {name_param.upper()} 👑</h2>
                <p style="font-size:16px; color:#94a3b8; margin:0;">Turning {age_param} | Special {relation_param} Edition</p>
                <hr style="border-color:{title_color};">
                <p style="font-size: 20px; font-style: italic;">"{wishes_bank[wish_index]}"</p>
            </div>
        """, unsafe_allow_html=True)
        
    elif view_type == "video":
        singer_param = query_params.get("singer", "Arijit")
        
        if singer_param == "Arijit":
            audio_url = "https://soundhelix.com"
            voice_tag = "Arijit Singh AI"
        elif singer_param == "Neha":
            audio_url = "https://soundhelix.com"
            voice_tag = "Neha Kakkar AI"
        else:
            audio_url = "https://soundhelix.com"
            voice_tag = "Sonu Nigam AI"
            
        st.markdown("<div class='video-monitor'>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='color:#38bdf8 !important; margin:0;'>🎬 SPECIAL VIDEO FOR {name_param.upper()}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#a7f3d0; font-size:16px; margin: 10px 0;'>🎤 AI Vocal Dedicated By: <b>{voice_tag}</b></p>", unsafe_allow_html=True)
        
        st.audio(audio_url, format="audio/mp3", autoplay=True)
        
        st.markdown(f"<h2 style='color:#fbbf24 !important; font-weight:bold; margin-top:30px;'>🎉 Happy Birthday to you, {name_param}! 🎉</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#ffffff; font-size:18px;'>Special {relation_param} edition song successfully synced for this sweet {age_param} years milestone!</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.info("🕒 Yeh content temporary server cloud dwara 24 ghante ke liye live kiya gaya hai.")
    st.stop()

# =====================================================================
# 4. NORMAL STUDIO INTERFACE
# =====================================================================
st.title("⚡ AI Lyrical Birthday Studio Engine Pro")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["⚙️ PANEL 1: Admin Form (Locked)", "🖼️ PANEL 2: Design Card Maker (Locked)", "🎬 PANEL 3: Cinematic Video Studio (Locked)"])

# =====================================================================
# PANEL 1: ADMIN CONTROL METADATA FORM (With Hidden Forgot Password Option)
# =====================================================================
with tab1:
    st.header("⚙️ PANEL 1: Master Registration Dashboard")
    p1_col1, p1_col2 = st.columns()
    with p1_col1:
        st.markdown("<div class='lock-style'><h4>🔒 Panel 1 Login</h4></div>", unsafe_allow_html=True)
        p1_user = st.text_input("Admin ID", placeholder="e.g. admin", key="p1_uid")
        p1_pass = st.text_input("Admin Password", type="password", placeholder="e.g. admin123", key="p1_pwd")
        
        # --- FORGOT PASSWORD HIDDEN SYSTEM ---
        st.markdown("---")
        show_forgot = st.checkbox("🔍 Need Help / Forgot Password?", value=False)
        
        if show_forgot:
            # Yeh content tabhi unhide hoga jab user box ko check (click) karega
            st.markdown("""
                <div class='forgot-box'>
                    💡 <b>Master Recovery Hint:</b><br>
                    ID: <code>admin</code><br>
                    Password: <code>admin123</code>
                </div>
            """, unsafe_allow_html=True)
    
    with p1_col2:
        if p1_user == "admin" and p1_pass == "admin123":
            st.success("🔓 Panel 1 Access Granted!")
            form_name = st.text_input("Celebrant Name (Naam Kya Hai?):", st.session_state.bday_name)
            form_gender = st.radio("Gender Chunein (Boy/Girl?):", ["Boy", "Girl"], index=0 if st.session_state.bday_gender == "Boy" else 1)
            form_age = st.number_input("Age Type (Kitne Saal Ka Hai?):", min_value=1, max_value=120, value=int(st.session_state.bday_age))
            form_relation = st.selectbox("Relationship (Aapka Kon Hai?):", ["Best Friend", "Brother", "Sister", "Love/Partner", "Family Member"], index=0)
            
            if st.button("💾 Deploy Data & Sync System Globally"):
                st.session_state.bday_name = form_name
                st.session_state.bday_gender = form_gender
                st.session_state.bday_age = form_age
                st.session_state.bday_relation = form_relation
                st.success("🎉 Metadata processing complete! Panel 2 and 3 updated.")
        else:
            if p1_user != "" or p1_pass != "": st.error("❌ Galat Admin ID ya Password!")
            st.warning("⚠️ Password daal kar form unlock kijiye.")

# =====================================================================
# PANEL 2: DESIGN CARD MAKER (ONLY PANEL 2 CONTROL NODE)
# =====================================================================
with tab2:
    st.header("🖼️ PANEL 2: High-Res Designer Card Frame Generator")
    p2_col1, p2_col2 = st.columns()
    
    with p2_col1:
        st.markdown("<div class='lock-style'><h4>🔒 Panel 2 Login</h4></div>", unsafe_allow_html=True)
        # Dedicated credentials fields for panel 2
        p2_user = st.text_input("Card User ID", placeholder="e.g. carduser", key="p2_uid")
        p2_pass = st.text_input("Card Password", type="password", placeholder="e.g. card123", key="p2_pwd")
        
    with p2_col2:
        # Strict logic execution block for authorization gating
        if p2_user == "carduser" and p2_pass == "card123":
            st.success("🔓 Panel 2 Access Granted!")
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown("### 🎨 Template & Wish Options")
                selected_design = st.selectbox("Choose Layout Template:", ["🏆 Royal Midnight Gold", "💖 Cyber Neon Glow", "🍂 Classic Golden Vintage"])
                template_slug = "gold" if "Royal" in selected_design else "neon" if "Cyber" in selected_design else "vintage"
                
                # Fetching real-time global state strings synchronised by Panel 1 form values
                wishes_bank = [
                    f"Happy Birthday to my wonderful {st.session_state.bday_relation}! May your {st.session_state.bday_age}th year bring endless laughter!",
                    f"Cheers to another gorgeous year! Happy Birthday {st.session_state.bday_name}, the best {st.session_state.bday_relation} ever.",
                    f"Wishing a magnificent {st.session_state.bday_age}rd birthday to the most awesome {st.session_state.bday_gender} in the world!"
                ]
                chosen_wish = st.selectbox("Select Best Wish Quotes:", wishes_bank)
                wish_idx = wishes_bank.index(chosen_wish)
                
                uploaded_img = st.file_uploader("Upload Portrait Photo (Auto-Crop Active):", type=["png", "jpg", "jpeg"], key="p2_upload")
                render_card = st.button("✨ Compile Layout & Render Card")
                
            with c2:
                if render_card:
                    # Rendering custom typography template skins natively via CSS templates inline injects
                    template_css = "template-gold"
                    title_color = "#fbbf24"
                    if template_slug == "neon":
                        template_css = "template-neon"
                        title_color = "#ec4899"
                    elif template_slug == "vintage":
                        template_css = "template-vintage"
                        title_color = "#f59e0b"
                        
                    st.markdown(f"""
                        <div class="{template_css}">
                            <h1 style="color: {title_color} !important; font-size:36px; margin:0;">🎉 HAPPY BIRTHDAY 🎉</h1>
                            <h2 style="color:#ffffff !important; letter-spacing:2px; margin:10px 0;">👑 {st.session_state.bday_name.upper()} 👑</h2>
                            <p style="font-size:14px; color:#94a3b8; margin:0;">Turning {st.session_state.bday_age} | Special {st.session_state.bday_relation} Edition</p>
                            <hr style="border-color:{title_color};">
                            <p class="card-text">"{chosen_wish}"</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Smart pixel cropping calculations logic block execution matrices
                    if uploaded_img:
                        raw_image = Image.open(uploaded_img)
                        width, height = raw_image.size
                        min_dim = min(width, height)
                        cropped_img = raw_image.crop(((width-min_dim)/2, (height-min_dim)/2, (width+min_dim)/2, (height+min_dim)/2))
                        st.image(cropped_img, caption="AI Auto-Fit Portrait Mode Active", use_container_width=True)
                        
                    st.markdown("<div class='share-box'>", unsafe_allow_html=True)
                    st.subheader("📥 Export & Distribution Nodes")
                    col_b1, col_b2 = st.columns(2)
                    
                    with col_b1:
                        # Twin Export Target 01: Standard local asset rendering box
                        st.download_button(label="💾 Download HD PNG Card", data=b"MockImageData", file_name=f"{st.session_state.bday_name}_card.png", mime="image/png")
                    with col_b2:
                        # Twin Export Target 02: Auto-Routing dynamic URL Parameter injection strings mapping rules
                        real_card_link = f"https://streamlit.app{st.session_state.bday_name.replace(' ', '%20')}&age={st.session_state.bday_age}&relation={st.session_state.bday_relation.replace(' ', '%20')}&template={template_slug}&wish={wish_idx}"
                        st.info("🕒 Generated 24Hrs Active Cloud Link:")
                        st.code(real_card_link, language="text")
                        
                    # Integrated instant WhatsApp external target messaging route handler
                    wa_api_url = f"https://whatsapp.com{st.session_state.bday_name}!%20👉%20{real_card_link}"
                    st.markdown(f'<a href="{wa_api_url}" target="_blank"><button style="background-color:#25D366; color:white; border-radius:8px; padding:10px; width:100%; border:none; font-weight:bold; cursor:pointer;">📲 Direct Share To WhatsApp</button></a>', unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            if p2_user != "" or p2_pass != "": 
                st.error("❌ Galat User ID ya Password!")
            st.warning("⚠️ Card Maker Panel locked hai. Sahi parameters dalkar override kijiye.")

# =====================================================================
# PANEL 3: CINEMATIC VIDEO STUDIO (ONLY PANEL 3 CONTROL NODE)
# =====================================================================
with tab3:
    st.header("🎬 PANEL 3: Premium AI Lyrical Video & Voice Studio")
    p3_col1, p3_col2 = st.columns()
    
    with p3_col1:
        st.markdown("<div class='lock-style'><h4>🔒 Panel 3 Login</h4></div>", unsafe_allow_html=True)
        # Dedicated credentials fields for panel 3
        p3_user = st.text_input("Video User ID", placeholder="e.g. videouser", key="p3_uid")
        p3_pass = st.text_input("Video Password", type="password", placeholder="e.g. video123", key="p3_pwd")
        
    with p3_col2:
        # Strict logic execution block for authorization gating
        if p3_user == "videouser" and p3_pass == "video123":
            st.success("🔓 Panel 3 Access Granted!")
            v1, v2 = st.columns(2)
            
            with v1:
                st.markdown("### 🎛️ AI Voice & Music Pipeline Settings")
                # Fetching real-time parameters synchronised by Panel 1 form values
                st.write(f"👤 **Target Profile:** Name: `{st.session_state.bday_name}` | Gender: `{st.session_state.bday_gender}` | Age: `{st.session_state.bday_age}`")
                
                selected_singer = st.selectbox("🎙️ Select AI Singer Voice:", ["🎵 Arijit Singh AI Vocal Engine", "🎵 Neha Kakkar AI Vocal Engine", "🎵 Sonu Nigam AI Vocal Engine"])
                singer_slug = "Arijit" if "Arijit" in selected_singer else "Neha" if "Neha" in selected_singer else "Sonu"
                
                bulk_photos = st.file_uploader("Upload 2-4 Slideshow Assets:", type=["jpg","png","jpeg"], accept_multiple_files=True, key="p3_bulk_pics")
                compile_video = st.button("🚀 Render Custom AI Voice Video")
                
            with v2:
                if compile_video:
                    if bulk_photos and len(bulk_photos) >= 2:
                        st.markdown("<div class='video-monitor'>", unsafe_allow_html=True)
                        st.markdown(f"<h3 style='color:#38bdf8 !important; margin:0;'>🎬 SLIDESHOW INTERFACE ENABLED</h3>", unsafe_allow_html=True)
                        
                        # Custom name track music mapping rules
                        if singer_slug == "Arijit":
                            audio_url = "https://soundhelix.com"
                            voice_tag = "Arijit Singh AI"
                        elif singer_slug == "Neha":
                            audio_url = "https://soundhelix.com"
                            voice_tag = "Neha Kakkar AI"
                        else:
                            audio_url = "https://soundhelix.com"
                            voice_tag = "Sonu Nigam AI"
                        
                        # Audio Engine Activation with Autoplay
                        st.audio(audio_url, format="audio/mp3", autoplay=True)
                        
                        # Displaying first 4 images beautifully inside clean responsive columns
                        grid_cols = st.columns(min(len(bulk_photos), 4))
                        for index, photo_file in enumerate(bulk_photos[:4]):
                            with grid_cols[index]: 
                                st.image(photo_file, use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("<div class='share-box'>", unsafe_allow_html=True)
                        st.subheader("📥 Export & Share Video Option Node")
                        v_col1, v_col2 = st.columns(2)
                        
                        with v_col1:
                            # Twin Export Target 01: Standard local asset download frame
                            st.download_button(label="💾 Download Full Video (HD MP4)", data=b"MockVideoData", file_name=f"{st.session_state.bday_name}_video.mp4", mime="video/mp4")
                        with v_col2:
                            # Twin Export Target 02: Auto-Routing dynamic URL Parameter injection strings mapping rules
                            real_video_link = f"https://streamlit.app{st.session_state.bday_name.replace(' ', '%20')}&age={st.session_state.bday_age}&relation={st.session_state.bday_relation.replace(' ', '%20')}&singer={singer_slug}"
                            st.info("🕒 Generated 24Hrs Active Cloud Link:")
                            st.code(real_video_link, language="text")
                            
                        # Integrated instant WhatsApp external target messaging route handler
                        v_wa_api = f"https://whatsapp.com{st.session_state.bday_name}!%20👉%20{real_video_link}"
                        st.markdown(f'<a href="{v_wa_api}" target="_blank"><button style="background-color:#25D366; color:white; border-radius:8px; padding:10px; width:100%; border:none; font-weight:bold; cursor:pointer;">📲 Share Video on WhatsApp</button></a>', unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.error("❌ Kam se kam 2 photos upload karein!")
        else:
            if p3_user != "" or p3_pass != "": 
                st.error("❌ Galat User ID ya Password!")
            st.warning("⚠️ Video Studio Panel locked hai. Sahi parameters dalkar override kijiye.")
        
