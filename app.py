import streamlit as st
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── CONFIG ─────────────────────────────
st.set_page_config(page_title="Empathica 💜", layout="centered")

USER_FILE = "users.csv"

# ── AUTH FUNCTIONS ─────────────────────
def load_users():
    if not os.path.exists(USER_FILE):
        return pd.DataFrame(columns=["username", "password"])
    return pd.read_csv(USER_FILE)

def save_user(username, password):
    df = load_users()
    if username in df["username"].values:
        return False
    new_user = pd.DataFrame([[username, password]], columns=["username", "password"])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USER_FILE, index=False)
    return True

def authenticate(username, password):
    df = load_users()
    user = df[(df["username"] == username) & (df["password"] == password)]
    return not user.empty

# ── LOAD DATA ──────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("counsel_chat.csv")
    df = df.dropna(subset=["questionText", "answerText", "therapistInfo"])
    return df

df = load_data()

vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df["questionText"])

# ── EMOTION DETECTION ──────────────────
def detect_emotion(text):
    text = text.lower()
    if any(w in text for w in ["lonely","alone","isolated"]):
        return "depression"
    elif any(w in text for w in ["anxious","stress","worried"]):
        return "anxiety"
    elif any(w in text for w in ["angry","frustrated"]):
        return "anger"
    elif any(w in text for w in ["breakup","heartbroken"]):
        return "grief"
    else:
        return "sadness"

# ── MATCH RESPONSE ─────────────────────
def get_best_match(user_text):
    user_vec = vectorizer.transform([user_text])
    similarity = cosine_similarity(user_vec, tfidf_matrix)
    best = df.iloc[similarity.argmax()]
    return best

# ── SESSION ────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── UI STYLE ───────────────────────────
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #1a1f3c, #0e1117 60%);
}

.card {
    background: rgba(28,32,48,0.7);
    padding:20px;
    border-radius:20px;
    backdrop-filter: blur(10px);
}

.user {
    background: linear-gradient(135deg,#7C3AED,#A78BFA);
    padding:10px 15px;
    border-radius:15px;
    color:white;
    text-align:right;
    margin:8px 0;
}

.bot {
    background: rgba(255,255,255,0.05);
    padding:15px;
    border-radius:15px;
    margin:8px 0;
    color:#E5E7EB;
}

.avatar {
    width:40px;
    height:40px;
    border-radius:50%;
    background:linear-gradient(135deg,#7C3AED,#A78BFA);
    display:flex;
    align-items:center;
    justify-content:center;
    color:white;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ── LOGIN / SIGNUP ─────────────────────
if not st.session_state.logged_in:

    st.markdown("<h2 style='text-align:center;color:white;'>💜 Empathica</h2>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(u, p):
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        nu = st.text_input("Create Username")
        np = st.text_input("Create Password", type="password")

        if st.button("Signup"):
            if save_user(nu, np):
                st.success("Account created! Login now.")
            else:
                st.warning("User already exists")

    st.stop()

# ── PROFILE HEADER ─────────────────────
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
    <div style="display:flex;align-items:center;gap:10px;">
        <div class="avatar">{st.session_state.username[0].upper()}</div>
        <div style="color:white;">
            <b>{st.session_state.username}</b><br>
            <span style="font-size:12px;color:#9CA3AF;">Online</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── LOGOUT ─────────────────────────────
if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.messages = []
    st.rerun()

# ── CHAT BOX ───────────────────────────
st.markdown("<div class='card'>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='bot'>

        <b>Detected Emotion:</b> {msg['emotion']}<br><br>

        <b>Topic:</b> {msg['topic']}<br><br>

        <b>Therapist Info:</b><br>
        {msg['therapist']}<br><br>

        <b>Therapist Advice:</b><br>
        {msg['answer']}

        <br><br>
        <div style="text-align:right;color:#A78BFA;font-size:12px;">
        — Empathica 💜
        </div>

        </div>
        """, unsafe_allow_html=True)

# ── INPUT ──────────────────────────────
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Share what's on your mind...")
    send = st.form_submit_button("Send 💜")

if send and user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    emotion = detect_emotion(user_input)
    best = get_best_match(user_input)

    st.session_state.messages.append({
        "role": "bot",
        "emotion": emotion,
        "topic": best["topic"],
        "therapist": best["therapistInfo"],
        "answer": best["answerText"]
    })

    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ── CLEAR CHAT ─────────────────────────
if st.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.rerun()
