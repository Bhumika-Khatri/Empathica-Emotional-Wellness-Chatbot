import streamlit as st
import pandas as pd
import anthropic
import json
import re

# ── Load Dataset ─────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("counsel_chat.csv")
    df = df.dropna(subset=["questionText", "answerText", "therapistInfo"])
    return df

df = load_data()

# ── Page Config ─────────────────────────────
st.set_page_config(page_title="Empathica 💜", page_icon="💜")

# ── Session State ───────────────────────────
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# ── Sidebar ────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")
    api_input = st.text_input("Anthropic API Key", type="password")
    if api_input:
        st.session_state.api_key = api_input

    st.markdown("⚠️ Not a substitute for therapy")

# ── Claude Prompt (ONLY emotion + topic) ────
SYSTEM_PROMPT = """
Analyze user input and return ONLY JSON:

{
 "emotion": "",
 "topic": ""
}

No extra text.
"""

def detect_emotion(user_text, api_key):
    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_text}],
    )

    raw = response.content[0].text
    clean = re.sub(r"```json|```", "", raw).strip()

    return json.loads(clean)

# ── Match dataset based on user input ───────
def get_best_match(user_text):
    user_text = user_text.lower()

    df["score"] = df["questionText"].apply(
        lambda x: sum(word in str(x).lower() for word in user_text.split())
    )

    best = df.sort_values(by="score", ascending=False).iloc[0]

    return {
        "question": best["questionText"],
        "therapist": best["therapistInfo"],
        "answer": best["answerText"],
        "topic": best["topic"]
    }

# ── UI ─────────────────────────────────────
st.title("💜 Empathica")
st.write("Your emotional wellness companion")

user_input = st.text_area("How are you feeling?")

if st.button("Send 💜"):

    if not user_input.strip():
        st.warning("Please write something")
    
    else:
        with st.spinner("Listening..."):

            try:
                # emotion detection (only if key present)
                if st.session_state.api_key:
                    emo = detect_emotion(user_input, st.session_state.api_key)
                    emotion = emo.get("emotion", "Unknown")
                    topic_ai = emo.get("topic", "General")
                else:
                    emotion = "Unknown"
                    topic_ai = "General"

                # dataset match
                data = get_best_match(user_input)

                # ── OUTPUT ──
                st.subheader("🫀 Emotion")
                st.write(emotion)

                st.subheader("💬 Topic")
                st.write(data["topic"])

                st.subheader("👩‍⚕️ Therapist")
                st.write(data["therapist"])

                st.subheader("💜 Advice")
                st.write(data["answer"])

            except Exception as e:
                st.error(f"Error: {str(e)}")
