import streamlit as st
import google.generativeai as genai
import time

# --- 1. ACURA CANADA VISUAL ENGINE (CSS) ---
st.set_page_config(page_title="Acura Precision Configurator", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1, h2, h3 { text-transform: uppercase; letter-spacing: 2px; font-weight: 700 !important; }
    .stButton>button { 
        background-color: #E4002B; color: white; border-radius: 0px; border: none; 
        font-weight: bold; width: 100%; height: 3em; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #ffffff; color: #E4002B; }
    .red-line { height: 4px; background-color: #E4002B; margin: 10px 0 30px 0; }
    .garage-panel { background: #111; padding: 20px; border-left: 5px solid #E4002B; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURATOR DATABASE ---
ACURA_MODELS = {
    "Integra Type S": {"hp": 320, "torque": 310, "colors": ["Apex Blue Pearl", "Tiger Eye Pearl", "Majestic Black", "Championship White"]},
    "MDX Type S": {"hp": 355, "torque": 354, "colors": ["Urban Gray Pearl", "Performance Red Pearl", "Majestic Black"]}
}

# --- 3. SESSION STATE ---
if "app_state" not in st.session_state:
    st.session_state.app_state = "CHAT"
if "selected_car" not in st.session_state:
    st.session_state.selected_car = "Integra Type S"
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False

# Fix: Use a valid model name (1.5-flash)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 4. PHASE 1: THE AI INTERVIEW ---
if st.session_state.app_state == "CHAT":
    st.image("https://www.acura.ca/Content/AcuraCA/Static/logo/acura_logo_white.png", width=120)
    st.title("Precision Personality Sync")
    st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)
    
    prompt = st.chat_input("Tell me... do you chase the redline or the horizon?")
    
    if prompt:
        with st.spinner("Analyzing Driver DNA..."):
            # Fix: Using valid model for content generation
            res = model.generate_content(f"You are a high-energy Acura specialist. Based on '{prompt}', recommend the Integra Type S or MDX Type S. Be brief and punchy.")
            st.write(f"### Specialist: {res.text}")
            st.session_state.chat_complete = True

    # Fix: Button moved OUTSIDE the 'if prompt' block so it stays visible
    if st.session_state.chat_complete:
        st.write("---")
        if st.button("ENTER THE GARAGE"):
            st.session_state.app_state = "GARAGE"
            st.rerun()

# --- 5. PHASE 2: THE NFS GARAGE ---
else:
    st.title(f"PROJECT: {st.session_state.selected_car.upper()}")
    st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)
    
    col_vis, col_ui = st.columns([2, 1])
    
    with col_ui:
        st.markdown('<div class="garage-panel">', unsafe_allow_html=True)
        st.subheader("🛠️ EXTERIOR")
        
        colors = ACURA_MODELS[st.session_state.selected_car]["colors"]
        paint = st.pills("PAINT FINISH", colors, default=colors[0])
        
        st.markdown("---")
        st.subheader("PERFORMANCE HUD")
        st.metric("POWER", f"{ACURA_MODELS[st.session_state.selected_car]['hp']} HP")
        st.metric("TORQUE", f"{ACURA_MODELS[st.session_state.selected_car]['torque']} LB-FT")
        
        if st.button("🔥 LOCK IN BUILD"):
            st.balloons()
            st.success("Build Secured. Welcome to the Family.")
        
        if st.button("← BACK TO SYNC"):
            st.session_state.app_state = "CHAT"
            st.session_state.chat_complete = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_vis:
        # Visualizer placeholder matching the Acura aesthetic
        st.image("https://www.acura.ca/Content/AcuraCA/Models/Integra/2026/site-assets/hero/hero-desktop.jpg", use_container_width=True)
