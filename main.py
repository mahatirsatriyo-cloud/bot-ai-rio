import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

# 1. Konfigurasi Halaman Web
st.set_page_config(page_title="AI Bot - Rio Ferdian", page_icon="🤖")
st.title("🤖 Asisten AI Pintar")
st.caption("Diciptakan oleh Rio Ferdian")

# 2. Mengambil API Key secara aman dari Secrets Streamlit
API_KEY = st.secrets["GEMINI_API_KEY"]

identitas_bot = """
Kamu adalah asisten AI yang cerdas, ramah, dan membantu.
Jika ada yang bertanya siapa penciptamu, pemilikmu, atau siapa yang membuatmu, jawablah dengan bangga bahwa penciptamu adalah Rio Ferdian.
Jawablah selalu menggunakan bahasa Indonesia yang baik dan mudah dimengerti.
"""

# 3. Simpan Client dan Sesi Obrolan di Memori Web
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

# 4. Panel Samping (Sidebar) untuk Unggah Foto & Hapus Chat
with st.sidebar:
    st.header("📸 Kirim Foto ke Bot")
    uploaded_file = st.file_uploader("Pilih gambar (JPG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"])
    
    gambar_terpilih = None
    if uploaded_file is not None:
        gambar_terpilih = Image.open(uploaded_file)
        st.image(gambar_terpilih, caption="Foto siap dikirim", use_container_width=True)
        st.info("Ketik pertanyaan tentang foto ini di kolom chat.")

    st.divider()
    if st.button("🗑️ Hapus Riwayat Obrolan"):
        st.session_state.messages = []
        st.session_state.chat = st.session_state.client.chats.create(
            model="gemini-3.5-flash-lite",
            config=types.GenerateContentConfig(
                system_instruction=identitas_bot,
                temperature=0.7,
            )
        )
        st.rerun()

# 5. Menampilkan Riwayat Obrolan
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image" in message and message["image"] is not None:
            st.image(message["image"], width=250)
        st.markdown(message["content"])

# 6. Kolom Ketik Pesan Baru
if prompt := st.chat_input("Ketik pertanyaan Anda di sini..."):
    # Tampilkan pesan dan gambar pengguna di layar
    with st.chat_message("user"):
        if gambar_terpilih is not None:
            st.image(gambar_terpilih, width=250)
        st.markdown(prompt)
        
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt, 
        "image": gambar_terpilih
    })

    # Siapkan isi pesan (gabungkan teks dan foto jika ada)
    isi_pesan = [gambar_terpilih, prompt] if gambar_terpilih is not None else prompt

    # Kirim ke AI dan tampilkan balasannya
    with st.chat_message("assistant"):
        with st.spinner("Sedang menganalisis..."):
            try:
                response = st.session_state.chat.send_message(isi_pesan)
                st.markdown(response.text)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response.text
                })
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
