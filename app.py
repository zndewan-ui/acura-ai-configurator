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

# --- 2. 2026 ACURA LINEUP DATA ---
# Personality traits and specs based on official Acura Canada data
ACURA_MODELS = {
    "Integra Type S": {
        "hp": 320, "torque": 310, 
        "traits": "The Purist. You value raw mechanical connection, a close-ratio 6-speed manual, and track-ready performance.",
        "colors": ["Apex Blue Pearl", "Tiger Eye Pearl", "Majestic Black", "Championship White"]
    },
    "TLX Type S": {
        "hp": 355, "torque": 354, 
        "traits": "The Executive Athlete. You want an aggressive sport sedan with a Turbo V6 and Super Handling All-Wheel Drive.",
        "colors": ["Urban Gray Pearl", "Apex Blue Pearl", "Majestic Black", "Performance Red Pearl"]
    },
    "ADX Platinum": {
        "hp": 190, "torque": 179, 
        "traits": "The Urban Adventurer. You seek a tech-forward, premium compact SUV with versatile AWD for active city living.",
        "colors": ["Urban Gray Pearl", "Double Apex Blue Pearl II", "Platinum White Pearl"]
    },
    "RDX A-Spec": {
        "hp": 272, "torque": 280, 
        "traits": "The Balanced Versatile. You demand turbo performance mixed with premium crossover utility and bold A-Spec styling.",
        "colors": ["Berlina Black", "Apex Blue Pearl", "Performance Red Pearl", "Lunar Silver Metallic"]
    },
    "MDX Type S": {
        "hp": 355, "torque": 354, 
        "traits": "The Power Leader. You need a 7-passenger SUV with a Turbo V6 engine and an adrenaline-seeking soul.",
        "colors": ["Urban Gray Pearl", "Performance Red Pearl", "Majestic Black", "Liquid Carbon Metallic"]
    },
    "ZDX Type S": {
        "hp": 500, "torque": 544, 
        "traits": "The Future Specialist. You want Acura's most powerful SUV ever, featuring instant electric torque and elite tech.",
        "colors": ["Double Apex Blue Pearl", "Urban Gray Pearl", "Majestic Black"]
    }
}

CAR_ASSETS = {
    "Integra Type S": {
        "Apex Blue Pearl": "https://acura.ca/etc/designs/AcuraCA/Static/images/models/integra/2026/top-view.png",
        "Tiger Eye Pearl": "https://www.acura.com/-/media/Acura-Platform/Models/Integra/2024/Type-S/Overview/Hero/2024-Integra-Type-S-Hero-M.jpg",
        "Championship White": "https://acura.ca/Content/AcuraCA/Static/images/models/integra/2026/gallery/integra-4.jpg",
        "Majestic Black": "https://acura.ca/Content/AcuraCA/Static/images/models/integra/2026/gallery/integra-1.jpg"
    },
    "TLX Type S": {
        "Urban Gray Pearl": "https://www.acura.ca/Content/AcuraCA/Models/TLX/2024/site-assets/hero/hero-desktop.jpg",
        "Apex Blue Pearl": "https://www.acura.ca/Content/AcuraCA/Models/TLX/2024/site-assets/gallery/exterior/tlx-1.jpg",
        "Majestic Black": "https://www.acura.ca/Content/AcuraCA/Models/TLX/2024/site-assets/gallery/exterior/tlx-2.jpg",
        "Performance Red Pearl": "https://www.acura.ca/Content/AcuraCA/Models/TLX/2024/site-assets/gallery/exterior/tlx-3.jpg"
    },
    "ADX Platinum": {
        "Urban Gray Pearl": "https://www.acura.ca/Content/AcuraCA/Models/ADX/2026/site-assets/hero/hero-desktop.jpg",
        "Double Apex Blue Pearl II": "https://www.acura.ca/Content/AcuraCA/Models/ADX/2026/site-assets/gallery/exterior/adx-1.jpg",
        "Platinum White Pearl": "https://www.acura.ca/Content/AcuraCA/Models/ADX/2026/site-assets/gallery/exterior/adx-2.jpg"
    },
    "RDX A-Spec": {
        "Berlina Black": "https://www.acura.ca/Content/AcuraCA/Models/RDX/2026/site-assets/hero/hero-desktop.jpg",
        "Apex Blue Pearl": "https://www.acura.ca/Content/AcuraCA/Models/RDX/2026/site-assets/gallery/exterior/rdx-1.jpg",
        "Performance Red Pearl": "https://www.acura.ca/Content/AcuraCA/Models/RDX/2026/site-assets/gallery/exterior/rdx-2.jpg",
        "Lunar Silver Metallic": "https://www.acura.ca/Content/AcuraCA/Models/RDX/2026/site-assets/gallery/exterior/rdx-3.jpg"
    },
    "MDX Type S": {
        "Urban Gray Pearl": "https://www.acura.ca/Content/AcuraCA/Models/MDX/2026/site-assets/hero/hero-desktop.jpg",
        "Performance Red Pearl": "https://www.acura.ca/Content/AcuraCA/Models/MDX/2026/site-assets/gallery/exterior/mdx-1.jpg",
        "Majestic Black": "https://www.acura.ca/Content/AcuraCA/Models/MDX/2026/site-assets/gallery/exterior/mdx-2.jpg",
        "Liquid Carbon Metallic": "https://www.acura.ca/Content/AcuraCA/Models/MDX/2026/site-assets/gallery/exterior/mdx-3.jpg"
    },
    "ZDX Type S": {
        "Double Apex Blue Pearl": "https://www.acura.ca/Content/AcuraCA/Models/ZDX/2024/site-assets/hero/hero-desktop.jpg",
        "Urban Gray Pearl": "https://www.acura.ca/Content/AcuraCA/Models/ZDX/2024/site-assets/gallery/exterior/zdx-1.jpg",
        "Majestic Black": "https://www.acura.ca/Content/AcuraCA/Models/ZDX/2024/site-assets/gallery/exterior/zdx-2.jpg"
    }
}

