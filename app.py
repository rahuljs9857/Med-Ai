import streamlit as st
from google import genai

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MediAI", page_icon="🩺", layout="centered")

KB_FILE = "Healthchatbot.txt"
MODEL = "gemini-2.5-flash"

# API key comes from Streamlit secrets, not hardcoded in the file.
# Locally: create .streamlit/secrets.toml with GEMINI_API_KEY = "your-key"
# On Streamlit Cloud: set it under App settings -> Secrets
API_KEY = st.secrets["GEMINI_API_KEY"]

# ---------------- STYLING ----------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:wght@500;600;700&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #1B2A41;
}
.stApp {
    background: linear-gradient(180deg, #f3f6fb 0%, #e6edf7 45%, #d9e4f3 100%);
}
p, span, label, div, li {
    color: #1B2A41;
}
h1, h2, h3 {
    font-family: 'Fraunces', serif;
    color: #16223A;
    font-weight: 600;
    letter-spacing: -0.01em;
}
.stCaption, [data-testid="stCaptionContainer"] {
    color: #445269 !important;
    font-size: 0.92rem;
}
[data-testid="stChatMessage"] {
    background-color: #ffffff;
    border: 1px solid #E4EAF3;
    border-radius: 16px;
    padding: 14px 18px;
    margin-bottom: 12px;
    box-shadow: 0 3px 12px rgba(40, 70, 110, 0.06);
    color: #1B2A41;
}
[data-testid="stChatMessage"] p {
    color: #1B2A41;
    line-height: 1.55;
}
.stChatMessage:has(> div[data-testid="stChatMessageAvatarUser"]) {
    background-color: #EEF3FB;
    border-color: #DCE6F5;
}
[data-testid="stChatInput"] > div {
    background: #ffffff;
    border: 1px solid #DCE6F5;
    border-radius: 14px;
    box-shadow: 0 4px 14px rgba(40, 70, 110, 0.07);
}
[data-testid="stChatInput"] textarea {
    color: #1B2A41 !important;
}
.stButton>button, [data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #3E5C8A, #2C4165);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    font-weight: 500;
    transition: box-shadow 0.15s ease, transform 0.15s ease;
}
.stButton>button:hover, [data-testid="stChatInput"] button:hover {
    box-shadow: 0 4px 14px rgba(44, 65, 101, 0.28);
    transform: translateY(-1px);
}
 
/* ---- Background decoration: faded watermark + floating equipment ---- */
[data-testid="stAppViewContainer"], [data-testid="stMain"] {
    position: relative;
    z-index: 1;
}
.bg-decor {
    position: fixed;
    inset: 0;
    overflow: hidden;
    pointer-events: none;
    z-index: 0;
}
.bg-watermark {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-6deg);
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 13vw;
    color: #2C4165;
    opacity: 0.05;
    white-space: nowrap;
}
.float-icon {
    position: absolute;
    color: #3E5C8A;
    opacity: 0.16;
    animation: floaty 7s ease-in-out infinite;
}
@keyframes floaty {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-18px) rotate(4deg); }
}
</style>
""", unsafe_allow_html=True)
 
# Floating hospital-equipment icons + a large faded "MED AI" watermark,
# all fixed to the viewport behind the actual chat content (z-index 0
# vs the content's z-index 1), non-interactive (pointer-events: none)
# so they never block clicks.
st.html("""
<div class="bg-decor">
    <div class="bg-watermark">MED AI</div>
 
    <svg class="float-icon" style="top:8%; left:6%; animation-delay:0s;" width="70" height="70" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4">
        <path d="M4 3v7a5 5 0 0 0 5 5v0a5 5 0 0 0 5-5V3"/>
        <circle cx="18" cy="16" r="3"/>
        <path d="M14 15v-2"/>
    </svg>
 
    <svg class="float-icon" style="top:18%; left:85%; animation-delay:1.2s;" width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4">
        <rect x="3" y="3" width="18" height="18" rx="3"/>
        <path d="M12 8v8M8 12h8"/>
    </svg>
 
    <svg class="float-icon" style="top:70%; left:4%; animation-delay:2.4s;" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4">
        <rect x="6" y="2" width="4" height="8" rx="1"/>
        <path d="M8 10v10a2 2 0 0 0 4 0V10"/>
    </svg>
 
    <svg class="float-icon" style="top:80%; left:80%; animation-delay:0.6s;" width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4">
        <rect x="4" y="9" width="9" height="6" rx="1.5"/>
        <path d="M13 12h3l2-2v4l-2-2"/>
    </svg>
 
    <svg class="float-icon" style="top:42%; left:92%; animation-delay:1.8s;" width="50" height="50" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4">
        <path d="M2 12h4l2-6 4 12 3-9 2 3h5"/>
    </svg>
 
    <svg class="float-icon" style="top:52%; left:2%; animation-delay:3s;" width="50" height="50" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4">
        <rect x="10" y="3" width="4" height="14" rx="2"/>
        <circle cx="12" cy="19" r="2.5"/>
    </svg>
</div>
""")
 
st.title("🩺 MediAI")
st.caption("AI-powered health information & clinical decision-support assistant")
 
# ---------------- LOAD KB ----------------
@st.cache_data
def load_kb():
    with open(KB_FILE, "r") as f:
        return f.read()

kb = load_kb()

SYSTEM_PROMPT = f"""
You are MediAI, an AI-powered health information and clinical decision-support assistant.
You help users understand symptoms, identify possible health conditions, assess risk, and suggest the appropriate medical specialist.
You can help users find verified doctors and hospitals around Tirunelveli and Tamil Nadu when requested.
You provide health information, not definitive diagnoses or personalized prescriptions.
Always encourage users to consult a qualified medical professional for diagnosis and treatment.

{kb}
"""

# ---------------- INIT CLIENT & CHAT SESSION ----------------
@st.cache_resource
def get_client():
    return genai.Client(api_key=API_KEY)

client = get_client()

if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(
        model=MODEL,
        config={"system_instruction": SYSTEM_PROMPT}
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- RENDER CHAT HISTORY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- CHAT INPUT ----------------
user_input = st.chat_input("Describe your symptoms or ask a question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat.send_message(user_input)
            st.markdown(response.text)

    st.session_state.messages.append({"role": "assistant", "content": response.text})
