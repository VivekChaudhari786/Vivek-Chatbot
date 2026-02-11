import streamlit as st
import google.generativeai as genai

# --- Page Setup ---
st.set_page_config(page_title="Universal AI Assistant", page_icon="🤖")
st.title("🤖 Universal AI Assistant (Auto-Fix)")

# --- Sidebar ---
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Google Gemini API Key:", type="password")
    
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.session_state.chat = None
        st.rerun()

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat" not in st.session_state:
    st.session_state.chat = None

# --- Main Logic ---
if api_key:
    try:
        # 1. API Configure
        genai.configure(api_key=api_key)
        
        # 2. AUTO-DETECT MODEL (Ye step error fix karega)
        if st.session_state.chat is None:
            available_model_name = None
            
            # Google se puchte hain ki kaunse models available hain
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    # Pehla working model utha lo (usually gemini-1.5-flash ya gemini-pro)
                    available_model_name = m.name
                    break
            
            if available_model_name:
                st.success(f"Connected to model: **{available_model_name}**")
                model = genai.GenerativeModel(available_model_name)
                st.session_state.chat = model.start_chat(history=[])
            else:
                st.error("❌ Koi bhi model nahi mila. Kripya API Key check karein.")
                st.stop()

        # 3. Display Chat History
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # 4. User Input
        if prompt := st.chat_input("Ask me anything..."):
            # Show User Message
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Generate Response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Thinking...")
                
                try:
                    response = st.session_state.chat.send_message(prompt)
                    message_placeholder.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    message_placeholder.error(f"Error: {e}")

    except Exception as e:
        st.error(f"Connection Error: {e}")

else:
    st.info("👋 Shuru karne ke liye sidebar mein apni API Key dalein.")