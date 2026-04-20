import streamlit as st
import pandas as pd
import re

# ML for better matching
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Load Dataset ─────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("counsel_chat.csv")
    df = df.dropna(subset=["questionText", "answerText", "therapistInfo"])
    return df

df = load_data()

# ── TF-IDF Setup (IMPORTANT FIX) ─────────────
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df["questionText"])

# ── Page Config ─────────────────────────────
st.set_page_config(page_title="Empathica 💜", page_icon="💜")

# ── Emotion Detection (NO API NEEDED) ───────
def detect_emotion(text):
    text = text.lower()

    if any(word in text for word in ["lonely", "alone", "isolated"]):
        return "depression", "loneliness"
    elif any(word in text for word in ["anxious", "stress", "worried"]):
        return "anxiety", "stress"
    elif any(word in text for word in ["angry", "mad", "frustrated"]):
        return "anger", "frustration"
    elif any(word in text for word in ["breakup", "heartbroken"]):
        return "grief", "relationship"
    else:
        return "sadness", "general"

# ── Smart Matching (FIXED) ───────────────────
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

# ── UI ──────────────────────────────────────
st.title("💜 Empathica")
st.write("Your emotional wellness companion")

user_input = st.text_area("How are you feeling?")

if st.button("Send 💜"):

    if not user_input.strip():
        st.warning("Please write something")
    
    else:
        with st.spinner("Listening..."):

            try:
                # Emotion detection
                emotion, topic_detected = detect_emotion(user_input)

                # Dataset matching
                data = get_best_match(user_input)

                # ── OUTPUT ──
                st.subheader("🫀 Emotion")
                st.write(emotion)

                st.subheader("💬 Topic")
                st.write(topic_detected)

                st.subheader("👩‍⚕️ Therapist")
                st.write(data["therapist"])

                st.subheader("💜 Advice")
                st.write(data["answer"])

            except Exception as e:
                st.error(f"Error: {str(e)}")
