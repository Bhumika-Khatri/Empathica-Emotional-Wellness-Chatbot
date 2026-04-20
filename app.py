import streamlit as st
import anthropic
import json
import re

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Empathica – Emotional Wellness",
    page_icon="💜",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Root & body ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0D0F14 !important;
    color: #F0EEF8 !important;
}
.stApp { background-color: #0D0F14 !important; }

/* ── Hide streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 760px !important; }

/* ── Header ── */
.emp-header {
    display: flex; align-items: center; gap: 14px;
    padding: 0 0 24px 0; border-bottom: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 28px;
}
.emp-orb {
    width: 48px; height: 48px; border-radius: 50%;
    background: linear-gradient(135deg, #7C3AED, #A78BFA);
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; box-shadow: 0 0 24px rgba(167,139,250,0.3);
    flex-shrink: 0;
}
.emp-title { font-family: 'DM Serif Display', serif; font-size: 30px; color: #F0EEF8; line-height:1; }
.emp-title span { color: #A78BFA; }
.emp-sub { font-size: 13px; color: #9896A8; margin-top: 4px; }
.emp-badge {
    margin-left: auto; font-size: 11px; font-weight: 500;
    padding: 4px 12px; border-radius: 20px;
    background: rgba(52,211,153,0.12); color: #34D399;
    border: 1px solid rgba(52,211,153,0.25);
}

/* ── Chat message – User ── */
.user-msg-wrap { display: flex; justify-content: flex-end; margin-bottom: 16px; }
.user-bubble {
    background: linear-gradient(135deg, #7C3AED, #A78BFA);
    color: #fff; padding: 12px 18px; border-radius: 18px 18px 4px 18px;
    max-width: 78%; font-size: 14px; line-height: 1.7;
    box-shadow: 0 2px 12px rgba(124,58,237,0.25);
}

/* ── Chat message – Bot ── */
.bot-msg-wrap { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 20px; }
.bot-avatar {
    width: 34px; height: 34px; border-radius: 50%;
    background: linear-gradient(135deg, #7C3AED, #A78BFA);
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0;
    box-shadow: 0 0 12px rgba(167,139,250,0.3);
}

/* ── Analysis card ── */
.analysis-card {
    background: #151820; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px; overflow: hidden; max-width: 92%;
}
.card-header {
    padding: 10px 16px; background: #1C2030;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    font-size: 10px; font-weight: 500; color: #5C5A6B;
    letter-spacing: 0.1em; text-transform: uppercase;
}
.tags-row { display: flex; gap: 8px; padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.06); flex-wrap: wrap; }
.tag-emotion {
    font-size: 11px; font-weight: 500; padding: 4px 12px; border-radius: 20px;
    background: rgba(167,139,250,0.15); color: #A78BFA;
    border: 1px solid rgba(167,139,250,0.3);
}
.tag-topic {
    font-size: 11px; font-weight: 500; padding: 4px 12px; border-radius: 20px;
    background: rgba(34,211,238,0.1); color: #22D3EE;
    border: 1px solid rgba(34,211,238,0.25);
}
.therapist-row {
    display: flex; align-items: center; gap: 12px;
    padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.06);
}
.t-avatar {
    width: 40px; height: 40px; border-radius: 50%;
    background: linear-gradient(135deg, #553C9A, #A78BFA);
    display: flex; align-items: center; justify-content: center;
    font-family: 'DM Serif Display', serif; font-size: 14px; color: #fff; flex-shrink: 0;
}
.t-name { font-size: 14px; font-weight: 500; color: #F0EEF8; }
.t-spec { font-size: 12px; color: #9896A8; margin-top: 2px; }
.advice-section { padding: 16px; }
.advice-label {
    font-size: 10px; font-weight: 500; color: #A78BFA;
    letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 10px;
}
.advice-text { font-size: 14px; color: #9896A8; line-height: 1.85; }

/* ── Starter prompts ── */
.starters-title { font-size: 13px; color: #5C5A6B; text-align: center; margin-bottom: 12px; }

/* ── Divider ── */
.emp-divider { border: none; border-top: 1px solid rgba(255,255,255,0.07); margin: 24px 0; }

/* ── Input overrides ── */
.stTextArea textarea {
    background: #1C2030 !important; color: #F0EEF8 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 14px !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important; resize: none !important;
}
.stTextArea textarea:focus {
    border-color: rgba(167,139,250,0.5) !important;
    box-shadow: 0 0 0 3px rgba(167,139,250,0.08) !important;
}
.stTextArea textarea::placeholder { color: #5C5A6B !important; }
.stTextArea label { color: #9896A8 !important; font-size: 13px !important; }

/* ── Button ── */
.stButton > button {
    width: 100%; background: linear-gradient(135deg, #7C3AED, #A78BFA) !important;
    color: white !important; border: none !important; border-radius: 14px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 15px !important;
    font-weight: 500 !important; padding: 12px 0 !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.3) !important;
    transition: opacity 0.15s !important; cursor: pointer !important;
}
.stButton > button:hover { opacity: 0.88 !important; }
.stButton > button:disabled { opacity: 0.4 !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #151820 !important; border-right: 1px solid rgba(255,255,255,0.07) !important;
}
section[data-testid="stSidebar"] * { color: #9896A8 !important; }
section[data-testid="stSidebar"] h2 { color: #F0EEF8 !important; }

/* ── Footer hint ── */
.emp-footer { text-align: center; font-size: 11px; color: #5C5A6B; margin-top: 20px; }

/* ── Error ── */
.emp-error {
    padding: 12px 16px; background: rgba(248,113,113,0.1);
    border: 1px solid rgba(248,113,113,0.2); border-radius: 12px;
    font-size: 13px; color: #F87171; margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []          # list of {role, content, data}
if "api_key" not in st.session_state:
    st.session_state.api_key = ""


# ── Sidebar – API key ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")
    api_input = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        value=st.session_state.api_key,
        help="Get your key at console.anthropic.com",
    )
    if api_input:
        st.session_state.api_key = api_input
    st.markdown("---")
    st.markdown("**About Empathica**")
    st.markdown(
        "Empathica is an AI emotional wellness companion. "
        "It detects emotions, identifies topics, and offers compassionate advice inspired by real therapeutic approaches."
    )
    st.markdown("---")
    st.caption("⚠️ Not a substitute for professional mental health care.")
    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.rerun()


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="emp-header">
  <div class="emp-orb">💜</div>
  <div>
    <div class="emp-title">Empathic<span>a</span></div>
    <div class="emp-sub">Your emotional wellness companion</div>
  </div>
  <div class="emp-badge">● Online</div>
</div>
""", unsafe_allow_html=True)


# ── Helper: call Claude ────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Empathica — a warm, emotionally intelligent AI wellness companion.

Analyze the user's message and respond ONLY with a valid JSON object (no markdown, no backticks, no preamble) in this exact format:
{
  "emotion": "<primary emotion, e.g. anxiety, loneliness, grief, anger, overwhelm>",
  "topic": "<main theme, e.g. work stress, relationship issues, self-worth>",
  "therapist_name": "<realistic full name with title, e.g. Dr. Priya Sharma>",
  "therapist_specialization": "<credentials + specialization, e.g. Licensed Clinical Psychologist · Cognitive Behavioural Therapy>",
  "advice": "<3-5 sentences of warm, empathetic, psychologically grounded advice. Acknowledge their pain first, then offer a gentle perspective or coping strategy. Sound like a compassionate human therapist.>"
}

RULES:
- Never mention being an AI
- Always validate feelings before offering advice
- Keep advice practical and grounding
- Never be preachy or judgmental"""


def call_empathica(user_text: str, api_key: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_text}],
    )
    raw = response.content[0].text
    clean = re.sub(r"```json|```", "", raw).strip()
    return json.loads(clean)


def get_initials(name: str) -> str:
    parts = name.replace("Dr.", "").replace("Mr.", "").replace("Ms.", "").strip().split()
    return "".join(p[0].upper() for p in parts[:2])


def render_analysis_card(data: dict) -> str:
    initials = get_initials(data["therapist_name"])
    return f"""
<div class="bot-msg-wrap">
  <div class="bot-avatar">💜</div>
  <div class="analysis-card">
    <div class="card-header">Empathica Analysis</div>
    <div class="tags-row">
      <span class="tag-emotion">🫀 Emotion: {data['emotion'].title()}</span>
      <span class="tag-topic">💬 Topic: {data['topic'].title()}</span>
    </div>
    <div class="therapist-row">
      <div class="t-avatar">{initials}</div>
      <div>
        <div class="t-name">{data['therapist_name']}</div>
        <div class="t-spec">{data['therapist_specialization']}</div>
      </div>
    </div>
    <div class="advice-section">
      <div class="advice-label">Therapist Advice</div>
      <div class="advice-text">{data['advice']}</div>
    </div>
  </div>
</div>"""


# ── Welcome / starter prompts ──────────────────────────────────────────────────
STARTERS = [
    "💭  I've been feeling really anxious about my future lately",
    "😔  I feel so alone even when I'm surrounded by people",
    "😤  I'm overwhelmed with work and can't seem to switch off",
    "💔  I'm going through a painful breakup and don't know how to cope",
]

if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 28px;">
      <div style="font-size:52px;margin-bottom:14px;">💜</div>
      <div style="font-family:'DM Serif Display',serif;font-size:24px;color:#F0EEF8;margin-bottom:8px;">Hello, I'm Empathica</div>
      <div style="font-size:14px;color:#9896A8;max-width:340px;margin:0 auto;line-height:1.7;">
        A safe space to share how you're feeling. I'll listen without judgment and offer thoughtful, compassionate support.
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="starters-title">— Try one of these to get started —</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, s in enumerate(STARTERS):
        with cols[i % 2]:
            if st.button(s, key=f"starter_{i}", use_container_width=True):
                clean_text = re.sub(r"^[^\s]+\s{2}", "", s)
                st.session_state.pending_input = clean_text
                st.rerun()

    st.markdown("<hr class='emp-divider'>", unsafe_allow_html=True)


# ── Render chat history ────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="user-msg-wrap">
          <div class="user-bubble">{msg['content']}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(render_analysis_card(msg["data"]), unsafe_allow_html=True)


# ── Process pending starter input ─────────────────────────────────────────────
if "pending_input" in st.session_state:
    pending = st.session_state.pop("pending_input")
    if pending and st.session_state.api_key:
        st.session_state.messages.append({"role": "user", "content": pending})
        with st.spinner("Empathica is listening…"):
            try:
                result = call_empathica(pending, st.session_state.api_key)
                st.session_state.messages.append({"role": "bot", "content": "", "data": result})
            except Exception as e:
                st.markdown(f'<div class="emp-error">⚠️ {str(e)}</div>', unsafe_allow_html=True)
        st.rerun()
    elif not st.session_state.api_key:
        st.session_state.messages.append({"role": "user", "content": pending})
        st.warning("⚠️ Please enter your Anthropic API key in the sidebar to get a response.")
        st.rerun()


# ── Input form ─────────────────────────────────────────────────────────────────
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_area(
        "Share what's on your mind…",
        placeholder="e.g. I've been feeling overwhelmed and don't know how to cope…",
        height=100,
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Send to Empathica  💜", use_container_width=True)

if submitted and user_input.strip():
    if not st.session_state.api_key:
        st.warning("⚠️ Please enter your Anthropic API key in the sidebar.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        with st.spinner("Empathica is listening…"):
            try:
                result = call_empathica(user_input.strip(), st.session_state.api_key)
                st.session_state.messages.append({"role": "bot", "content": "", "data": result})
            except json.JSONDecodeError:
                st.markdown('<div class="emp-error">⚠️ Could not parse response. Please try again.</div>', unsafe_allow_html=True)
            except anthropic.AuthenticationError:
                st.markdown('<div class="emp-error">⚠️ Invalid API key. Please check your key in the sidebar.</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="emp-error">⚠️ Error: {str(e)}</div>', unsafe_allow_html=True)
        st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="emp-footer">Empathica is not a substitute for professional mental health care · Built with Claude AI</div>', unsafe_allow_html=True)
