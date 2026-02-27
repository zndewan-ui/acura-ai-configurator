import streamlit as st
from google import genai
from google.genai import types
from lumaai import LumaAI
import random
import time
import requests
import base64

# --- PAGE CONFIG ---
st.set_page_config(page_title="Acura AI Configurator", layout="wide", initial_sidebar_state="collapsed")

# --- GLOBAL CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 2rem 2rem 2rem !important; max-width: 100% !important; }

/* Deep Dealership Background */
.stApp {
    background: linear-gradient(180deg, #1a1d23 0%, #050608 100%);
    min-height: 100vh;
    color: #fff !important;
}

/* Top nav */
.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0 20px 0;
    border-bottom: 1px solid rgba(0,114,188,0.25);
    margin-bottom: 24px;
}
.nav-logo {
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 5px;
    color: #fff;
    text-transform: uppercase;
}
.nav-badge {
    background: rgba(0,114,188,0.15);
    border: 1px solid rgba(0,114,188,0.5);
    color: #0072bc;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 3px;
    padding: 5px 14px;
    border-radius: 2px;
    text-transform: uppercase;
}
.nav-right {
    font-size: 0.65rem;
    letter-spacing: 3px;
    color: rgba(255,255,255,0.25);
    text-transform: uppercase;
}

/* Car image floating animation */
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-10px); }
}
.car-float { animation: float 6s ease-in-out infinite; }

/* Car panel label */
.car-label {
    text-align: center;
    padding: 16px 0 8px;
}
.car-label-name {
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #fff;
}
.car-label-sub {
    font-size: 0.6rem;
    letter-spacing: 3px;
    color: rgba(255,255,255,0.3);
    text-transform: uppercase;
    margin-top: 4px;
}

