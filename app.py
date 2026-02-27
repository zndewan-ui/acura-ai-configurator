import streamlit as st
from google import genai
from google.genai import types
from lumaai import LumaAI
import random
import time
import requests
import base64
from io import BytesIO
from PIL import Image

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Acura AI Configurator", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }

.stApp {
    background: #000;
    color: #fff;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Showroom background ── */
.showroom-bg {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background:
        radial-gradient(ellipse at 20% 50%, rgba(20,30,60,0.9) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(40,10,10,0.7) 0%, transparent 50%),
        linear-gradient(180deg, #050810 0%, #0a0d1a 50%, #080508 100%);
    z-index: 0;
}

/* Animated floor reflection line */
.showroom-bg::after {
    content: '';
    position: fixed;
    bottom: 0; left: 0;
    width: 100%; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(228,0,43,0.6), transparent);
    animation: scanline 3s ease-in-out infinite;
}
@keyframes scanline {
    0%, 100% { opacity: 0.3; transform: scaleX(0.5); }
    50% { opacity: 1; transform: scaleX(1); }
}

/* ── Top nav bar ── */
.top-nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 56px;
    background: rgba(0,0,0,0.7);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(228,0,43,0.3);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 32px;
    z-index: 100;
}
.nav-logo {
    color: #fff;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 4px;
    text-transform: uppercase;
}
.nav-badge {
    background: rgba(228,0,43,0.15);
    border: 1px solid rgba(228,0,43,0.4);
    color: #E4002B;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 3px;
    padding: 4px 12px;
    border-radius: 2px;
    text-transform: uppercase;
}

/* ── Main layout wrapper ── */
.main-layout {
    display: flex;
    height: 100vh;
    padding-top: 56px;
    position: relative;
    z-index: 1;
}

/* ── Left: car display panel ── */
.car-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
    position: relative;
}
.car-display-img {
    width: 100%;
    max-width: 700px;
    border-radius: 8px;
    filter: drop-shadow(0 20px 60px rgba(228,0,43,0.2));
    animation: float 6s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-12px); }
}
.car-placeholder {
    width: 100%;
    max-width: 700px;
    height: 380px;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(255,255,255,0.02);
    backdrop-filter: blur(10px);
    gap: 16px;
}
.car-name-tag {
    text-align: center;
    margin-top: 20px;
}
.car-name-tag h2 {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 4px !important;
    color: #fff !important;
    margin: 0 !important;
    text-transform: uppercase !important;
}
.car-name-tag span {
    color: #E4002B;
    font-size: 0.7rem;
    letter-spacing: 3px;
    text-transform: uppercase;
}
.stat-row {
    display: flex;
    gap: 32px;
    margin-top: 16px;
    justify-content: center;
}
.stat-item {
    text-align: center;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 10px 20px;
    border-radius: 4px;
    backdrop-filter: blur(10px);
}
.stat-value { font-size: 1.3rem; font-weight: 700; color: #fff; }
.stat-label { font-size: 0.6rem; letter-spacing: 2px; color: #888; text-transform: uppercase; }

/* ── Right: glass chat panel ── */
.chat-panel {
    width: 420px;
    min-width: 420px;
    height: calc(100vh - 56px);
    background: rgba(10, 10, 20, 0.6);
    backdrop-filter: blur(30px);
    border-left: 1px solid rgba(228,0,43,0.2);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
.chat-header {
    padding: 20px 24px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    flex-shrink: 0;
}
.chat-header-title {
    font-size: 0.65rem;
    letter-spacing: 3px;
    color: #E4002B;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.chat-header-sub {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.5);
}
.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    scrollbar-width: thin;
    scrollbar-color: rgba(228,0,43,0.3) transparent;
}
.msg-kai {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
}
.msg-user {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 6px;
}
.msg-label {
    font-size: 0.6rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.3);
    padding: 0 4px;
}
.bubble-kai {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 2px 14px 14px 14px;
    padding: 14px 18px;
    font-size: 26px;
    line-height: 1.6;
    color: #fff;
    max-width: 90%;
    backdrop-filter: blur(10px);
}
.bubble-user {
    background: rgba(228,0,43,0.12);
    border: 1px solid rgba(228,0,43,0.25);
    border-radius: 14px 2px 14px 14px;
    padding: 14px 18px;
    font-size: 26px;
    line-height: 1.6;
    color: #fff;
    max-width: 90%;
}
.kai-dot {
    width: 8px; height: 8px;
    background: #E4002B;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
}

/* ── Streamlit overrides for chat phase ── */
.stChatInput { 
    background: rgba(10,10,20,0.8) !important;
    border-top: 1px solid rgba(255,255,255,0.06) !important;
}
.stChatInput textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 4px !important;
    color: #fff !important;
    font-size: 15px !important;
}

