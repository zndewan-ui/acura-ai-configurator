import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import random

# --- 1. ACURA BRAND STYLING (CSS) ---
st.set_page_config(page_title="Acura Precision Configurator", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1, h2, h3 { text-transform: uppercase; letter-spacing: 2px; font-weight: 700 !important; }
    .stButton>button { 
        background-color: #E4002B; color: white; border-radius: 0px; border: none; 
        font-weight: bold; width: 100%; height: 3.5em; transition: 0.3s;
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
        "traits": "The Purist. You value visceral engagement and raw mechanical connection.",
        "colors": ["Apex Blue Pearl", "Tiger Eye Pearl", "Championship White", "Solar Silver Metallic"]
    },
    "ADX Platinum": {
        "hp": 190, "torque": 179,
        "traits": "The Urban Adventurer. A premium, tech-focused compact SUV for active city life.",
        "colors": ["Urban Gray Pearl", "Double Apex Blue Pearl II", "Platinum White Pearl"]
    },
    "MDX Type S Ultra": {
        "hp": 355, "torque": 354,
        "traits": "The Power Leader. A high-performing 7-seater at the absolute pinnacle.",
        "colors": ["Performance Red Pearl", "Urban Gray Pearl", "Majestic Black Pearl"]
    },
    "RDX A-Spec": {
        "hp": 272, "torque": 280,
        "traits": "The Balanced Versatile. Turbo power meets premium utility and bold styling.",
        "colors": ["Berlina Black", "Apex Blue Pearl", "Performance Red Pearl"]
    },
    "TLX Type S": {
        "hp": 355, "torque": 354,
        "traits": "The Executive Athlete. Racetrack-inspired performance in a sophisticated sedan.",
        "colors": ["Urban Gray Pearl", "Apex Blue Pearl", "Majestic Black"]
    },
    "ZDX Type S": {
        "hp": 500, "torque": 544,
        "traits": "The Future Specialist. Instant electric torque in the most powerful Acura SUV ever.",
        "colors": ["Double Apex Blue Pearl", "Urban Gray Pearl", "Majestic Black"]
    }
}

# --- 3. SESSION STATE & CLIENT SETUP ---
if "app_state" not in st.session_state: st.session_state.app_state = "CHAT"
if "selected_car" not in st.session_state: st.session_state.selected_car = "Integra Type S"
if "chat_complete" not in st.session_state: st.session_state.chat_complete = False
if "current_image" not in st.session_state: st.session_state.current_image = None

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def generate_ai_render(car, color):
    """Generate car image using Gemini 2.0 Flash image generation (no special access required)."""
    noise = random.randint(1, 1000000)
    prompt = (
        f"Professional 3D automotive render of a 2026 Acura {car} in {color} paint, "
        f"cinematic studio lighting, dark garage background, NFS aesthetic, "
        f"ultra-realistic, 8k resolution, ray-tracing reflections. Variation ID: {noise}"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"]
            )
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                return Image.open(BytesIO(part.inline_data.data))

        st.error("No image was returned. Please try again.")
        return None

    except Exception as e:
        st.error(f"Image generation failed: {e}")
        return None


# --- 4. PHASE 1: THE AI INTERVIEW ---
if st.session_state.app_state == "CHAT":
    st.image("https://www.acura.ca/Content/AcuraCA/Static/logo/acura_logo_white.png", width=120)
    st.title("Precision Personality Sync")
    st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)

    prompt = st.chat_input("Do you chase the redline or the horizon?")

    if prompt:
        with st.spinner("Analyzing DNA..."):
            context = "\n".join([f"{k}: {v['traits']}" for k, v in ACURA_MODELS.items()])
            try:
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=(
                        f"You are an Acura performance specialist. "
                        f"Recommend exactly ONE Acura model from this list: {context} "
                        f"based on the customer's response: '{prompt}'. "
                        f"Be high energy, bold, and mention the model name clearly."
                    )
                )
                st.write(f"### Specialist: {res.text}")
                for car in ACURA_MODELS.keys():
                    if car in res.text:
                        st.session_state.selected_car = car
                        break
                st.session_state.chat_complete = True
            except Exception as e:
                st.error(f"Chat error: {e}")

    if st.session_state.chat_complete:
        if st.button(f"ENTER GARAGE: {st.session_state.selected_car.upper()}"):
            st.session_state.app_state = "GARAGE"
            st.rerun()

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

        if st.button("🚀 GENERATE NEW AI RENDER"):
            with st.spinner("Rendering unique 3D build..."):
                st.session_state.current_image = generate_ai_render(
                    st.session_state.selected_car, paint
                )

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
            st.info("Click 'GENERATE NEW AI RENDER' to see your custom build.")