/* Stat pills */
.stat-strip {
    display: flex;
    gap: 12px;
    justify-content: center;
    margin-top: 12px;
}
.stat-pill {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 4px;
    padding: 8px 18px;
    text-align: center;
    backdrop-filter: blur(10px);
}
.stat-val { font-size: 1.1rem; font-weight: 700; color: #fff; }
.stat-lbl { font-size: 0.55rem; letter-spacing: 2px; color: #888; text-transform: uppercase; }

/* Glass chat panel */
.chat-glass-header {
    background: rgba(8,8,18,0.75);
    border: 1px solid rgba(0,114,188,0.25);
    border-radius: 8px 8px 0 0;
    padding: 14px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.chat-glass-body {
    background: rgba(8,8,18,0.6);
    border: 1px solid rgba(0,114,188,0.15);
    border-top: none;
    border-radius: 0 0 8px 8px;
    padding: 16px 20px;
    backdrop-filter: blur(24px);
    min-height: 400px;
    max-height: 55vh;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: rgba(228,0,43,0.3) transparent;
}

/* Chat bubbles */
.msg-block-kai  { margin: 10px 0; display: flex; flex-direction: column; align-items: flex-start; gap: 5px; }
.msg-block-user { margin: 10px 0; display: flex; flex-direction: column; align-items: flex-end;   gap: 5px; }
.msg-lbl { font-size: 0.58rem; letter-spacing: 2px; color: rgba(255,255,255,0.3); text-transform: uppercase; padding: 0 3px; }

@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.3;} }
.kai-dot {
    display: inline-block; width: 7px; height: 7px;
    background: #0072bc; border-radius: 50%;
    margin-right: 5px;
    animation: pulse 2s ease-in-out infinite;
}
.bubble-kai {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 3px 14px 14px 14px;
    padding: 13px 17px;
    font-size: 16px;
    line-height: 1.6;
    color: #fff;
    max-width: 92%;
    backdrop-filter: blur(10px);
}
.bubble-user {
    background: rgba(0,114,188,0.12);
    border: 1px solid rgba(0,114,188,0.3);
    border-radius: 14px 3px 14px 14px;
    padding: 13px 17px;
    font-size: 16px;
    line-height: 1.6;
    color: #fff;
    max-width: 92%;
}

/* Buttons — Acura Blue */
.stButton > button {
    background: #0072bc !important;
    color: #fff !important;
    border: none !important;
    border-radius: 50px !important;
    font-weight: 700 !important;
    font-size: 0.75rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    width: 100% !important;
    height: 3em !important;
    padding: 10px 40px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #005a96 !important;
    color: #fff !important;
}

/* Chat input — glassmorphic pill */
.stChatInput > div {
    background: rgba(0,0,0,0.4) !important;
    backdrop-filter: blur(25px) !important;
    -webkit-backdrop-filter: blur(25px) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 30px !important;
    box-shadow: 0 20px 50px rgba(0,0,0,0.5) !important;
    padding: 6px 16px !important;
}
.stChatInput textarea {
    color: #fff !important;
    font-size: 15px !important;
    background: transparent !important;
}

/* Garage glass panel */
.garage-glass {
    background: rgba(8,8,18,0.7);
    border: 1px solid rgba(0,114,188,0.25);
    border-radius: 8px;
    padding: 24px;
    backdrop-filter: blur(20px);
}

video { border-radius: 8px; width: 100%; }

/* Metric labels */
[data-testid="stMetricLabel"] { color: rgba(255,255,255,0.4) !important; font-size: 0.65rem !important; letter-spacing: 2px !important; }
[data-testid="stMetricValue"] { color: #fff !important; font-size: 1.4rem !important; }
</style>
""", unsafe_allow_html=True)

# --- ACURA LINEUP ---
ACURA_MODELS = {
    "Integra": {
        "hp": 200, "torque": 192,
        "traits": "The Daily Driver. Sporty hatchback-sedan with VTEC Turbo and available 6-speed manual.",
        "colors": ["Urban Gray Pearl", "Apex Blue Pearl", "Platinum White Pearl", "Sonic Gray Pearl", "Performance Red Pearl", "Majestic Black Pearl"]
    },
    "Integra Type S": {
        "hp": 320, "torque": 310,
        "traits": "The Purist. Most powerful Integra ever. 6-speed manual, Brembo brakes, 320HP.",
        "colors": ["Apex Blue Pearl", "Tiger Eye Pearl", "Championship White", "Solar Silver Metallic", "Gotham Gray Pearl"]
    },
    "TLX": {
        "hp": 272, "torque": 280,
        "traits": "The Refined Performer. Luxury sports sedan with standard SH-AWD and turbo engine.",
        "colors": ["Liquid Carbon Metallic", "Platinum White Pearl", "Majestic Black Pearl", "Apex Blue Pearl", "Performance Red Pearl"]
    },
    "TLX Type S": {
        "hp": 355, "torque": 354,
        "traits": "The Executive Athlete. 3.0L Turbo V6, NSX-derived brakes, Brembo calipers.",
        "colors": ["Urban Gray Pearl", "Apex Blue Pearl", "Majestic Black Pearl", "Liquid Carbon Metallic", "Performance Red Pearl"]
    },
    "ADX": {
        "hp": 190, "torque": 179,
        "traits": "The Urban Adventurer. Compact SUV with Bang & Olufsen sound and city-focused tech.",
        "colors": ["Urban Gray Pearl", "Double Apex Blue Pearl II", "Platinum White Pearl", "Sonic Gray Pearl", "Majestic Black Pearl"]
    },
    "RDX A-Spec": {
        "hp": 272, "torque": 280,
        "traits": "The Balanced Versatile. Sport crossover with SH-AWD torque vectoring.",
        "colors": ["Berlina Black", "Apex Blue Pearl", "Performance Red Pearl", "Liquid Carbon Metallic", "Platinum White Pearl"]
    },
    "MDX": {
        "hp": 290, "torque": 267,
        "traits": "The Family Commander. 3-row V6 SUV with racecar DNA and available SH-AWD.",
        "colors": ["Platinum White Pearl", "Urban Gray Pearl", "Majestic Black Pearl", "Performance Red Pearl", "Apex Blue Pearl"]
    },
    "MDX Type S": {
        "hp": 355, "torque": 354,
        "traits": "The Power Leader. 7-seat SUV, 3.0L Turbo V6, adaptive air suspension.",
        "colors": ["Performance Red Pearl", "Urban Gray Pearl", "Majestic Black Pearl", "Apex Blue Pearl", "Platinum White Pearl"]
    },
    "ZDX Type S": {
        "hp": 500, "torque": 544,
        "traits": "The Electric Vanguard. 500HP, instant torque, zero emissions.",
        "colors": ["Double Apex Blue Pearl", "Urban Gray Pearl", "Majestic Black Pearl", "Performance Red Pearl"]
    },
}

# --- SESSION STATE ---
defaults = {
    "app_state": "CHAT",
    "selected_car": "Integra Type S",
    "chat_complete": False,
    "video_url": None,
    "user_name": "",
    "messages": [],
    "kai_started": False,
    "preview_image_b64": None,
    "preview_car": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- API CLIENTS ---
gemini_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
luma_client = LumaAI(auth_token=st.secrets["LUMA_API_KEY"])

# --- KAI SYSTEM PROMPT ---
SYSTEM_PROMPT = f"""You are Kai, a friendly passionate Acura specialist. Warm, casual, enthusiastic, witty — like a car-obsessed friend.

Your job: natural back-and-forth conversation to find the perfect Acura for this person.

Rules:
- First message: introduce yourself as Kai, ask for their name. Keep it short and warm.
- Ask ONE question at a time. Never list multiple questions.
- Short punchy messages — like texting. 2-4 sentences max.
- React naturally before next question ("Oh nice!", "Okay I love that 👀", "That tells me a lot!").
- Uncover: lifestyle, car usage, performance/comfort/space/tech/EV preference, vibe.
- After 4-6 exchanges make your recommendation. Excited, specific, explain WHY it fits THEM.
- Model name MUST exactly match one of: {list(ACURA_MODELS.keys())}
- End recommendation with this token on its own line: RECOMMENDATION_READY
- No more questions after recommending. Never break character."""


def get_kai_response(messages):
    formatted = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]} for m in messages]
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=formatted,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
    )
    return response.text


def generate_preview_image(car):
    prompt = (
        f"Photorealistic 3D render of a 2026 Acura {car}, front three-quarter view, "
        f"dark luxury showroom floor with subtle reflection, dramatic blue-white rim lighting, "
        f"very dark near-black background with faint depth, cinematic automotive photography. "
        f"No text, no people, no environment details."
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
    prompt = (
        f"Professional photorealistic automotive studio photograph of a 2026 Acura {car} "
        f"in {color} paint. Front three-quarter view. Pure black studio background, "
        f"dramatic cinematic lighting, ultra-realistic, 8k. No text, no people."
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
    b64 = base64.b64encode(image_bytes).decode()
    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": st.secrets["IMGBB_API_KEY"], "image": b64, "expiration": 600},
        timeout=30
    )
    response.raise_for_status()
    return response.json()["data"]["url"]


def generate_luma_video(car, color):
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

        status_text.markdown("📤 **Uploading reference image...**")
        progress_bar.progress(0.25)
        image_url = upload_image_to_imgbb(image_bytes)

        status_text.markdown("🎬 **Step 2/2 — Submitting to Luma AI...**")
        progress_bar.progress(0.35)
        generation = luma_client.generations.create(
            prompt=(
                f"Cinematic 360-degree turntable reveal of this exact 2026 Acura {car} in {color} paint. "
                f"Slowly rotates on a black reflective studio floor. Dramatic rim lighting, luxury automotive ad quality."
            ),
            model="ray-2", resolution="1080p", duration="5s",
            keyframes={"frame0": {"type": "image", "url": image_url}}
        )

        gen_id = generation.id
        elapsed = 0
        status_msgs = ["🎨 Composing scene...", "💡 Studio lights...", "🚗 Animating your Acura...", "✨ Cinematic motion...", "🎬 Finalising..."]
        while elapsed < 300:
            time.sleep(5); elapsed += 5
            generation = luma_client.generations.get(id=gen_id)
            progress = min(0.35 + (elapsed / 90) * 0.6, 0.95)
            idx = min(int((elapsed / 90) * len(status_msgs)), len(status_msgs) - 1)
            status_text.markdown(f"**{status_msgs[idx]}** *(~{max(0, 90 - elapsed):.0f}s remaining)*")
            progress_bar.progress(progress)
            if generation.state == "completed":
                progress_bar.progress(1.0); status_text.empty(); progress_bar.empty()
                return generation.assets.video
            elif generation.state == "failed":
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


# ══════════════════════════════════════════════
# TOP NAV (always visible)
# ══════════════════════════════════════════════
st.markdown("""
<div class="top-nav">
    <span class="nav-logo">⬡ &nbsp;ACURA</span>
    <span class="nav-badge">AI Configurator</span>
    <span class="nav-right">Precision Crafted Performance</span>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PHASE 1: CHAT
# ══════════════════════════════════════════════
if st.session_state.app_state == "CHAT":

    # Boot Kai on first load
    if not st.session_state.kai_started:
        with st.spinner(""):
            try:
                opening = get_kai_response([{"role": "user", "content": "hi"}])
                st.session_state.messages.append({"role": "assistant", "content": opening.replace("RECOMMENDATION_READY", "").strip()})
                st.session_state.kai_started = True
                st.rerun()
            except Exception as e:
                st.error(f"Could not connect to Kai: {e}")
        st.stop()

    # Two-column layout
    col_car, col_chat = st.columns([3, 2], gap="large")

    # ── LEFT: Car display ──
    with col_car:
        car = st.session_state.selected_car
        stats = ACURA_MODELS[car]

        if st.session_state.preview_image_b64 and st.session_state.preview_car == car:
            st.markdown(
                f'<div class="car-float"><img src="data:image/png;base64,{st.session_state.preview_image_b64}" '
                f'style="width:100%;border-radius:8px;filter:drop-shadow(0 20px 60px rgba(228,0,43,0.25));"/></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown("""
            <div style="width:100%;height:360px;border:1px solid rgba(255,255,255,0.05);
                border-radius:8px;display:flex;align-items:center;justify-content:center;
                background:rgba(255,255,255,0.02);flex-direction:column;gap:12px;">
                <div style="font-size:3rem;opacity:0.15;">⬡</div>
                <div style="color:rgba(255,255,255,0.15);font-size:0.65rem;letter-spacing:3px;">GENERATING PREVIEW...</div>
            </div>""", unsafe_allow_html=True)

        # Car name + stats
        st.markdown(f"""
        <div class="car-label">
            <div class="car-label-name">Acura {car}</div>
            <div class="car-label-sub">2026 · Precision Crafted Performance</div>
        </div>
        <div class="stat-strip">
            <div class="stat-pill"><div class="stat-val">{stats['hp']}</div><div class="stat-lbl">Horsepower</div></div>
            <div class="stat-pill"><div class="stat-val">{stats['torque']}</div><div class="stat-lbl">LB-FT Torque</div></div>
        </div>
        """, unsafe_allow_html=True)

    # ── RIGHT: Chat panel ──
    with col_chat:
        # Glass header
        st.markdown("""
        <div class="chat-glass-header">
            <div style="font-size:0.6rem;letter-spacing:3px;color:#E4002B;text-transform:uppercase;margin-bottom:3px;">
                <span class="kai-dot"></span>KAI — AI SPECIALIST
            </div>
            <div style="font-size:0.8rem;color:rgba(255,255,255,0.4);">Let's find your perfect Acura</div>
        </div>
        """, unsafe_allow_html=True)

        # Build messages HTML
        msgs_html = ""
        for msg in st.session_state.messages:
            if msg["role"] == "assistant":
                msgs_html += f"""
                <div class="msg-block-kai">
                    <div class="msg-lbl"><span class="kai-dot"></span>KAI</div>
                    <div class="bubble-kai">{msg['content']}</div>
                </div>"""
            else:
                msgs_html += f"""
                <div class="msg-block-user">
                    <div class="msg-lbl">YOU</div>
                    <div class="bubble-user">{msg['content']}</div>
                </div>"""

        st.markdown(f"""
        <div class="chat-glass-body" id="chat-end">
            {msgs_html}
        </div>
        <script>
            const el = document.getElementById('chat-end');
            if(el) el.scrollTop = el.scrollHeight;
        </script>
        """, unsafe_allow_html=True)

        # Input / action buttons
        if st.session_state.chat_complete:
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"🚗 ENTER GARAGE"):
                    st.session_state.app_state = "GARAGE"
                    st.rerun()
            with c2:
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
                        clean = reply.replace("RECOMMENDATION_READY", "").strip()
                        st.session_state.messages.append({"role": "assistant", "content": clean})
                        if is_done:
                            for c in ACURA_MODELS:
                                if c in clean:
                                    st.session_state.selected_car = c
                                    break
                            for msg in st.session_state.messages:
                                if msg["role"] == "user":
                                    w = msg["content"].strip().split()[0]
                                    if len(w) > 1 and w.isalpha():
                                        st.session_state.user_name = w.capitalize()
                                        break
                            st.session_state.chat_complete = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # Generate preview image in background if not cached for current car
    if st.session_state.preview_car != st.session_state.selected_car:
        try:
            b64 = generate_preview_image(st.session_state.selected_car)
            if b64:
                st.session_state.preview_image_b64 = b64
                st.session_state.preview_car = st.session_state.selected_car
                st.rerun()
        except Exception:
            pass


# ══════════════════════════════════════════════
# PHASE 2: GARAGE
# ══════════════════════════════════════════════
else:
    name_display = f"{st.session_state.user_name.upper()}'S " if st.session_state.user_name else ""
    st.markdown(f"""
    <div style="padding: 8px 0 24px 0;">
        <div style="font-size:0.6rem;letter-spacing:4px;color:#E4002B;text-transform:uppercase;margin-bottom:6px;">Acura Garage</div>
        <div style="font-size:1.8rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;">{name_display}Project: {st.session_state.selected_car}</div>
        <div style="height:2px;background:linear-gradient(90deg,#E4002B,transparent);margin:10px 0 0;width:280px;"></div>
    </div>
    """, unsafe_allow_html=True)

    col_vis, col_ui = st.columns([3, 1], gap="large")

    with col_ui:
        st.markdown('<div class="garage-glass">', unsafe_allow_html=True)
        colors = ACURA_MODELS[st.session_state.selected_car]["colors"]
        paint = st.pills("PAINT", colors, default=colors[0])
        st.markdown("<br>", unsafe_allow_html=True)
        stats = ACURA_MODELS[st.session_state.selected_car]
        ca, cb = st.columns(2)
        with ca: st.metric("HP", stats['hp'])
        with cb: st.metric("TQ", f"{stats['torque']}")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🎬 GENERATE CINEMATIC REVEAL"):
            st.session_state.video_url = None
            with col_vis:
                url = generate_luma_video(st.session_state.selected_car, paint)
                if url:
                    st.session_state.video_url = url
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
                        border-radius:8px;height:460px;display:flex;align-items:center;
                        justify-content:center;flex-direction:column;gap:14px;">
                <div style="font-size:3rem;opacity:0.2;">🎬</div>
                <div style="color:rgba(255,255,255,0.2);font-size:0.7rem;letter-spacing:3px;text-align:center;">
                    SELECT PAINT · CLICK GENERATE<br>
                    <span style="font-size:0.6rem;opacity:0.6;">Powered by Luma AI · ~90s</span>
                </div>
            </div>""", unsafe_allow_html=True)
