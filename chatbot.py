import streamlit as st
import google.generativeai as genai

# --- Page Setup ---
st.set_page_config(page_title="Universal AI Assistant", page_icon="🤖")
st.title("🤖 Universal AI Assistant")

# --- 1. API Key Setup ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ API Key Error: Please check Streamlit Secrets.")
    st.stop()

# --- 2. Model Setup (Fixed to 1.5 Flash for High Limit) ---
# Hum 'gemini-1.5-flash' use karenge kyunki iska free quota sabse zyada hai
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error connecting to model: {e}")
    st.stop()

# --- 3. Chat Session State ---
# Hum chat object ko session_state mein rakhenge taaki history yaad rahe
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. Chat Interface ---
# Purane messages dikhayein
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input Handle Karein
if prompt := st.chat_input("Ask me anything..."):
    # User ka message UI par
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            # Seedha chat object use karein (ye internal history maintain karta hai)
            response = st.session_state.chat.send_message(prompt)
            
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            # Agar phir se Quota error aaye, toh saaf batayein
            if "429" in str(e):
                message_placeholder.error("⏳ Too many requests! Please wait 1 minute.")
            else:
                message_placeholder.error(f"Error: {e}")
