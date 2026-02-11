import streamlit as st
import google.generativeai as genai

# --- Page Setup ---
st.set_page_config(page_title="Universal AI Assistant", page_icon="🤖")
st.title("🤖 Universal AI Assistant")

# --- 1. API Key Setup ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        # Fallback for local testing
        api_key = st.sidebar.text_input("Enter API Key", type="password")
        
    if not api_key:
        st.warning("⚠️ Please enter an API Key.")
        st.stop()
        
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"API Key Error: {e}")
    st.stop()

# --- 2. Smart Model Selector (Error 404 Fix) ---
@st.cache_resource
def get_best_model():
    # Priority list: Try these models in order
    preferences = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-pro"]
    available_models = []
    
    try:
        # Google se pucho kaunse model zinda hain
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        # Check priority
        for pref in preferences:
            full_name = f"models/{pref}"
            if full_name in available_models:
                return pref
        
        # Agar list mein se koi na mile, toh pehla available utha lo
        if available_models:
            return available_models[0].replace("models/", "")
            
    except Exception as e:
        return None
    return None

# Model select karein
model_name = get_best_model()

if not model_name:
    st.error("❌ Koi bhi model nahi mila. Shayad API Key galat hai ya Quota expire ho gaya.")
    st.stop()

# --- 3. Chat Logic (Error 400 & 429 Fix) ---
# Hum chat object ko session mein rakhenge taaki history automatic handle ho
if "chat_session" not in st.session_state:
    try:
        model = genai.GenerativeModel(model_name)
        st.session_state.chat_session = model.start_chat(history=[])
        st.sidebar.success(f"Connected to: {model_name}") # Ye batayega kaunsa model connect hua
    except Exception as e:
        st.error(f"Connection failed: {e}")

# --- 4. Display Chat ---
# Chat history display karna
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input handle karna
if prompt := st.chat_input("Ask me anything..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            # Send message using internal chat session
            # Ye automatic history maintain karta hai, isliye 'Role' error nahi aayega
            response = st.session_state.chat_session.send_message(prompt)
            
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            # Agar Quota error aaye (Error 429)
            if "429" in str(e):
                message_placeholder.error("⏳ Quota Exceeded. Please wait 1-2 minutes.")
            else:
                message_placeholder.error(f"Error: {e}")
                # Agar session expire ho gaya ho toh reset ka option
                if st.button("Reset Connection"):
                    del st.session_state.chat_session
                    st.rerun()