/* ── Garage phase ── */
.stButton>button {
    background: rgba(228,0,43,0.9);
    color: #fff;
    border: none;
    border-radius: 2px;
    font-weight: 600;
    font-size: 0.8rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    width: 100%;
    height: 3.2em;
    transition: all 0.2s;
}
.stButton>button:hover {
    background: #fff;
    color: #E4002B;
}
.garage-glass {
    background: rgba(10,10,20,0.7);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(228,0,43,0.2);
    border-radius: 8px;
    padding: 24px;
}

video { border-radius: 8px; width: 100%; }
</style>

<!-- Showroom background -->
<div class="showroom-bg"></div>

<!-- Top nav -->
<div class="top-nav">
    <span class="nav-logo">⬡ ACURA</span>
    <span class="nav-badge">AI Configurator</span>
    <span style="color:rgba(255,255,255,0.3);font-size:0.7rem;letter-spacing:2px;">PRECISION CRAFTED PERFORMANCE</span>
</div>
""", unsafe_allow_html=True)

# --- 2. ACURA CANADA FULL LINEUP ---
ACURA_MODELS = {
    "Integra": {
        "hp": 200, "torque": 192,
        "traits": "The Daily Driver. A sporty hatchback-sedan with a VTEC Turbo engine and available 6-speed manual.",
        "colors": ["Urban Gray Pearl", "Apex Blue Pearl", "Platinum White Pearl", "Sonic Gray Pearl", "Performance Red Pearl", "Majestic Black Pearl"]
    },
    "Integra Type S": {
        "hp": 320, "torque": 310,
        "traits": "The Purist. The most powerful Integra ever built. 6-speed manual, Brembo brakes, 320HP.",
        "colors": ["Apex Blue Pearl", "Tiger Eye Pearl", "Championship White", "Solar Silver Metallic", "Gotham Gray Pearl"]
    },
    "TLX": {
        "hp": 272, "torque": 280,
        "traits": "The Refined Performer. Luxury sports sedan with standard SH-AWD and turbocharged engine.",
        "colors": ["Liquid Carbon Metallic", "Platinum White Pearl", "Majestic Black Pearl", "Apex Blue Pearl", "Performance Red Pearl"]
    },
    "TLX Type S": {
        "hp": 355, "torque": 354,
        "traits": "The Executive Athlete. Racetrack-inspired 3.0L Turbo V6, NSX-derived brakes, Brembo calipers.",
        "colors": ["Urban Gray Pearl", "Apex Blue Pearl", "Majestic Black Pearl", "Liquid Carbon Metallic", "Performance Red Pearl"]
    },
    "ADX": {
        "hp": 190, "torque": 179,
        "traits": "The Urban Adventurer. Nimble, tech-loaded compact SUV with Bang & Olufsen sound.",
        "colors": ["Urban Gray Pearl", "Double Apex Blue Pearl II", "Platinum White Pearl", "Sonic Gray Pearl", "Majestic Black Pearl"]
    },
    "RDX A-Spec": {
        "hp": 272, "torque": 280,
        "traits": "The Balanced Versatile. Sport crossover with SH-AWD torque vectoring and bold A-Spec styling.",
        "colors": ["Berlina Black", "Apex Blue Pearl", "Performance Red Pearl", "Liquid Carbon Metallic", "Platinum White Pearl"]
    },
    "MDX": {
        "hp": 290, "torque": 267,
        "traits": "The Family Commander. 3-row V6 SUV with racecar DNA and available SH-AWD.",
        "colors": ["Platinum White Pearl", "Urban Gray Pearl", "Majestic Black Pearl", "Performance Red Pearl", "Apex Blue Pearl"]
    },
    "MDX Type S": {
        "hp": 355, "torque": 354,
        "traits": "The Power Leader. 7-seat SUV with 3.0L Turbo V6, adaptive air suspension, quad exhaust.",
        "colors": ["Performance Red Pearl", "Urban Gray Pearl", "Majestic Black Pearl", "Apex Blue Pearl", "Platinum White Pearl"]
    },
    "ZDX Type S": {
        "hp": 500, "torque": 544,
        "traits": "The Electric Vanguard. 500HP, instant torque, zero emissions. The most powerful Acura ever.",
        "colors": ["Double Apex Blue Pearl", "Urban Gray Pearl", "Majestic Black Pearl", "Performance Red Pearl"]
    },
}

# --- 3. SESSION STATE ---
defaults = {
    "app_state": "CHAT",
    "selected_car": "Integra Type S",
    "chat_complete": False,
    "video_url": None,
    "user_name": "",
    "messages": [],
    "kai_started": False,
    "preview_image": None,       # base64 string for live car preview during chat
    "preview_car": None,         # which car the preview is for
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- 4. API CLIENTS ---
gemini_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
luma_client = LumaAI(auth_token=st.secrets["LUMA_API_KEY"])

# --- 5. KAI SYSTEM PROMPT ---
SYSTEM_PROMPT = f"""You are Kai, a friendly and passionate Acura specialist. Your vibe is warm, casual, enthusiastic, and a little witty — like a car-obsessed friend who knows everything about Acura.

