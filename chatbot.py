import streamlit as st
import google.generativeai as genai

# --- Page Config ---
st.set_page_config(page_title="Universal AI Assistant", page_icon="🤖")
st.title("🤖 Universal AI Assistant")
st.caption("Powered by Google Gemini (Secure Mode)")

# --- 1. API Key Setup (Automatic) ---
# Pehle hum sidebar se mangte the, ab hum Secrets se lenge
try:
    # Ye line cloud se ya local secrets.toml file se key uthayegi
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    # Agar key nahi mili to error dikhayega
    st.error("⚠️ Error: API Key nahi mili! Please Streamlit Secrets check karein.")
    st.stop()

# --- Sidebar (Sirf Clear Button ke liye) ---
with st.sidebar:
    st.header("Settings")
    if st.button("Chat Clear Karein"):
        st.session_state.messages = []
        st.session_state.chat = None
        st.rerun()

# --- 2. Chat History Initialize ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. Model Setup (Auto-Detect Logic) ---
if "chat" not in st.session_state or st.session_state.chat is None:
    try:
        # Hum direct naya model try karenge
        model = genai.GenerativeModel('gemini-1.5-flash')
        st.session_state.chat = model.start_chat(history=[])
    except Exception as e:
        st.error(f"Model connect nahi hua: {e}")

# --- 4. Chat Interface ---
# Purane messages dikhana
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Naya input lena
if prompt := st.chat_input("Kuch bhi poochein..."):
    # User ka message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI ka jawab
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Soch raha hoon...")
        
        try:
            response = st.session_state.chat.send_message(prompt)
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            message_placeholder.error(f"Error aaya: {e}")
