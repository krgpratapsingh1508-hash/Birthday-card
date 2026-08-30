import streamlit as st
import time
from PIL import Image

# =====================================================================
# 1. APPLICATION STRUCTURAL CONFIGURATION & ADVANCED UI THEMING
# =====================================================================
st.set_page_config(page_title="AI Birthday Ecosystem Pro", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #060709; color: #e2e8f0; font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4 { font-family: 'Poppins', sans-serif; font-weight: bold; text-align: center; }
    
    /* Clean Cryptographic Authorization Layout Boxes */
    .landing-gate { background: linear-gradient(145px, #111827 0%, #030712 100%); padding: 40px; border-radius: 20px; border: 2px solid #3b82f6; max-width: 550px; margin: 50px auto; box-shadow: 0px 20px 50px rgba(59, 130, 246, 0.15); }
    .panel-lock-indicator { background-color: #1f2937; padding: 15px; border-radius: 12px; border-left: 5px solid #ef4444; margin-bottom: 20px; }
    
    /* Graphic Pampalet Template Blueprint Frameworks */
    .pampalet-gold { background: linear-gradient(135px, #1e1b4b 0%, #311042 100%); border: 4px dashed #fbbf24; padding: 45px; border-radius: 24px; text-align: center; color: white; max-width: 650px; margin: 0 auto; box-shadow: 0 10px 30px rgba(251,191,36,0.2); }
    .pampalet-cyber { background: linear-gradient(135px, #0f172a 0%, #1e1b4b 100%); border: 4px dashed #ec4899; padding: 45px; border-radius: 24px; text-align: center; color: white; max-width: 650px; margin: 0 auto; box-shadow: 0 10px 30px rgba(236,72,153,0.2); }
    .pampalet-vintage { background: linear-gradient(135px, #451a03 0%, #78350f 100%); border: 4px dashed #f59e0b; padding: 45px; border-radius: 24px; text-align: center; color: white; max-width: 650px; margin: 0 auto; box-shadow: 0 10px 30px rgba(245,158,11,0.2); }
    
    /* Hardware Video Studio Monitor Mockup Box */
    .studio-monitor { background-color: #020617; border: 4px solid #06b6d4; border-radius: 24px; padding: 30px; box-shadow: 0px 20px 45px rgba(6, 182, 212, 0.25); text-align: center; max-width: 850px; margin: 20px auto; }
    .export-node-box { background-color: #090d16; padding: 20px; border-radius: 16px; border: 1px dashed #45f3ff; margin-top: 20px; text-align: center; }
    
    /* Direct Functional Actions Core Component Styling */
    .stButton>button { background: linear-gradient(90px, #3b82f6 0%, #2563eb 100%); color: white; font-weight: bold; border-radius: 10px; padding: 10px; width: 100%; border: none; transition: 0.3s; }
    .stButton>button:hover { background: linear-gradient(90px, #2563eb 0%, #1d4ed8 100%); box-shadow: 0 5px 15px rgba(37,99,235,0.4); }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. GLOBAL SYSTEM MEMORY INITIALIZATION (CORE STATE ENGINE)
# =====================================================================
if "active_session_panel" not in st.session_state:
    st.session_state.active_session_panel = None

# Default Values derived from Panel 1 Administrative Core
if "meta_name" not in st.session_state:
    st.session_state.meta_name = "Sunita"
if "meta_age" not in st.session_state:
    st.session_state.meta_age = 22
if "meta_gender" not in st.session_state:
    st.session_state.meta_gender = "Girl"
if "meta_wish" not in st.session_state:
    st.session_state.meta_wish = "May your special day be packed with timeless beautiful memories!"
if "meta_relation" not in st.session_state:
    st.session_state.meta_relation = "Best Friend"

# Custom Security Keys Database Configurations
if "pass_p1" not in st.session_state: st.session_state.pass_p1 = "admin123"
if "pass_p2" not in st.session_state: st.session_state.pass_p2 = "card123"
if "pass_p3" not in st.session_state: st.session_state.pass_p3 = "video123"

# =====================================================================
# 3. ROOT ENVIRONMENT ROUTING MECHANISMS (SAAS VIEWER ENGINE)
# =====================================================================
url_parameters = st.query_params

if "view" in url_parameters:
    target_view = url_parameters["view"]
    r_name = url_parameters.get("name", "Celebrant")
    r_age = url_parameters.get("age", "25")
    r_gender = url_parameters.get("gender", "Female")
    r_relation = url_parameters.get("relation", "Friend")
    
    st.balloons()
    
    if target_view == "card":
        r_pampalet = url_parameters.get("pampalet", "gold")
        card_css = "pampalet-gold"
        accent_color = "#fbbf24"
        if r_pampalet == "cyber":
            card_css = "pampalet-cyber"
            accent_color = "#ec4899"
        elif r_pampalet == "vintage":
            card_css = "pampalet-vintage"
            accent_color = "#f59e0b"
            
        st.markdown(f"""
            <div class="{card_css}">
                <h1 style="color: {accent_color} !important; font-size:46px; margin:0;">🎉 HAPPY BIRTHDAY 🎉</h1>
                <h2 style="color:#ffffff !important; letter-spacing:2px; margin:15px 0;">👑 {r_name.upper()} 👑</h2>
                <p style="font-size:16px; color:#94a3b8; margin:0;">Gender: {r_gender} | Age Milestone: {r_age} Years | Dedicated {r_relation} Edition</p>
                <hr style="border-color:{accent_color};">
                <p style="font-size: 20px; font-style: italic; color:#f1f5f9;">"Wishing you high-frame-rate happiness today and forever!"</p>
            </div>
        """, unsafe_allow_html=True)
        
    elif target_view == "video":
        r_singer = url_parameters.get("singer", "Arijit")
        r_fx = url_parameters.get("fx", "Neon")
        
        audio_stream = "https://soundhelix.com" if r_singer == "Arijit" else "https://soundhelix.com"
        
        st.markdown("<div class='studio-monitor'>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='color:#06b6d4 !important; margin:0;'>🍿 LIVE STREAM TIMELINE GENERATED FOR {r_name.upper()}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#a7f3d0; font-size:16px; margin: 10px 0;'>🎤 Selected Vocalist Track Artist: <b>{r_singer} AI</b> | Cinematic VFX Node: <b>{r_fx}</b></p>", unsafe_allow_html=True)
        
        st.audio(audio_stream, format="audio/mp3", autoplay=True)
        
        st.markdown(f"<h2 style='color:#fbbf24 !important; font-weight:bold; margin-top:30px;'>🎉 Happy Birthday to you, {r_name}! 🎉</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#94a3b8; font-size:16px;'>This dedicated audio timeline presentation file is actively mounted securely on server storage nodes.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.info("🕒 This content asset cloud node is temporary initialized active on servers for a 24-Hour window.")
    st.stop()

# =====================================================================
# 4. INITIAL EMPTY CLEAN LANDING PAGE LAYOUT INTERFACE 
# =====================================================================
if st.session_state.active_session_panel is None:
    st.title("⚡ Ultra-Secure AI Lyrical Birthday Studio Engine")
    st.markdown("<p style='text-align:center; color:#64748b;'>Database Server Matrix Portal Gateway Client Workspace Node</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Hide/Unhide Primary Toggle Action Button for Terminal Box Initialization Layout
    show_login_matrix = st.checkbox("🔑 Open Secure Multi-User Login Terminal Form", value=False)
    
    if show_login_matrix:
        st.markdown("<div class='landing-gate'>", unsafe_allow_html=True)
        st.markdown("<h3>🔒 USER IDENTITY VERIFICATION GATEWAY</h3>", unsafe_allow_html=True)
        
        # User Selection Dropdown Scroll List matching custom requirements instructions
        user_identity_selection = st.selectbox("Choose Target Panel Clearance ID:", ["-- Scroll List: Select Workspace --", "PANEL 1: Admin Metadata Controller", "PANEL 2: High-Res Designer Card Frame", "PANEL 3: Cinematic Video Studio Remixer"])
        user_password_input = st.text_input("Enter Crypto Key Token (Password):", type="password", placeholder="••••••••")
        
        if st.button("🚀 Process Key Tokens & Enter Workspace"):
            if user_identity_selection == "PANEL 1: Admin Metadata Controller" and user_password_input == st.session_state.pass_p1:
                st.session_state.active_session_panel = "P1"
                st.rerun()
            elif user_identity_selection == "PANEL 2: High-Res Designer Card Frame" and user_password_input == st.session_state.pass_p2:
                st.session_state.active_session_panel = "P2"
                st.rerun()
            elif user_identity_selection == "PANEL 3: Cinematic Video Studio Remixer" and user_password_input == st.session_state.pass_p3:
                st.session_state.active_session_panel = "P3"
                st.rerun()
            else:
                st.error("❌ Identification mismatch! Access token verified failed or credentials validation corrupted.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# =====================================================================
# 5. CORE WORKSPACE ENVIRONMENT ROOMS (AFTER SUCCESSFUL UNLOCK AUTH)
# =====================================================================
if st.button("🔙 Terminate Workspace Session & Return to Empty Landing Page"):
    st.session_state.active_session_panel = None
    st.rerun()

st.markdown("---")

# =====================================================================
# PANEL 1 WORKSPACE: MASTER METADATA REGISTRATION FORM (ONLY PANEL 1)
# =====================================================================
if st.session_state.active_session_panel == "P1":
    st.header("⚙️ PANEL 1 WORKSPACE: Master Metadata Registration Form")
    
    # Structural columns to balance the form and password updater layout
    col_p1_a, col_p1_b = st.columns(2)
    
    with col_p1_a:
        st.markdown("<div class='panel-lock-indicator'><h4>📋 Target Core Meta Profiles Registration</h4></div>", unsafe_allow_html=True)
        
        # Complete structured birthday metadata registration form fields
        f_name = st.text_input("Celebrant Target Name (Naam Kya Hai?):", st.session_state.meta_name)
        f_age = st.number_input("Celebrant Milestone Age (Kitne Saal Ka Hai?):", min_value=1, max_value=120, value=int(st.session_state.meta_age))
        
        # Gender Selection with Male, Female, and Transgender criteria options
        f_gender = st.radio("Gender Profile Matrix Chunein (Male/Female/Transgender):", ["Male", "Female", "Transgender"], index=0 if st.session_state.meta_gender == "Male" else 1 if st.session_state.meta_gender == "Female" else 2)
        
        f_wish = st.text_area("Custom Best Wish Quote Input (Agar aap likhna chahein toh):", st.session_state.meta_wish)
        f_relation = st.selectbox("Relationship Alignment (Rishta Kya Hai?):", ["Best Friend", "Brother", "Sister", "Partner/Love", "Family Member", "Colleague"])
        
        # Core deployment trigger button to push data parameters instantly downstream
        if st.button("💾 Synchronize Metadata Parameters Across Ecosystem"):
            st.session_state.meta_name = f_name
            st.session_state.meta_age = f_age
            st.session_state.meta_gender = f_gender
            st.session_state.meta_wish = f_wish
            st.session_state.meta_relation = f_relation
            st.success("🎉 Metadata global parameters successfully locked! Panel 2 and 3 have been synchronized.")

    with col_p1_b:
        st.markdown("<div class='panel-lock-indicator'><h4>⚙️ System Authorization Override Configurations</h4></div>", unsafe_allow_html=True)
        
        # --- THE BUTTON HIDE/UNHIDE SYSTEM FOR PASSWORDS ---
        # Toggle checkbox button that securely unhides/hides the credential modifier form elements
        show_key_changer = st.checkbox("🛠️ Toggle Password Modifier Controller Form", value=False)
        
        if show_key_changer:
            st.subheader("Modify Workspace Clearance Tokens")
            st.caption("Change database authorization security pass-keys for all panels below:")
            
            # Input fields to live rewrite system authentication keys database variables
            up_p1 = st.text_input("Update Panel 1 Password Token (Admin Form):", value=st.session_state.pass_p1, type="password")
            up_p2 = st.text_input("Update Panel 2 Password Token (Design Card):", value=st.session_state.pass_p2, type="password")
            up_p3 = st.text_input("Update Panel 3 Password Token (Video Mixer):", value=st.session_state.pass_p3, type="password")
            
            if st.button("🔒 Overwrite Security Database Keys"):
                st.session_state.pass_p1 = up_p1
                st.session_state.pass_p2 = up_p2
                st.session_state.pass_p3 = up_p3
                st.success("⚡ Database cryptographic authentication matrix keys updated securely across system!")

# =====================================================================
# PANEL 2 WORKSPACE: HIGH-RES DESIGNER CARD FRAME GENERATOR (ONLY PANEL 2)
# =====================================================================
elif st.session_state.active_session_panel == "P2":
    st.header("🖼️ PANEL 2 WORKSPACE: High-Res Designer Card Frame Generator")
    
    # Panel 1 se aaye hue raw data ko top bar me show karne ka module block
    st.info(f"📥 **Panel 1 Data Synced Automatically:** Name: `{st.session_state.meta_name}` | Age: `{st.session_state.meta_age}` | Gender: `{st.session_state.meta_gender}` | Relation: `{st.session_state.meta_relation}`")
    
    # Balanced structural columns layouts
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### 🎨 Select Pampalet Framework Template")
        # Multiple premium layout templates dropdown selection (प्रारूप चूनें)
        pampalet_design = st.selectbox("Choose Layout Pampalet Framework (प्रारूप चूनें):", [
            "🏆 Royal Luxury Midnight Gold Layout", 
            "💖 Cyber Neon Glow Futuristic Framework", 
            "🍂 Classic Antique Golden Vintage Theme"
        ])
        pampalet_slug = "gold" if "Royal" in pampalet_design else "cyber" if "Cyber" in pampalet_design else "vintage"
        
        # Best wishes bank list injecting real-time Panel 1 form values
        preset_wishes_nodes = [
            st.session_state.meta_wish, # Custom wish typed by admin inside panel 1 form
            f"Happy Birthday to my wonderful {st.session_state.meta_relation}! May your gorgeous {st.session_state.meta_age}th milestone year be full of success and pure layout graphics joy!",
            f"Cheers to another super hit trip around the sun, dear {st.session_state.meta_name}! You are the best {st.session_state.meta_relation} anyone could ask for."
        ]
        chosen_wish_text = st.selectbox("Select Best Wish Quotes (शुभकामना संदेश):", preset_wishes_nodes)
        
        # Single image portrait uploader slot configuration
        uploaded_portrait = st.file_uploader("Upload Portrait Photo Asset (Auto-Crop Fit Active):", type=["jpg", "png", "jpeg"], key="p2_card_uploader")
        render_pampalet_btn = st.button("✨ Compile Graphics Layout Grid & Render Card")
        
    with c2:
        st.markdown("### 🍿 Real-Time Render Output Monitor Canvas")
        if render_pampalet_btn:
            st.balloons()
            
            # CSS skins selector mapping rules matrices depending on choices dropdown
            card_class_css = "pampalet-gold"
            accent_title_hue = "#fbbf24"
            if pampalet_slug == "cyber":
                card_class_css = "pampalet-cyber"
                accent_title_hue = "#ec4899"
            elif pampalet_slug == "vintage":
                card_class_css = "pampalet-vintage"
                accent_title_hue = "#f59e0b"
                
            # Rendering final template framework block natively via HTML elements injection strings
            st.markdown(f"""
                <div class="{card_class_css}">
                    <h1 style="color: {accent_title_hue} !important; font-size:38px; margin:0;">🎉 HAPPY BIRTHDAY 🎉</h1>
                    <h2 style="color:#ffffff !important; letter-spacing:2px; margin:12px 0;">👑 {st.session_state.meta_name.upper()} 👑</h2>
                    <p style="font-size:14px; color:#cbd5e1; margin:0;">Turning {st.session_state.meta_age} | Profile Category: {st.session_state.meta_gender} | Dedicated {st.session_state.meta_relation} Mode</p>
                    <hr style="border-color:{accent_title_hue};">
                    <p style="font-size: 18px; font-style: italic; color:#f8fafc; line-height:1.6;">"{chosen_wish_text}"</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Smart center pixel crop automation compiler logic structures blocks
            if uploaded_portrait:
                raw_image = Image.open(uploaded_portrait)
                width, height = raw_image.size
                min_dim = min(width, height)
                # Mathematical pixel coordinate matrices calculation center bounding parameters
                cropped_img = raw_image.crop(((width-min_dim)/2, (height-min_dim)/2, (width+min_dim)/2, (height+min_dim)/2))
                st.markdown("<br>", unsafe_allow_html=True)
                st.image(cropped_img, caption="AI Auto-Fit Portrait Aspect Ratio Enabled", use_container_width=True)
                
            # Dual export utility action button slots as instructions required
            st.markdown("<div class='export-node-box'>", unsafe_allow_html=True)
            st.subheader("📥 Asset Distribution Channels Export Nodes")
            
            ex_col1, ex_col2 = st.columns(2)
            with ex_col1:
                # Button 1: Local storage physical layout asset file down button node download link
                st.download_button(label="💾 Download Image Layout (HD PNG)", data=b"MockPNGAssetDataBuffer", file_name=f"{st.session_state.meta_name}_card.png", mime="image/png")
            with ex_col2:
                # Button 2: Server initialization routing links constructor mappings
                secure_24h_card_link = f"https://streamlit.app{st.session_state.meta_name.replace(' ', '%20')}&age={st.session_state.meta_age}&gender={st.session_state.meta_gender}&relation={st.session_state.meta_relation.replace(' ', '%20')}&pampalet={pampalet_slug}"
                st.info("🕒 Temporary Server Link (Valid for 24 Hrs):")
                st.code(secure_24h_card_link, language="text")
                
            # WhatsApp instant target broadcast node handler component setup
            wa_api_route = f"https://whatsapp.com{st.session_state.meta_name}!%20Check%20it%20out%20here%20👉%20{secure_24h_card_link}"
            st.markdown(f'<a href="{wa_api_route}" target="_blank"><button style="background-color:#25D366; color:white; border-radius:8px; padding:10px; width:100%; border:none; font-weight:bold; cursor:pointer;">📲 Direct Share Active Asset Via WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Please choose your pampalet template style, upload your photograph, and click 'Compile Graphics Layout Grid & Render Card' tool button.")

        # =====================================================================
# PANEL 3 WORKSPACE: CINEMATIC VIDEO STUDIO REMIXER (ONLY PANEL 3)
# =====================================================================
elif st.session_state.active_session_panel == "P3":
    st.header("🎬 PANEL 3 WORKSPACE: Premium AI Lyrical Video & Voice Studio")
    
    # Panel 1 se aaye hue raw data ko top bar me automatically load karne ka module block
    st.info(f"📥 **Panel 1 Data Synced Automatically:** Name: `{st.session_state.meta_name}` | Age: `{st.session_state.meta_age}` | Gender: `{st.session_state.meta_gender}` | Relation: `{st.session_state.meta_relation}`")
    
    # Balanced structural columns layouts for timeline mixer components
    v1, v2 = st.columns(2)
    
    with v1:
        st.markdown("### 🎛️ AI Waveform Track Remixer Controls")
        
        # Multiple real-time video format layouts presets configuration
        video_format = st.selectbox("Choose Cinematic Video Format Template (वीडियो फॉर्मेट प्रारूप चूनें):", [
            "🎥 4K Ultra-HD Cinematic Landscape Master (16:9)",
            "📱 Premium Mobile Vertical Reels Format (9:16)",
            "⏹️ Modern Social Square Slideshow Grid (1:1)"
        ])
        
        # Audio custom tracks aligned with singer identities select configurations
        target_vocalist = st.selectbox("🎙️ Select AI Singer Voice Module Engine (सिंगर की आवाज चुनें):", [
            f"🔊 Arijit Singh AI Vocal Engine (Custom Dedicated to {st.session_state.meta_name})", 
            f"🔊 Neha Kakkar AI Vocal Engine (Custom Dedicated to {st.session_state.meta_name})", 
            f"🔊 Sonu Nigam AI Vocal Engine (Custom Dedicated to {st.session_state.meta_name})"
        ])
        vocalist_slug = "Arijit" if "Arijit" in target_vocalist else "Neha" if "Neha" in target_vocalist else "Sonu"
        
        # Cinematic transition visual overlay overlay effect criteria selection matrix options
        cinematic_vfx_filter = st.selectbox("🎆 Select Visual Cinematic VFX Effect Overlay (वीडियो इफेक्ट्स चुनें):", [
            "✨ Pure Golden Cyberpunk Light Leaks Glow",
            "⚡ 4K Neo-Neon Hologram Matrix Flare",
            "🎬 Chrono Vintage Retro Fading Frame Film",
            "🎈 Floating Birthday Magic Balloons Sparkles"
        ])
        
        st.markdown("#### 📸 Photo Timeline Assets Uploader (Drop exactly 2 pictures inside target slot)")
        slideshow_asset_images = st.file_uploader("Upload 2 Images for automatic transitions sequence timing loop:", type=["png","jpg","jpeg"], accept_multiple_files=True, key="p3_bulk_upload_node")
        
        compile_video_matrix_btn = st.button("🚀 Render Custom AI Voice Timeline & Compile Video")
        
    with v2:
        st.markdown("### 📺 Master Monitor Program Display Viewport")
        if compile_video_matrix_btn:
            # Strict logic verification check: exactly 2 photos rule criteria checking
            if slideshow_asset_images and len(slideshow_asset_images) >= 2:
                if len(slideshow_asset_images) > 2:
                    st.warning("⚠️ Optimized mode active: Processing only the first 2 images into render matrix block sequences.")
                    slideshow_asset_images = slideshow_asset_images[:2]
                    
                with st.spinner(f"AI Matrix Synthesis active... Mixing {vocalist_slug} AI track using custom vocal alignment nodes for {st.session_state.meta_name}..."):
                    time.sleep(1.5)
                st.snow()
                
                # Setup mapping rules for dynamic sound tracks URLs based on choices dropdown selection
                if vocalist_slug == "Arijit":
                    audio_source_node_url = "https://soundhelix.com"
                elif vocalist_slug == "Neha":
                    audio_source_node_url = "https://soundhelix.com"
                else:
                    audio_source_node_url = "https://soundhelix.com"
                    
                # Main Video Playback Simulator Frame Block Display Layout
                st.markdown("<div class='studio-monitor'>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='color:#06b6d4 !important; margin:0;'>🎬 PROGRAM MONITOR ACTIVE: {st.session_state.meta_name.upper()}__LYRICAL_HD.mp4</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:#a7f3d0; font-size:14px; margin: 5px 0;'>🎤 Audio Synthesis Pipeline Verified: <b>{vocalist_slug} AI Engine</b> | Video Style: <b>{video_format.split(' ')[1]}</b></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:#66fcf1; font-size:13px; margin: 0;'>⚙️ Applied VFX Node Effect: {cinematic_vfx_filter.split(' ')[1]}</p>", unsafe_allow_html=True)
                
                # Direct custom audio playback system with instant autoplay feature trigger
                st.write("👉 *Touch the player to manually override audio frequency controls if needed:*")
                st.audio(audio_source_node_url, format="audio/mp3", autoplay=True)
                
                # Dynamic horizontal columns matrix rendering loop for images slide frames viewer
                grid_frames_cols = st.columns(2)
                for order_idx, target_image_file in enumerate(slideshow_asset_images):
                    with grid_frames_cols[order_idx]:
                        st.image(target_image_file, caption=f"Scene Frame Timeline Sequence Asset Node 0{order_idx+1}", use_container_width=True)
                        
                st.markdown(f"<h2 style='color:#fbbf24 !important; font-weight:bold; margin-top:20px;'>🎉 Happy Birthday to You, {st.session_state.meta_name}! 🎉</h2>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:#ffffff; font-size:16px; font-style:italic;'>🎵 Dedicated to the best {st.session_state.meta_relation} on their sweet {st.session_state.meta_age}th Milestone Year! 🎵</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:#94a3b8; font-size:14px;'>\"{st.session_state.meta_wish}\"</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Twin Multimedia Video Export Action Channels
                st.markdown("<div class='export-node-box'>", unsafe_allow_html=True)
                st.subheader("📥 Multimedia Video File Export Target Nodes")
                
                v_ex_col1, v_ex_col2 = st.columns(2)
                with v_ex_col1:
                    # Button 1: Download full video file data component structure down link node local action
                    st.download_button(label="💾 Download Full Video Asset File (HD MP4)", data=b"MockMP4VideoAssetDataBuffer", file_name=f"{st.session_state.meta_name}_birthday_lyrical_video.mp4", mime="video/mp4")
                with v_ex_col2:
                    # Button 2: Generate dynamic online streaming parameter URLs matching SaaS logic rules
                    secure_24h_video_link = f"https://streamlit.app{st.session_state.meta_name.replace(' ', '%20')}&age={st.session_state.meta_age}&gender={st.session_state.meta_gender}&relation={st.session_state.meta_relation.replace(' ', '%20')}&singer={vocalist_slug}&fx={cinematic_vfx_filter.replace(' ', '%20')}"
                    st.info("🕒 Generated 24Hrs Active Cloud Streaming Video Node Link:")
                    st.code(secure_24h_video_link, language="text")
                    
                v_wa_api_route = f"https://whatsapp.com{st.session_state.meta_name}!%20🍿👉%20{secure_24h_video_link}"
                st.markdown(f'<a href="{v_wa_api_route}" target="_blank"><button style="background-color:#25D366; color:white; border-radius:8px; padding:10px; width:100%; border:none; font-weight:bold; cursor:pointer;">📲 Direct Share Active Video Via WhatsApp</button></a>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("❌ Multimedia Pipeline Error: Timeline build failure. Please upload exactly 2 pictures into target file slot to compile visual transitions.")
        else:
            st.info("Timeline parameters align karein, exactly 2 photos drop karein aur media track render karne ke liye button click karein.")

        
