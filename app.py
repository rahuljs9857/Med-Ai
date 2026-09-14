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
<style>
.stApp {
    background: linear-gradient(135deg, #eef3f8 0%, #dce8f5 50%, #cfe0f2 100%);
}
[data-testid="stChatMessage"] {
    border-radius: 14px;
    padding: 10px 14px;
    margin-bottom: 8px;
}
.stChatMessage:has(> div[data-testid="stChatMessageAvatarUser"]) {
    background-color: #e3edf7;
}
h1, h2, h3 {
    color: #2c4661;
}
.stButton>button {
    background: linear-gradient(90deg, #6fa3d8, #4c7fb3);
    color: white;
    border: none;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

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
