import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="AI Bot - Rio Ferdian", page_icon="🤖")
st.title("🤖 Asisten AI Pintar")
st.caption("Diciptakan oleh Rio Ferdian")

# Mengambil API Key secara aman dari brankas Streamlit Cloud
API_KEY = st.secrets["GEMINI_API_KEY"]

identitas_bot = """
Kamu adalah asisten AI yang cerdas, ramah, dan membantu.
Jika ada yang bertanya siapa penciptamu, pemilikmu, atau siapa yang membuatmu, jawablah dengan bangga bahwa penciptamu adalah Rio Ferdian.
Jawablah selalu menggunakan bahasa Indonesia yang baik dan mudah dimengerti.
"""

if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=API_KEY)

if "chat" not in st.session_state:
    st.session_state.chat = st.session_state.client.chats.create(
        model="gemini-3.5-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=identitas_bot,
            temperature=0.7,
        )
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ketik pertanyaan Anda di sini..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Sedang berpikir..."):
            try:
                response = st.session_state.chat.send_message(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")