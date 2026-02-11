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

# --- 2. Auto-Detect Model ---
@st.cache_resource
def get_model():
    try:
        # Check available models
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except Exception as e:
        return None

model_name = get_model()
if not model_name:
    st.error("❌ Koi bhi model nahi mila. API Key check karein.")
    st.stop()

model = genai.GenerativeModel(model_name)

# --- 3. Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. Chat Interface ---
# Purane messages dikhana
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Ask me anything..."):
    # 1. User ka message UI par dikhayein
    with st.chat_message("user"):
        st.markdown(prompt)
    # 2. Session state mein save karein
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            # --- MAIN FIX IS HERE (ROLE CONVERSION) ---
            # Streamlit ki history ko Gemini ke format mein badalna padega
            gemini_history = []
            
            # Hum last message (current prompt) ko history mein nahi dalenge
            # Kyunki wo send_message() mein jayega
            for msg in st.session_state.messages[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg["content"]]})
            
            # Chat start karein purani history ke saath
            chat = model.start_chat(history=gemini_history)
            
            # Naya sawal bhejein
            response = chat.send_message(prompt)
            
            message_placeholder.markdown(response.text)
            
            # Jawab ko session state mein save karein (as 'assistant' for Streamlit)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            message_placeholder.error(f"Error: {e}")
