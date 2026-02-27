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

# --- 2. 2026 ACURA CANADA FULL LINEUP DATA ---
ACURA_MODELS = {
    "Integra": {
        "hp": 200, "torque": 192,
        "traits": "The Daily Driver. A sporty hatchback-sedan with a VTEC Turbo engine and available 6-speed manual. The everyday Acura that never gets boring.",
        "colors": ["Urban Gray Pearl", "Apex Blue Pearl", "Platinum White Pearl", "Sonic Gray Pearl", "Performance Red Pearl", "Majestic Black Pearl"]
    },
    "Integra Type S": {
        "hp": 320, "torque": 310,
        "traits": "The Purist. The most powerful Integra ever built. A close-ratio 6-speed manual, Brembo brakes, and 320HP — raw mechanical connection at its finest.",
        "colors": ["Apex Blue Pearl", "Tiger Eye Pearl", "Championship White", "Solar Silver Metallic", "Gotham Gray Pearl"]
    },
    "TLX": {
        "hp": 272, "torque": 280,
        "traits": "The Refined Performer. A luxury sports sedan with standard SH-AWD and a turbocharged engine. Precision meets premium every single day.",
        "colors": ["Liquid Carbon Metallic", "Platinum White Pearl", "Majestic Black Pearl", "Apex Blue Pearl", "Performance Red Pearl"]
    },
    "TLX Type S": {
        "hp": 355, "torque": 354,
        "traits": "The Executive Athlete. Racetrack-inspired 3.0L Turbo V6, NSX-derived brakes, and Brembo calipers. The most powerful Acura sedan ever built.",
        "colors": ["Urban Gray Pearl", "Apex Blue Pearl", "Majestic Black Pearl", "Liquid Carbon Metallic", "Performance Red Pearl"]
    },
    "ADX": {
        "hp": 190, "torque": 179,
        "traits": "The Urban Adventurer. A nimble, tech-loaded compact SUV built for city life and weekend escapes. Premium Bang & Olufsen sound included.",
        "colors": ["Urban Gray Pearl", "Double Apex Blue Pearl II", "Platinum White Pearl", "Sonic Gray Pearl", "Majestic Black Pearl"]
    },
    "RDX A-Spec": {
        "hp": 272, "torque": 280,
        "traits": "The Balanced Versatile. Sport crossover with turbo power, SH-AWD torque vectoring, and bold A-Spec styling. Engineered to lead every day.",
        "colors": ["Berlina Black", "Apex Blue Pearl", "Performance Red Pearl", "Liquid Carbon Metallic", "Platinum White Pearl"]
    },
    "MDX": {
        "hp": 290, "torque": 267,
        "traits": "The Family Commander. A 3-row V6 SUV with racecar-derived engine DNA, spacious premium cabin, and available SH-AWD for confident all-weather performance.",
        "colors": ["Platinum White Pearl", "Urban Gray Pearl", "Majestic Black Pearl", "Performance Red Pearl", "Apex Blue Pearl"]
    },
    "MDX Type S": {
        "hp": 355, "torque": 354,
        "traits": "The Power Leader. A 7-seat SUV at the pinnacle of performance. 3.0L Turbo V6, adaptive air suspension, and quad exhaust — family hauler redefined.",
        "colors": ["Performance Red Pearl", "Urban Gray Pearl", "Majestic Black Pearl", "Apex Blue Pearl", "Platinum White Pearl"]
    },
    "ZDX Type S": {
        "hp": 500, "torque": 544,
        "traits": "The Electric Vanguard. Instant torque, zero emissions, 500HP. The most powerful Acura SUV ever built and a glimpse into the electrified future of the brand.",
        "colors": ["Double Apex Blue Pearl", "Urban Gray Pearl", "Majestic Black Pearl", "Performance Red Pearl"]
    },
}

