import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

# 1. Konfigurasi Halaman Web
st.set_page_config(page_title="Rionex - Dikembangkan oleh Rio Ferdian", page_icon="⚡", layout="centered")

# 2. CSS Kustom untuk Tampilan Modern Tanpa Avatar Kartun
st.markdown("""
<style>
/* Sembunyikan menu & footer bawaan Streamlit */
#MainMenu, footer, header {visibility: hidden;}

/* Hilangkan total ikon avatar robot & wajah pengguna */
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"],
[data-testid="chatAvatarIcon-user"],
[data-testid="chatAvatarIcon-assistant"] {
    display: none !important;
}

/* Gaya gelembung pesan Pengguna (rata kanan, sudut membulat seperti ChatGPT) */
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background-color: rgba(128, 128, 128, 0.15) !important;
    border-radius: 20px !important;
    padding: 12px 18px !important;
    margin-left: auto !important;
    max-width: 80% !important;
    width: fit-content !important;
}

/* Gaya jawaban AI (bersih tanpa kotak kaku & tanpa logo) */
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background-color: transparent !important;
    padding: 8px 4px !important;
    max-width: 100% !important;
}

/* Pastikan baris header & bar input bawah selalu sejajar rapi di HP maupun Laptop */
div[data-testid="stHorizontalBlock"] {
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: 8px !important;
}

div[data-testid="stColumn"] {
    min-width: 0 !important;
}

/* Tombol kamera bulat minimalis di samping kotak ketik */
div[data-testid="stBottom"] button[kind="secondary"] {
    border-radius: 50% !important;
    width: 44px !important;
    height: 44px !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    border: 1px solid rgba(128, 128, 128, 0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# 3. Header Minimalis di Bagian Atas
col_title, col_clear = st.columns([4, 1.2])
with col_title:
    st.markdown("#### **Rionex**")
with col_clear:
    if st.button("Reset", use_container_width=True):
        st.session_state.messages = []
        st.session_state.buka_kamera = False
        st.session_state.foto_kamera = None
        if "client" in st.session_state:
            st.session_state.chat = st.session_state.client.chats.create(
                model="gemini-3.5-flash-lite",
                config=types.GenerateContentConfig(
                    system_instruction="""
                    Kamu adalah Rionex, asisten AI generasi terbaru yang cerdas, ramah, dan membantu.
                    Jika ada yang bertanya siapa namamu, jawablah Rionex.
                    Jika ada yang bertanya siapa pencipta, pemilik, atau pengembangmu, jawablah dengan bangga bahwa kamu dikembangkan oleh Rio Ferdian.
                    Jawablah selalu menggunakan bahasa Indonesia yang baik dan mudah dimengerti.
                    """,
                    temperature=0.7,
                )
            )
        st.rerun()

# 4. Inisialisasi API Key & Sesi Obrolan
API_KEY = st.secrets["GEMINI_API_KEY"]

identitas_bot = """
Kamu adalah Rionex, asisten AI generasi terbaru yang cerdas, ramah, dan membantu.
Jika ada yang bertanya siapa namamu, jawablah Rionex.
Jika ada yang bertanya siapa pencipta, pemilik, atau pengembangmu, jawablah dengan bangga bahwa kamu dikembangkan oleh Rio Ferdian.
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

# 5. Layar Sambutan Bersih Saat Belum Ada Chat
if len(st.session_state.messages) == 0:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; font-weight: 600;'>Halo, ada yang bisa Rionex bantu?</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; font-size: 14px;'>Dikembangkan oleh Rio Ferdian</p>", unsafe_allow_html=True)

# 6. Menampilkan Riwayat Obrolan Tanpa Avatar
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image" in message and message["image"] is not None:
            st.image(message["image"], width=240)
        st.markdown(message["content"])

# 7. Jendela Kamera (Hanya terbuka saat ikon kamera diklik)
if st.session_state.buka_kamera:
    with st.container(border=True):
        c_cam1, c_cam2 = st.columns([4, 1])
        with c_cam1:
            st.markdown("**Ambil Foto**")
        with c_cam2:
            if st.button("✕"):
                st.session_state.buka_kamera = False
                st.rerun()
        
        jepretan = st.camera_input("Kamera", label_visibility="collapsed")
        if jepretan is not None:
            st.session_state.foto_kamera = Image.open(jepretan)
            st.session_state.buka_kamera = False
            st.rerun()

# Pratinjau mini jika foto dari kamera sudah siap dikirim
if st.session_state.foto_kamera is not None:
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 3.5, 1])
        with c1:
            st.image(st.session_state.foto_kamera, width=55)
        with c2:
            st.caption("Foto siap dikirim. Ketik pesan di bawah.")
        with c3:
            if st.button("Batal"):
                st.session_state.foto_kamera = None
                st.rerun()

# 8. Bar Ketik Pesan Bawah + Tombol Kamera Sejajar
with st._bottom:
    col_input, col_cam = st.columns([6.5, 1])
    with col_input:
        prompt_data = st.chat_input(
            "Tanya Rionex...",
            accept_file=True,
            file_type=["jpg", "jpeg", "png", "webp"]
        )
    with col_cam:
        if st.button("📷", help="Ambil foto dari kamera"):
            st.session_state.buka_kamera = not st.session_state.buka_kamera
            st.rerun()

# 9. Proses Pengiriman Pesan
if prompt_data:
    teks_pesan = prompt_data.text
    file_galeri = prompt_data.files[0] if prompt_data.files else None

    gambar_terpilih = None
    if file_galeri is not None:
        gambar_terpilih = Image.open(file_galeri)
    elif st.session_state.foto_kamera is not None:
        gambar_terpilih = st.session_state.foto_kamera
        st.session_state.foto_kamera = None

    if not teks_pesan and gambar_terpilih:
        teks_pesan = "Jelaskan isi gambar ini secara detail."

    with st.chat_message("user"):
        if gambar_terpilih is not None:
            st.image(gambar_terpilih, width=240)
        if teks_pesan:
            st.markdown(teks_pesan)

    st.session_state.messages.append({
        "role": "user",
        "content": teks_pesan,
        "image": gambar_terpilih
    })

    isi_pesan = [gambar_terpilih, teks_pesan] if gambar_terpilih is not None else teks_pesan

    with st.chat_message("assistant"):
        with st.spinner("Rionex sedang berpikir..."):
            try:
                response = st.session_state.chat.send_message(isi_pesan)
                st.markdown(response.text)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.text
                })
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
