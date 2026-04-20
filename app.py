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
body { background-color: #0E1117; }
.user-bubble {
    background: linear-gradient(135deg, #7C3AED, #A78BFA);
    color: white;
    padding: 12px;
    border-radius: 18px;
    margin: 10px 0;
    text-align: right;
}
.bot-bubble {
    background: #1C2030;
    color: #E5E7EB;
    padding: 14px;
    border-radius: 18px;
    margin: 10px 0;
}
.title {
    text-align: center;
    font-size: 32px;
    color: #A78BFA;
}
.subtitle {
    text-align: center;
    color: #9CA3AF;
    margin-bottom: 20px;
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
user_input = st.text_input("Share what's on your mind...")

if st.button("Send 💜"):

    if user_input.strip():

        # Save user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        # Process
        emotion, topic_detected = detect_emotion(user_input)
        data = get_best_match(user_input)

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

        st.rerun()

# ── Clear Chat ─────────────────────────────
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()
