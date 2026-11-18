import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

# 1. Konfigurasi Halaman Web
st.set_page_config(page_title="AI Bot - Rio Ferdian", page_icon="🤖", layout="centered")

# 2. CSS Kustom agar Tampilan Rapi Persis seperti ChatGPT di HP
st.markdown("""
<style>
/* Menyembunyikan menu bawaan atas & footer Streamlit agar bersih */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Membuat tombol di bar bawah tetap sejajar menyamping di layar HP */
div[data-testid="stHorizontalBlock"] {
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: 8px !important;
}

div[data-testid="stColumn"] {
    min-width: 0 !important;
}

/* Merapikan tombol kamera agar bulat & pas di samping kotak chat */
div[data-testid="stColumn"]:nth-child(2) button {
    border-radius: 50% !important;
    width: 46px !important;
    height: 46px !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background-color: #262730 !important;
    border: 1px solid #41444C !important;
    font-size: 20px !important;
}
</style>
""", unsafe_allow_html=True)

# 3. Header Bersih Sejajar (Judul di Kiri, Tombol Hapus di Kanan)
col_title, col_clear = st.columns([4, 1.3])
with col_title:
    st.markdown("### 🤖 Asisten AI Pintar")
    st.caption("Diciptakan oleh Rio Ferdian")
with col_clear:
    if st.button("🗑️ Hapus", use_container_width=True):
        st.session_state.messages = []
        st.session_state.buka_kamera = False
        st.session_state.foto_kamera = None
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

st.divider()

# 4. Inisialisasi API Key & Memori Chat
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
if "buka_kamera" not in st.session_state:
    st.session_state.buka_kamera = False
if "foto_kamera" not in st.session_state:
    st.session_state.foto_kamera = None

# 5. Menampilkan Riwayat Obrolan
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image" in message and message["image"] is not None:
            st.image(message["image"], width=250)
        st.markdown(message["content"])

# 6. Jendela Kamera (Hanya muncul saat tombol 📷 diklik)
if st.session_state.buka_kamera:
    with st.container(border=True):
        col_cam_title, col_cam_close = st.columns([4, 1])
        with col_cam_title:
            st.markdown("**📸 Ambil Foto Langsung**")
        with col_cam_close:
            if st.button("✖️"):
                st.session_state.buka_kamera = False
                st.rerun()
        
        jepretan = st.camera_input("Arahkan kamera lalu jepret", label_visibility="collapsed")
        if jepretan is not None:
            st.session_state.foto_kamera = Image.open(jepretan)
            st.session_state.buka_kamera = False
            st.rerun()

# Pratinjau mini jika foto kamera sudah diambil dan siap dikirim
if st.session_state.foto_kamera is not None:
    with st.container(border=True):
        c1, c2, c3 = st.columns([1.2, 3, 1])
        with c1:
            st.image(st.session_state.foto_kamera, width=60)
        with c2:
            st.caption("✅ Foto kamera siap dikirim! Ketik pesan di bawah lalu kirim.")
        with c3:
            if st.button("Batal"):
                st.session_state.foto_kamera = None
                st.rerun()

# 7. Bar Bawah Melayang: Kotak Ketik (+ Galeri) Sejajar dengan Tombol Kamera 📷
with st._bottom:
    col_input, col_cam_btn = st.columns([6, 1])
    with col_input:
        prompt_data = st.chat_input(
            "Tanya apa saja...",
            accept_file=True,
            file_type=["jpg", "jpeg", "png", "webp"]
        )
    with col_cam_btn:
        if st.button("📷", help="Buka Kamera"):
            st.session_state.buka_kamera = not st.session_state.buka_kamera
            st.rerun()

# 8. Proses Pengiriman Pesan & Gambar
if prompt_data:
    teks_pesan = prompt_data.text
    file_galeri = prompt_data.files[0] if prompt_data.files else None

    gambar_terpilih = None
    if file_galeri is not None:
        gambar_terpilih = Image.open(file_galeri)
    elif st.session_state.foto_kamera is not None:
        gambar_terpilih = st.session_state.foto_kamera
        st.session_state.foto_kamera = None  # Reset setelah terkirim

    if not teks_pesan and gambar_terpilih:
        teks_pesan = "Jelaskan isi gambar ini secara detail."

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

    isi_pesan = [gambar_terpilih, teks_pesan] if gambar_terpilih is not None else teks_pesan

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