# --- 3. SESSION STATE ---
if "app_state" not in st.session_state:
    st.session_state.app_state = "CHAT"
if "selected_car" not in st.session_state:
    st.session_state.selected_car = "Integra Type S"
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False

# Connect to Gemini 2.5 Flash
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 4. PHASE 1: THE AI INTERVIEW ---
if st.session_state.app_state == "CHAT":
    st.image("https://www.acura.ca/Content/AcuraCA/Static/logo/acura_logo_white.png", width=120)
    st.title("Precision Personality Sync")
    st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)
    
    prompt = st.chat_input("Tell me... do you chase the redline or the horizon?")
    
    if prompt:
        with st.spinner("Analyzing Driver DNA..."):
            # The AI pulls from our personality traits list
            personality_data = "\n".join([f"{k}: {v['traits']}" for k,v in ACURA_MODELS.items()])
            instruction = f"You are a high-energy Acura specialist. Based on the driver's response: '{prompt}', recommend ONE model from this list: {personality_data}. Explain your choice with NFS-style energy."
            res = model.generate_content(instruction)
            st.write(f"### Specialist: {res.text}")
            
            # Extract the car name from the response to update the garage automatically
            for car in ACURA_MODELS.keys():
                if car in res.text:
                    st.session_state.selected_car = car
            st.session_state.chat_complete = True

    if st.session_state.chat_complete:
        st.write("---")
        if st.button(f"ENTER THE GARAGE: {st.session_state.selected_car.upper()}"):
            st.session_state.app_state = "GARAGE"
            st.rerun()

# --- 5. PHASE 2: THE NFS GARAGE ---
else:
    st.title(f"PROJECT: {st.session_state.selected_car.upper()}")
    st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)
    
    col_vis, col_ui = st.columns([2, 1])
    
    with col_ui:
        st.markdown('<div class="garage-panel">', unsafe_allow_html=True)
        st.subheader("🛠️ EXTERIOR CONFIG")
        
        # Color mapping logic
        colors = ACURA_MODELS[st.session_state.selected_car]["colors"]
        paint = st.pills("PAINT FINISH", colors, default=colors[0])
        
        st.markdown("---")
        st.subheader("PERFORMANCE HUD")
        stats = ACURA_MODELS[st.session_state.selected_car]
        st.metric("POWER", f"{stats['hp']} HP")
        st.metric("TORQUE", f"{stats['torque']} LB-FT")
        
        if st.button("🔥 LOCK IN BUILD"):
            st.balloons()
            st.success("Build Secured. Your specialist will contact you.")
        
        if st.button("← BACK TO SYNC"):
            st.session_state.app_state = "CHAT"
            st.session_state.chat_complete = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_vis:
        # Dynamic visual lookup
        img_url = CAR_ASSETS[st.session_state.selected_car][paint]
        st.image(img_url, use_container_width=True, caption=f"2026 {st.session_state.selected_car} // {paint}")
