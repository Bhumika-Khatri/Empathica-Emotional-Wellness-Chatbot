# ── Session State for Chat ───────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="Empathica 💜", page_icon="💜", layout="centered")

# ── CUSTOM CSS (BEAUTIFUL UI) ────────────────
st.markdown("""
<style>
body {
    background-color: #0E1117;
}
.chat-container {
    max-width: 700px;
    margin: auto;
}
.user-bubble {
    background: linear-gradient(135deg, #7C3AED, #A78BFA);
    color: white;
    padding: 12px 16px;
    border-radius: 18px;
    margin: 10px 0;
    text-align: right;
}
.bot-bubble {
    background: #1C2030;
    color: #E5E7EB;
    padding: 14px 16px;
    border-radius: 18px;
    margin: 10px 0;
}
.title {
    text-align: center;
    font-size: 32px;
    font-weight: bold;
    color: #A78BFA;
}
.subtitle {
    text-align: center;
    color: #9CA3AF;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────
st.markdown('<div class="title">💜 Empathica</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Your emotional wellness companion</div>', unsafe_allow_html=True)

# ── SHOW CHAT HISTORY ──────────────────────
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

# ── INPUT ──────────────────────────────────
user_input = st.text_input("Share what's on your mind...")

if st.button("Send 💜"):

    if user_input.strip():

        # Save user msg
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        # Emotion + matching
        emotion, topic_detected = detect_emotion(user_input)
        data = get_best_match(user_input)

        bot_data = {
            "emotion": emotion,
            "topic": topic_detected,
            "therapist": data["therapist"],
            "answer": data["answer"]
        }

        # Save bot msg
        st.session_state.messages.append({
            "role": "bot",
            "data": bot_data
        })

        st.rerun()

# ── CLEAR BUTTON ───────────────────────────
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()
