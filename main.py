import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

# 1. Konfigurasi Halaman Web
st.set_page_config(page_title="AI Bot - Rio Ferdian", page_icon="🤖")

# Header dan tombol hapus chat di bagian atas
kolom_judul, kolom_tombol = st.columns([4, 1])
with kolom_judul:
    st.title("🤖 Asisten AI Pintar")
    st.caption("Diciptakan oleh Rio Ferdian")
with kolom_tombol:
    st.write("")
    if st.button("🗑️ Hapus"):
        st.session_state.messages = []
        if "client" in st.session_state:
            st.session_state.chat = st.session_state.client.chats.create(
                model="gemini-3.5-flash-lite",
                config=types.GenerateContentConfig(
                    system_instruction="""
                    Kamu adalah asisten AI yang cerdas, ramah, dan membantu.
                    Jika ada yang bertanya siapa penciptamu, pemilikmu, atau siapa yang membuatmu, jawablah dengan bangga bahwa penciptamu adalah Rio Ferdian.
                    Jawablah selalu menggunakan bahasa Indonesia yang baik dan mudah dimengerti.
                    """,
                    temperature=0.7,
                )
            )
        st.rerun()

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

# 4. Menampilkan Riwayat Obrolan
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image" in message and message["image"] is not None:
            st.image(message["image"], width=250)
        st.markdown(message["content"])

# 5. Kolom Ketik Pesan dengan Tombol Lampirkan Foto Langsung di Dalamnya
prompt_data = st.chat_input(
    "Ketik pertanyaan atau lampirkan foto...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp"]
)

if prompt_data:
    teks_pesan = prompt_data.text
    file_foto = prompt_data.files[0] if prompt_data.files else None
    gambar_terpilih = Image.open(file_foto) if file_foto else None

    # Jika pengguna mengirim foto tanpa mengetik teks, beri perintah bawaan
    if not teks_pesan and gambar_terpilih:
        teks_pesan = "Jelaskan isi gambar ini secara detail."

    # Tampilkan pesan dan foto pengguna di layar
    with st.chat_message("user"):
        if gambar_terpilih is not None:
            st.image(gambar_terpilih, width=250)
        if teks_pesan:
            st.markdown(teks_pesan)

    st.session_state.messages.append({
        "role": "user",
        "content": teks_pesan,
        "image": gambar_terpilih
    })

    # Siapkan isi pesan untuk dikirim ke AI
    isi_pesan = [gambar_terpilih, teks_pesan] if gambar_terpilih is not None else teks_pesan

    # Kirim ke AI dan tampilkan balasannya
    with st.chat_message("assistant"):
        with st.spinner("Sedang berpikir..."):
            try:
                response = st.session_state.chat.send_message(isi_pesan)
                st.markdown(response.text)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.text
                })
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