Your job: have a fun, natural back-and-forth conversation to figure out which Acura is perfect for this person.

Rules:
- First message: introduce yourself as Kai, ask for their name. Keep it short and warm.
- Ask ONE question at a time. Never list multiple questions.
- Keep messages short and punchy — like texting. 2-4 sentences max.
- React naturally before your next question (e.g. "Oh nice!", "Okay I love that 👀", "That tells me a lot!").
- Uncover: their lifestyle, car usage, performance/comfort/space/tech/EV preference, and vibe.
- After 4-6 exchanges, make your recommendation. Be excited, specific, explain WHY it fits THEM.
- Model name MUST exactly match one of: {list(ACURA_MODELS.keys())}
- End your recommendation with this token on its own line: RECOMMENDATION_READY
- No more questions after recommending.
- Never break character. You are Kai."""


def get_kai_response(messages):
    formatted = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]} for m in messages]
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=formatted,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
    )
    return response.text


def generate_preview_image(car):
    """Generate a quick preview image of the car for the showroom display."""
    prompt = (
        f"Photorealistic 3D render of a 2026 Acura {car}, front three-quarter view, "
        f"on a dark reflective showroom floor, dramatic moody blue lighting from above, "
        f"pure dark background, cinematic automotive photography, ultra sharp, 8k."
    )
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            return base64.b64encode(part.inline_data.data).decode()
    return None


def generate_still_image(car, color):
    """Generate a photorealistic still of the exact Acura using Gemini."""
    prompt = (
        f"Professional photorealistic automotive studio photograph of a 2026 Acura {car} "
        f"in {color} paint. Front three-quarter view. Pure black studio background, "
        f"dramatic cinematic lighting, ultra-realistic, sharp detail, 8k quality. "
        f"No text, no people, no environment — just the car."
    )
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            return part.inline_data.data, part.inline_data.mime_type
    return None, None


def upload_image_to_imgbb(image_bytes):
    """Upload image to ImgBB and return a public URL."""
    b64 = base64.b64encode(image_bytes).decode()
    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": st.secrets["IMGBB_API_KEY"], "image": b64, "expiration": 600},
        timeout=30
    )
    response.raise_for_status()
    return response.json()["data"]["url"]


def generate_luma_video(car, color):
    """Two-step: Gemini still → ImgBB upload → Luma animation."""
    status_text = st.empty()
    progress_bar = st.progress(0)
    try:
        status_text.markdown("🖼️ **Step 1/2 — Generating reference image...**")
        progress_bar.progress(0.1)
        image_bytes, mime_type = generate_still_image(car, color)
        if not image_bytes:
            st.error("Could not generate reference image. Please try again.")
            status_text.empty(); progress_bar.empty()
            return None

        progress_bar.progress(0.25)
        status_text.markdown("📤 **Uploading reference image...**")
        image_url = upload_image_to_imgbb(image_bytes)

        progress_bar.progress(0.35)
        status_text.markdown("🎬 **Step 2/2 — Submitting to Luma AI...**")
        video_prompt = (
            f"Cinematic 360-degree turntable reveal of this exact 2026 Acura {car} in {color} paint. "
            f"The car slowly rotates on a black reflective studio floor. "
            f"Dramatic rim lighting, luxury automotive advertisement quality, smooth camera motion."
        )
        generation = luma_client.generations.create(
            prompt=video_prompt,
            model="ray-2",
            resolution="1080p",
            duration="5s",
            keyframes={"frame0": {"type": "image", "url": image_url}}
        )

        gen_id = generation.id
        max_wait = 300
        poll_interval = 5
        elapsed = 0
        status_msgs = ["🎨 Composing scene...", "💡 Placing studio lights...", "🚗 Animating your Acura...", "✨ Adding cinematic motion...", "🎬 Finalising..."]

        while elapsed < max_wait:
            time.sleep(poll_interval)
            elapsed += poll_interval
            generation = luma_client.generations.get(id=gen_id)
            state = generation.state
            progress = min(0.35 + (elapsed / 90) * 0.6, 0.95)
            msg_index = min(int((elapsed / 90) * len(status_msgs)), len(status_msgs) - 1)
            status_text.markdown(f"**{status_msgs[msg_index]}** *(~{max(0, 90 - elapsed):.0f}s remaining)*")
            progress_bar.progress(progress)
            if state == "completed":
                progress_bar.progress(1.0)
                status_text.empty(); progress_bar.empty()
                return generation.assets.video
            elif state == "failed":
                status_text.empty(); progress_bar.empty()
                st.error(f"Luma failed: {getattr(generation, 'failure_reason', 'Unknown')}")
                return None

        status_text.empty(); progress_bar.empty()
        st.error("Timed out. Please try again.")
        return None
    except Exception as e:
        status_text.empty(); progress_bar.empty()
        st.error(f"Luma AI error: {e}")
        return None


# ============================================================
# PHASE 1: IMMERSIVE CHAT WITH KAI
# ============================================================
if st.session_state.app_state == "CHAT":

    # Kai sends opening message on first load
    if not st.session_state.kai_started:
        with st.spinner(""):
            try:
                opening = get_kai_response([{"role": "user", "content": "hi"}])
                clean = opening.replace("RECOMMENDATION_READY", "").strip()
                st.session_state.messages.append({"role": "assistant", "content": clean})
                st.session_state.kai_started = True
                st.rerun()
            except Exception as e:
                st.error(f"Could not connect to Kai: {e}")
        st.stop()

    # ── Build left panel (car preview) HTML ──
    car = st.session_state.selected_car
    stats = ACURA_MODELS[car]

    if st.session_state.preview_image and st.session_state.preview_car == car:
        car_html = f'<img class="car-display-img" src="data:image/png;base64,{st.session_state.preview_image}" />'
    else:
        car_html = f'''<div class="car-placeholder">
            <div style="font-size:4rem;opacity:0.2;">⬡</div>
            <div style="color:rgba(255,255,255,0.2);font-size:0.7rem;letter-spacing:3px;">LOADING PREVIEW...</div>
        </div>'''

    stat_html = f'''<div class="stat-row">
        <div class="stat-item"><div class="stat-value">{stats["hp"]}</div><div class="stat-label">HP</div></div>
        <div class="stat-item"><div class="stat-value">{stats["torque"]}</div><div class="stat-label">LB-FT</div></div>
    </div>'''

    # ── Build chat messages HTML ──
    msgs_html = ""
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            msgs_html += f'''<div class="msg-kai">
                <div class="msg-label"><span class="kai-dot"></span>KAI</div>
                <div class="bubble-kai">{msg["content"]}</div>
            </div>'''
        else:
            msgs_html += f'''<div class="msg-user">
                <div class="msg-label">YOU</div>
                <div class="bubble-user">{msg["content"]}</div>
            </div>'''

    # ── Render full immersive layout ──
    st.markdown(f"""
    <div class="main-layout">
        <!-- LEFT: Car display -->
        <div class="car-panel">
            {car_html}
            <div class="car-name-tag">
                <h2>Acura {car}</h2>
                <span>2026 LINEUP · PRECISION CRAFTED PERFORMANCE</span>
            </div>
            {stat_html}
        </div>

        <!-- RIGHT: Chat panel -->
        <div class="chat-panel">
            <div class="chat-header">
                <div class="chat-header-title">⚡ KAI — AI SPECIALIST</div>
                <div class="chat-header-sub">Let's find your perfect Acura</div>
            </div>
            <div class="chat-messages" id="chat-scroll">
                {msgs_html}
            </div>
        </div>
    </div>

    <script>
        // Auto-scroll chat to bottom
        const el = document.getElementById('chat-scroll');
        if (el) el.scrollTop = el.scrollHeight;
    </script>
    """, unsafe_allow_html=True)

    # ── Chat input & action buttons (rendered by Streamlit below the HTML) ──
    if st.session_state.chat_complete:
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
                        for c in ACURA_MODELS.keys():
                            if c in clean_reply:
                                st.session_state.selected_car = c
                                break
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

    # Generate preview image in background if not cached
    if st.session_state.preview_car != st.session_state.selected_car:
        try:
            b64 = generate_preview_image(st.session_state.selected_car)
            if b64:
                st.session_state.preview_image = b64
                st.session_state.preview_car = st.session_state.selected_car
                st.rerun()
        except Exception:
            pass


# ============================================================
# PHASE 2: THE GARAGE
# ============================================================
else:
    name_display = f"{st.session_state.user_name.upper()}'S " if st.session_state.user_name else ""

    st.markdown(f"""
    <div style="padding: 80px 40px 20px 40px; position: relative; z-index: 1;">
        <div style="font-size:0.65rem;letter-spacing:4px;color:#E4002B;text-transform:uppercase;margin-bottom:6px;">
            Acura Garage
        </div>
        <div style="font-size:2rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;">
            {name_display}Project: {st.session_state.selected_car}
        </div>
        <div style="height:3px;background:linear-gradient(90deg,#E4002B,transparent);margin:12px 0 32px;width:300px;"></div>
    </div>
    """, unsafe_allow_html=True)

    col_vis, col_ui = st.columns([2, 1])

    with col_ui:
        st.markdown('<div class="garage-glass">', unsafe_allow_html=True)

        colors = ACURA_MODELS[st.session_state.selected_car]["colors"]
        paint = st.pills("PAINT", colors, default=colors[0])

        st.markdown("<br>", unsafe_allow_html=True)
        stats = ACURA_MODELS[st.session_state.selected_car]
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("POWER", f"{stats['hp']} HP")
        with col_b:
            st.metric("TORQUE", f"{stats['torque']} LB-FT")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🎬 GENERATE CINEMATIC REVEAL"):
            st.session_state.video_url = None
            with col_vis:
                video_url = generate_luma_video(st.session_state.selected_car, paint)
                if video_url:
                    st.session_state.video_url = video_url
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("← BACK TO CHAT"):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with col_vis:
        if st.session_state.video_url:
            try:
                video_bytes = requests.get(st.session_state.video_url, timeout=30).content
                st.video(video_bytes, autoplay=True, loop=True, muted=True)
            except Exception:
                st.video(st.session_state.video_url)
            st.caption(f"2026 Acura {st.session_state.selected_car} · {paint} · Cinematic AI Reveal")
        else:
            st.markdown("""
            <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
                        backdrop-filter:blur(20px);border-radius:8px;height:460px;
                        display:flex;align-items:center;justify-content:center;
                        flex-direction:column;gap:16px;">
                <div style="font-size:3rem;opacity:0.3;">🎬</div>
                <div style="color:rgba(255,255,255,0.25);font-size:0.75rem;letter-spacing:3px;text-align:center;">
                    SELECT PAINT · CLICK GENERATE<br>
                    <span style="font-size:0.65rem;color:rgba(255,255,255,0.15);">Powered by Luma AI · ~90 seconds</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