# --- 3. SESSION STATE & CLIENT SETUP ---
if "app_state" not in st.session_state: st.session_state.app_state = "CHAT"
if "selected_car" not in st.session_state: st.session_state.selected_car = "Integra Type S"
if "chat_complete" not in st.session_state: st.session_state.chat_complete = False
if "current_image" not in st.session_state: st.session_state.current_image = None
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "recommendation_text" not in st.session_state: st.session_state.recommendation_text = ""

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
            model="gemini-2.5-flash-image",
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
    st.image("https://pngimg.com/uploads/acura/acura_PNG73.png", width=120)
    st.title("Let's Find Your Dream Acura")
    st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)

    if not st.session_state.chat_complete:
        st.markdown("#### Tell us a little about yourself and we'll match you with your perfect Acura.")
        st.markdown("")

        name = st.text_input("👤 First Name", placeholder="e.g. Alex")

        lifestyle = st.selectbox("🌆 How would you describe your lifestyle?", [
            "— Select —",
            "Urban professional — city commutes, weekend trips",
            "Family-focused — need space, safety, and comfort",
            "Performance enthusiast — I drive for the feel of it",
            "Adventure seeker — trails, road trips, outdoors",
            "Eco-conscious — sustainability matters to me",
        ])

        priorities = st.multiselect("🏁 What matters most to you in a vehicle? (pick up to 3)", [
            "Raw performance & horsepower",
            "Luxury & premium interior",
            "Technology & connectivity",
            "Practicality & cargo space",
            "Fuel efficiency / EV range",
            "Bold, head-turning styling",
            "All-weather capability",
            "Driving engagement & manual control",
        ], max_selections=3)

        personality = st.text_area(
            "✍️ Describe yourself in a few words (optional)",
            placeholder="e.g. I'm competitive, always on the go, love weekend track days but also need to seat 5..."
        )

        st.markdown("")
        if st.button("🔍 FIND MY ACURA"):
            if not name:
                st.warning("Please enter your first name to continue.")
            elif lifestyle == "— Select —":
                st.warning("Please select a lifestyle option.")
            elif not priorities:
                st.warning("Please select at least one priority.")
            else:
                st.session_state.user_name = name
                with st.spinner(f"Analyzing your profile, {name}..."):
                    context = "\n".join([f"{k}: {v['traits']}" for k, v in ACURA_MODELS.items()])
                    priority_str = ", ".join(priorities)
                    extra = f" They also said: '{personality}'" if personality.strip() else ""
                    try:
                        res = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=(
                                f"You are an enthusiastic Acura specialist at a premium dealership. "
                                f"A customer named {name} is looking for their perfect Acura. "
                                f"Their lifestyle: {lifestyle}. "
                                f"Their priorities: {priority_str}.{extra} "
                                f"Based on this profile, recommend exactly ONE Acura from this list: {context}. "
                                f"Address {name} by name, be high-energy and bold, explain WHY this car fits their personality, "
                                f"and mention the exact model name clearly."
                            )
                        )
                        st.session_state.recommendation_text = res.text
                        for car in ACURA_MODELS.keys():
                            if car in res.text:
                                st.session_state.selected_car = car
                                break
                        st.session_state.chat_complete = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    else:
        st.markdown(f"### 👋 Welcome, {st.session_state.user_name}!")
        st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)
        st.info(st.session_state.recommendation_text)
        st.markdown("")
        if st.button(f"🚗 ENTER GARAGE: {st.session_state.selected_car.upper()}"):
            st.session_state.app_state = "GARAGE"
            st.rerun()
        if st.button("↩ START OVER"):
            for key in ["chat_complete", "user_name", "recommendation_text", "current_image"]:
                st.session_state[key] = "" if key in ["user_name", "recommendation_text"] else False if key == "chat_complete" else None
            st.rerun()

# --- 5. PHASE 2: THE AI VISUALIZER GARAGE ---
else:
    name_display = f"{st.session_state.user_name.upper()}'S " if st.session_state.user_name else ""
    st.title(f"{name_display}PROJECT: {st.session_state.selected_car.upper()}")
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
