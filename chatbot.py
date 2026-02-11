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

# --- 2. Auto-Detect Model (Magic Fix) ---
# Ye function check karega ki kaunsa model available hai
@st.cache_resource
def get_model():
    try:
        # Google se pucho ki kaunse models available hain
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Pehla working model milte hi return kar do
                return m.name
    except Exception as e:
        return None

# Model select karo
model_name = get_model()

if model_name:
    # Sidebar mein dikhao ki kaunsa model connect hua
    with st.sidebar:
        st.success(f"Connected to: **{model_name}**")
        if st.button("Reset Chat"):
            st.session_state.messages = []
            st.rerun()
            
    model = genai.GenerativeModel(model_name)
else:
    st.error("❌ Koi bhi model nahi mila. Shayad API Key galat hai ya Quota khatam ho gaya hai.")
    st.stop()

# --- 3. Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. Chat Interface ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask me anything..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        try:
            # Chat object har baar naya banayenge taaki purane errors na aayein
            chat = model.start_chat(history=[
                {"role": m["role"], "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1] # Current prompt chhod kar purani history
            ])
            
            response = chat.send_message(prompt)
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            message_placeholder.error(f"Error: {e}")
