import streamlit as st
import google.generativeai as genai
import time

# --- 1. THE SHOWROOM DESIGN (CSS) ---
st.set_page_config(page_title="Acura Precision Configurator", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1, h2, h3 { text-transform: uppercase; letter-spacing: 2px; font-weight: 800 !important; }
    .stButton>button { 
        background-color: #E4002B; color: white; border-radius: 0px; border: none; 
        font-weight: bold; padding: 10px; transition: 0.5s;
    }
    .stButton>button:hover { background-color: #ffffff; color: #E4002B; transform: scale(1.02); }
    .red-accent { height: 4px; background-color: #E4002B; margin-bottom: 25px; }
    /* Garage Menu Styling */
    .garage-card { 
        background: #111; padding: 25px; border-left: 5px solid #E4002B;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    </style>
    <div class="red-accent"></div>
    """, unsafe_allow_html=True)

# --- 2. THE VISUALIZER DATABASE ---
# These are mapped to official Acura design colors for the 2026 lineup
CAR_ASSETS = {
    "Integra Type S": {
        "Apex Blue Pearl": "https://www.acura.ca/Content/AcuraCA/Models/Integra/2026/site-assets/hero/hero-desktop.jpg",
        "Tiger Eye Pearl": "https://www.acura.com/-/media/Acura-Platform/Models/Integra/2024/Type-S/Overview/Hero/2024-Integra-Type-S-Hero-M.jpg",
        "Championship White": "https://www.acura.ca/Content/AcuraCA/Static/images/models/integra/2026/top-view.png",
        "Majestic Black": "https://www.acura.ca/Content/AcuraCA/Static/images/models/integra/2026/gallery/integra-1.jpg"
    },
    "MDX Type S": {
        "Urban Gray Pearl": "https://www.acura.ca/Content/AcuraCA/Models/MDX/2026/site-assets/hero/hero-desktop.jpg",
        "Performance Red Pearl": "https://www.acura.ca/Content/AcuraCA/Models/MDX/2026/site-assets/gallery/exterior/mdx-1.jpg",
        "Majestic Black": "https://www.acura.ca/Content/AcuraCA/Models/MDX/2026/site-assets/gallery/exterior/mdx-2.jpg"
    }
}

# --- 3. LOGIC & AI SETUP ---
if "app_state" not in st.session_state:
    st.session_state.app_state = "CHAT"
if "selected_car" not in st.session_state:
    st.session_state.selected_car = "Integra Type S"

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

# --- 4. PHASE 1: THE AI INTERVIEW ---
if st.session_state.app_state == "CHAT":
    st.image("https://www.acura.ca/Content/AcuraCA/Static/logo/acura_logo_white.png", width=150)
    st.title("Precision Personality Sync")
    
    with st.container():
        st.write("### ANALYZING DRIVER DNA...")
        prompt = st.chat_input("Tell me... do you chase the redline or the horizon?")
        
        if prompt:
            with st.spinner("Processing..."):
                res = model.generate_content(f"You are a high-energy Acura specialist. Based on '{prompt}', recommend the Integra Type S or MDX Type S. Be brief and punchy.")
                st.write(f"**Specialist:** {res.text}")
                
            if st.button("ENTER THE GARAGE"):
                st.session_state.app_state = "GARAGE"
                st.rerun()

# --- 5. PHASE 2: THE NFS VISUALIZER ---
else:
    st.title(f"PROJECT: {st.session_state.selected_car.upper()}")
    
    # HUD Layout
    col_vis, col_ui = st.columns([2, 1])
    
    with col_ui:
        st.markdown('<div class="garage-card">', unsafe_allow_html=True)
        st.subheader("🛠️ EXTERIOR CONFIG")
        
        # COLOR SELECTOR (This triggers the visualizer)
        available_colors = list(CAR_ASSETS[st.session_state.selected_car].keys())
        paint = st.pills("PAINT FINISH", available_colors, default=available_colors[0])
        
        st.markdown("---")
        st.subheader("PERFORMANCE STATS")
        st.metric("HORSEPOWER", "320 HP", "STAGE 1")
        st.metric("0-100 KM/H", "5.1s", "EXCELLENT")
        
        if st.button("🔥 LOCK IN BUILD"):
            st.balloons()
            st.success("BUILD SENT TO DEALERSHIP. ACCESS GRANTED.")
        
        if st.button("← RETURN TO SYNC"):
            st.session_state.app_state = "CHAT"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_vis:
        # THE VISUALIZER: Updates image based on 'paint' selection
        img_url = CAR_ASSETS[st.session_state.selected_car][paint]
        st.image(img_url, use_container_width=True, caption=f"2026 {st.session_state.selected_car} // {paint}")

