import streamlit as st
import pandas as pd
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Page Config ─────────────────────────────
st.set_page_config(page_title="Empathica 💜", page_icon="💜", layout="centered")

# ── Load Dataset ────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("counsel_chat.csv")
    df = df.dropna(subset=["questionText", "answerText", "therapistInfo"])
    return df

df = load_data()

# ── TF-IDF Setup ───────────────────────────
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df["questionText"])

# ── Emotion Detection ──────────────────────
def detect_emotion(text):
    text = text.lower()

    if any(w in text for w in ["lonely", "alone", "isolated"]):
        return "depression", "loneliness"
    elif any(w in text for w in ["anxious", "stress", "worried"]):
        return "anxiety", "stress"
    elif any(w in text for w in ["angry", "mad", "frustrated"]):
        return "anger", "frustration"
    elif any(w in text for w in ["breakup", "heartbroken"]):
        return "grief", "relationship"
    else:
        return "sadness", "general"

# ── Smart Matching ─────────────────────────
def get_best_match(user_text):
    user_vec = vectorizer.transform([user_text])
    similarity = cosine_similarity(user_vec, tfidf_matrix)

    best_idx = similarity.argmax()
    best = df.iloc[best_idx]

    return {
        "therapist": best["therapistInfo"],
        "answer": best["answerText"],
        "topic": best["topic"]
    }

# ── Session State ──────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── UI CSS ─────────────────────────────────
st.markdown("""
<style>

/* ── FULL APP BACKGROUND ── */
.stApp {
    background: radial-gradient(circle at top left, #1a1f3c, #0e1117 60%);
    background-attachment: fixed;
}

/* Optional glowing overlay */
.stApp::before {
    content: "";
    position: fixed;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(124,58,237,0.25), transparent 70%);
    top: -100px;
    left: -100px;
    filter: blur(100px);
    z-index: -1;
}

/* ── USER MESSAGE ── */
.user-bubble {
    background: linear-gradient(135deg, #7C3AED, #A78BFA);
    color: white;
    padding: 12px 16px;
    border-radius: 18px 18px 4px 18px;
    margin: 10px 0;
    text-align: right;
    box-shadow: 0 4px 15px rgba(124,58,237,0.3);
}

/* ── BOT MESSAGE ── */
.bot-bubble {
    background: rgba(28,32,48,0.85);
    backdrop-filter: blur(10px);
    color: #E5E7EB;
    padding: 14px 16px;
    border-radius: 18px 18px 18px 4px;
    margin: 10px 0;
    border: 1px solid rgba(255,255,255,0.05);
}

/* ── TITLE ── */
.title {
    text-align: center;
    font-size: 34px;
    font-weight: bold;
    background: linear-gradient(135deg, #A78BFA, #7C3AED);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ── SUBTITLE ── */
.subtitle {
    text-align: center;
    color: #9CA3AF;
    margin-bottom: 25px;
    font-size: 14px;
}

/* ── INPUT BOX ── */
.stTextInput input {
    background-color: #1C2030 !important;
    color: #E5E7EB !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}

/* ── BUTTON ── */
.stButton button {
    background: linear-gradient(135deg, #7C3AED, #A78BFA) !important;
    color: white !important;
    border-radius: 12px !important;
    border: none !important;
    font-weight: 500;
    box-shadow: 0 4px 15px rgba(124,58,237,0.4);
}

</style>
""", unsafe_allow_html=True)
# ── Header ─────────────────────────────────
st.markdown('<div class="title">💜 Empathica</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Your emotional wellness companion</div>', unsafe_allow_html=True)

# ── Show Chat ──────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        data = msg["data"]
        st.markdown(f"""
        <div class="bot-bubble">
        🫀 <b>Emotion:</b> {data['emotion']}<br>
        💬 <b>Topic:</b> {data['topic']}<br><br>
        👩‍⚕️ <b>{data['therapist']}</b><br><br>
        💜 {data['answer']}
        </div>
        """, unsafe_allow_html=True)

# ── Input ──────────────────────────────────
# ── Input State Fix ─────────────────────────
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

user_input = st.text_input(
    "Share what's on your mind...",
    key="input_text"
)

if st.button("Send 💜"):

    if st.session_state.input_text.strip():

        text = st.session_state.input_text  # store before clearing

        # Save user message
        st.session_state.messages.append({
            "role": "user",
            "content": text
        })

        # Process
        emotion, topic_detected = detect_emotion(text)
        data = get_best_match(text)

        bot_data = {
            "emotion": emotion,
            "topic": topic_detected,
            "therapist": data["therapist"],
            "answer": data["answer"]
        }

        # Save bot response
        st.session_state.messages.append({
            "role": "bot",
            "data": bot_data
        })

        # 🔥 CLEAR INPUT (THIS FIXES YOUR PROBLEM)
        st.session_state.input_text = ""

        st.rerun()

# ── Clear Chat ─────────────────────────────
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()
