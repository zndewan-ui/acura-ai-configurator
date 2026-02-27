import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import random

# --- 1. ACURA BRAND STYLING (CSS) ---
st.set_page_config(page_title="Acura Dream Finder", layout="wide")

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

    /* Chat bubble styling */
    .chat-user {
        background: #1a1a1a;
        border-left: 3px solid #E4002B;
        padding: 12px 16px;
        border-radius: 0 12px 12px 0;
        margin: 8px 60px 8px 0;
        color: #fff;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .chat-ai {
        background: #111;
        border-left: 3px solid #555;
        padding: 12px 16px;
        border-radius: 0 12px 12px 0;
        margin: 8px 0 8px 60px;
        color: #fff;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .chat-label-ai { color: #E4002B; font-size: 0.72rem; font-weight: bold; margin-bottom: 4px; letter-spacing: 1px; }
    .chat-label-user { color: #666; font-size: 0.72rem; font-weight: bold; margin-bottom: 4px; letter-spacing: 1px; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ACURA CANADA FULL LINEUP ---
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

# --- 3. SESSION STATE ---
defaults = {
    "app_state": "CHAT",
    "selected_car": "Integra Type S",
    "chat_complete": False,
    "current_image": None,
    "user_name": "",
    "messages": [],
    "kai_started": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- 4. KAI SYSTEM PROMPT ---
SYSTEM_PROMPT = f"""You are Kai, a friendly and passionate Acura specialist. Your vibe is warm, casual, enthusiastic, and a little witty — like a car-obsessed friend who happens to know everything about Acura.

Your job: have a fun, natural back-and-forth conversation to figure out which Acura is the perfect match for this person.

Rules:
- On your very first message (when the conversation is empty), introduce yourself as Kai and ask for their name in a warm, casual way. Keep it short.
- Ask ONE question at a time. Never list multiple questions.
- Keep messages short and punchy — like texting. 2-4 sentences max per message.
- React naturally to what they say before your next question (e.g. "Oh nice!", "Okay I love that 👀", "That tells me a lot actually!").
- Naturally uncover: their lifestyle, what they use a car for, whether they want performance/comfort/space/tech/EV, and their general vibe.
- After 4-6 back-and-forths (once you know enough), make your recommendation.
- When recommending: be genuinely excited, be specific, and explain exactly WHY this car fits THEM. Mention the exact model name clearly.
- The model name in your recommendation MUST exactly match one of these: {list(ACURA_MODELS.keys())}
- After your recommendation message, add this token on its own line at the very end: RECOMMENDATION_READY
- Do not ask any more questions after making your recommendation.
- Never break character or mention being an AI. You are just Kai."""


def get_kai_response(messages):
    """Send conversation history to Gemini and get Kai's next reply."""
    formatted = [{"role": m["role"], "parts": [{"text": m["content"]}]} for m in messages]
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=formatted,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
    )
    return response.text


def generate_ai_render(car, color):
    """Generate a car render using Gemini image generation."""
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
            config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                return Image.open(BytesIO(part.inline_data.data))
        st.error("No image was returned. Please try again.")
        return None
    except Exception as e:
        st.error(f"Image generation failed: {e}")
        return None


# ============================================================
# PHASE 1: CHAT WITH KAI
# ============================================================
if st.session_state.app_state == "CHAT":
    st.image("https://pngimg.com/uploads/acura/acura_PNG73.png", width=120)
    st.title("Let's Find Your Dream Acura")
    st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)

    # Kai sends the opening message automatically on first load
    if not st.session_state.kai_started:
        with st.spinner(""):
            try:
                seed = [{"role": "user", "content": "hi"}]
                opening = get_kai_response(seed)
                clean = opening.replace("RECOMMENDATION_READY", "").strip()
                st.session_state.messages.append({"role": "assistant", "content": clean})
                st.session_state.kai_started = True
                st.rerun()
            except Exception as e:
                st.error(f"Could not connect to Kai: {e}")
        st.stop()

    # Render all chat messages
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            st.markdown(
                f'<div class="chat-label-ai">⚡ KAI</div>'
                f'<div class="chat-ai">{msg["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="chat-label-user">YOU</div>'
                f'<div class="chat-user">{msg["content"]}</div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # After recommendation: show Enter Garage + Start Over
    if st.session_state.chat_complete:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🚗 ENTER GARAGE: {st.session_state.selected_car.upper()}"):
                st.session_state.app_state = "GARAGE"
                st.rerun()
        with col2:
            if st.button("↩ START OVER"):
                for k, v in defaults.items():
                    st.session_state[k] = v
                st.rerun()
    else:
        # Live chat input
        user_input = st.chat_input("Reply to Kai...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner("Kai is typing..."):
                try:
                    reply = get_kai_response(st.session_state.messages)
                    is_done = "RECOMMENDATION_READY" in reply
                    clean_reply = reply.replace("RECOMMENDATION_READY", "").strip()
                    st.session_state.messages.append({"role": "assistant", "content": clean_reply})

                    if is_done:
                        # Match the recommended car
                        for car in ACURA_MODELS.keys():
                            if car in clean_reply:
                                st.session_state.selected_car = car
                                break
                        # Try to extract user's name from early messages
                        for msg in st.session_state.messages:
                            if msg["role"] == "user":
                                first_word = msg["content"].strip().split()[0]
                                if len(first_word) > 1 and first_word.isalpha():
                                    st.session_state.user_name = first_word.capitalize()
                                    break
                        st.session_state.chat_complete = True

                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")


# ============================================================
# PHASE 2: THE GARAGE
# ============================================================
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
            with st.spinner("Rendering your build..."):
                st.session_state.current_image = generate_ai_render(
                    st.session_state.selected_car, paint
                )

        if st.button("← BACK TO CHAT"):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with col_vis:
        if st.session_state.current_image:
            st.image(st.session_state.current_image, use_container_width=True)
        else:
            st.info("Click 'GENERATE NEW AI RENDER' to see your custom build.")
