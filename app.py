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
ACURA_MODELS = {
    "Integra Type S": {
        "hp": 320, "torque": 310, 
        "traits": "The Purist. You value raw mechanical connection, a 6-speed manual, and track-ready performance.",
        "colors": ["Apex Blue Pearl", "Tiger Eye Pearl", "Majestic Black", "Championship White"]
    },
    "TLX Type S": {
        "hp": 355, "torque": 354, 
        "traits": "The Executive Athlete. You want a sharp sport sedan with Turbo V6 power and SH-AWD® handling.",
        "colors": ["Urban Gray Pearl", "Apex Blue Pearl", "Majestic Black", "Performance Red Pearl"]
    },
    "ADX Platinum": {
        "hp": 190, "torque": 179, 
        "traits": "The Urban Adventurer. You're tech-focused and active, seeking a stylish, premium compact SUV for city life.",
        "colors": ["Urban Gray Pearl", "Double Apex Blue Pearl II", "Platinum White Pearl"]
    },
    "RDX A-Spec": {
        "hp": 272, "torque": 280, 
        "traits": "The Balanced Versatile. You demand turbo power mixed with premium utility and bold A-Spec styling.",
        "colors": ["Berlina Black", "Apex Blue Pearl", "Performance Red Pearl", "Lunar Silver Metallic"]
    },
    "MDX Type S": {
        "hp": 355, "torque": 354, 
        "traits": "The Power Leader. You need a 7-passenger SUV that doesn't compromise on its high-performance soul.",
        "colors": ["Urban Gray Pearl", "Performance Red Pearl", "Majestic Black", "Liquid Carbon Metallic"]
    },
    "ZDX Type S": {
        "hp": 500, "torque": 544, 
        "traits": "The Future Specialist. You want Acura's most powerful SUV ever with instant electric torque.",
        "colors": ["Double Apex Blue Pearl", "Urban Gray Pearl", "Majestic Black"]
    }
}

# --- 3. STABLE IMAGE ASSETS ---
CAR_ASSETS = {
    "Integra Type S": "https://acuranews.com/en-US/releases/release-94943f6797b5e0ad0fee5bfc721464c8/download/46369",
    "TLX Type S": "https://acuranews.com/en-US/releases/release-15f53f6797b5e0ad0fee5bfc72401889/download/47281",
    "ADX Platinum": "https://acuranews.com/en-US/releases/release-0b15294a3c3300ad0fee5bfc7201a1cf/download/48201",
    "RDX A-Spec": "https://acuranews.com/en-US/releases/release-aa388dfd6f431bbab748dcd4ec00e6ad/download/47912",
    "MDX Type S": "https://acuranews.com/en-US/releases/release-33943f6797b5e0ad0fee5bfc72183c51/download/46824",
    "ZDX Type S": "https://acuranews.com/en-US/releases/release-d8e7e3d744b0a8d7736d6e20aa09ba8e/download/46001"
}

# --- 4. SESSION STATE & AI SETUP ---
if "app_state" not in st.session_state: st.session_state.app_state = "CHAT"
if "selected_car" not in st.session_state: st.session_state.selected_car = "Integra Type S"
if "chat_complete" not in st.session_state: st.session_state.chat_complete = False

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 5. PHASE 1: THE AI INTERVIEW ---
if st.session_state.app_state == "CHAT":
    st.image("https://www.acura.ca/Content/AcuraCA/Static/logo/acura_logo_white.png", width=120)
    st.title("Precision Personality Sync")
    st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)
    
    prompt = st.chat_input("Tell me... do you chase the redline or the horizon?")
    
    if prompt:
        with st.spinner("Analyzing Driver DNA..."):
            personality_context = "\n".join([f"{k}: {v['traits']}" for k,v in ACURA_MODELS.items()])
            instruction = f"Recommend ONE Acura from this list: {personality_context}. Use 'Need for Speed' energy."
            res = model.generate_content(instruction)
            st.write(f"### Specialist: {res.text}")
            
            for car in ACURA_MODELS.keys():
                if car in res.text: st.session_state.selected_car = car
            st.session_state.chat_complete = True

    if st.session_state.chat_complete:
        if st.button(f"ENTER GARAGE: {st.session_state.selected_car.upper()}"):
            st.session_state.app_state = "GARAGE"
            st.rerun()

# --- 6. PHASE 2: THE NFS GARAGE ---
else:
    st.title(f"PROJECT: {st.session_state.selected_car.upper()}")
    st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)
    
    col_vis, col_ui = st.columns([2, 1])
    
    with col_ui:
        st.markdown('<div class="garage-panel">', unsafe_allow_html=True)
        st.subheader("🛠️ EXTERIOR")
        colors = ACURA_MODELS[st.session_state.selected_car]["colors"]
        paint = st.pills("PAINT", colors, default=colors[0])
        
        st.subheader("PERFORMANCE HUD")
        stats = ACURA_MODELS[st.session_state.selected_car]
        st.metric("POWER", f"{stats['hp']} HP")
        st.metric("TORQUE", f"{stats['torque']} LB-FT")
        
        if st.button("🔥 LOCK IN BUILD"): st.balloons()
        if st.button("← BACK"):
            st.session_state.app_state = "CHAT"
            st.session_state.chat_complete = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_vis:
        # Using Newsroom assets which are less likely to be blocked
        st.image(CAR_ASSETS[st.session_state.selected_car], use_container_width=True)
