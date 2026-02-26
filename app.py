import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
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
        "traits": "The Purist. You value raw mechanical connection and track-ready performance.",
        "colors": ["Apex Blue Pearl", "Tiger Eye Pearl", "Championship White"]
    },
    "TLX Type S": {
        "hp": 355, "torque": 354, 
        "traits": "The Executive Athlete. You demand a sharp sport sedan with Turbo V6 and SH-AWD®.",
        "colors": ["Urban Gray Pearl", "Apex Blue Pearl", "Performance Red Pearl"]
    },
    "ADX Platinum": {
        "hp": 190, "torque": 179, 
        "traits": "The Urban Adventurer. A tech-forward subcompact SUV for active city life.",
        "colors": ["Urban Gray Pearl", "Double Apex Blue Pearl II", "Platinum White Pearl"]
    },
    "RDX A-Spec": {
        "hp": 272, "torque": 280, 
        "traits": "The Balanced Versatile. Turbo VTEC® power meets premium crossover utility.",
        "colors": ["Berlina Black", "Apex Blue Pearl", "Performance Red Pearl"]
    },
    "MDX Type S": {
        "hp": 355, "torque": 354, 
        "traits": "The Power Leader. A 7-passenger SUV that rules the road with predatory intent.",
        "colors": ["Urban Gray Pearl", "Performance Red Pearl", "Majestic Black"]
    },
    "ZDX Type S": {
        "hp": 499, "torque": 544, 
        "traits": "The Future Specialist. Instant electric torque and ground-breaking technology.",
        "colors": ["Double Apex Blue Pearl", "Urban Gray Pearl", "Majestic Black"]
    }
}

# --- 3. SESSION STATE & CLIENT SETUP ---
if "app_state" not in st.session_state: st.session_state.app_state = "CHAT"
if "selected_car" not in st.session_state: st.session_state.selected_car = "Integra Type S"
if "chat_complete" not in st.session_state: st.session_state.chat_complete = False
if "current_image" not in st.session_state: st.session_state.current_image = None

# New Client Initialization for Gemini 2.5 Flash
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- AI IMAGE ENGINE ---
def generate_ai_garage_render(car, color):
    prompt = f"Professional 3D automotive render of a 2026 {car} in {color}, NFS aesthetic, cinematic lighting, 8k resolution."
    response = client.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt=prompt,
        config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="16:9")
    )
    return Image.open(BytesIO(response.generated_images[0].image.image_bytes))

# --- 4. PHASE 1: THE AI INTERVIEW ---
if st.session_state.app_state == "CHAT":
    st.image("https://www.acura.ca/Content/AcuraCA/Static/logo/acura_logo_white.png", width=120)
    st.title("Precision Personality Sync")
    st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)
    
    prompt = st.chat_input("Tell me... do you chase the redline or the horizon?")
    
    if prompt:
        with st.spinner("Analyzing DNA..."):
            personality_context = "\n".join([f"{k}: {v['traits']}" for k,v in ACURA_MODELS.items()])
            res = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=f"Recommend ONE car from: {personality_context} based on: {prompt}."
            )
            st.write(f"### Specialist: {res.text}")
            for car in ACURA_MODELS.keys():
                if car in res.text: st.session_state.selected_car = car
            st.session_state.chat_complete = True

    if st.session_state.chat_complete:
        if st.button(f"ENTER GARAGE: {st.session_state.selected_car.upper()}"):
            st.session_state.app_state = "GARAGE"
            st.rerun() # Trigger rerun to switch phases

# --- 5. PHASE 2: THE AI VISUALIZER GARAGE ---
else:
    st.title(f"PROJECT: {st.session_state.selected_car.upper()}")
    st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)
    
    col_vis, col_ui = st.columns([2, 1])
    
    with col_ui:
        st.markdown('<div class="garage-panel">', unsafe_allow_html=True)
        st.subheader("🛠️ CONFIG")
        colors = ACURA_MODELS[st.session_state.selected_car]["colors"]
        paint = st.pills("PAINT", colors, default=colors[0])
        
        st.subheader("HUD")
        stats = ACURA_MODELS[st.session_state.selected_car]
        st.metric("POWER", f"{stats['hp']} HP")
        st.metric("TORQUE", f"{stats['torque']} LB-FT")
        
        if st.button("🚀 GENERATE AI RENDER"):
            with st.spinner("Rendering..."):
                st.session_state.current_image = generate_ai_garage_render(st.session_state.selected_car, paint)
        
        if st.button("← BACK"):
            st.session_state.app_state = "CHAT"
            st.session_state.chat_complete = False
            st.session_state.current_image = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_vis:
        if st.session_state.current_image:
            st.image(st.session_state.current_image, use_container_width=True)
        else:
            st.info("Click 'GENERATE AI RENDER' to see your build.")
