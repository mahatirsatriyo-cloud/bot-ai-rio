import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from google import genai
from google.genai import types

# 1. Konfigurasi Halaman Web
st.set_page_config(page_title="Rionex - Dikembangkan oleh Rio Ferdian", page_icon="⚡", layout="centered")

# 2. CSS Kustom: Logo Kamera Keren & Tombol Kirim Selalu Terlihat
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

/* Gelembung pesan Pengguna (rata kanan seperti Meta AI / ChatGPT) */
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background-color: rgba(128, 128, 128, 0.15) !important;
    border-radius: 20px !important;
    padding: 12px 18px !important;
    margin-left: auto !important;
    max-width: 80% !important;
    width: fit-content !important;
}

/* Jawaban AI (bersih tanpa kotak kaku & tanpa avatar) */
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background-color: transparent !important;
    padding: 8px 4px !important;
    max-width: 100% !important;
}

/* Pastikan baris header & bar input bawah selalu sejajar rapi */
div[data-testid="stHorizontalBlock"] {
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: 10px !important;
}

div[data-testid="stColumn"] {
    min-width: 0 !important;
}

/* Kunci lebar kolom kamera agar tidak pernah menutupi tombol kirim */
div[data-testid="stBottom"] div[data-testid="stColumn"]:nth-child(2) {
    flex: 0 0 48px !important;
    width: 48px !important;
    max-width: 48px !important;
}

/* Sembunyikan daftar teks nama file agar tidak melebar ke samping */
div[data-testid="stBottom"] [data-testid="stFileUploader"] ul,
div[data-testid="stBottom"] [data-testid="stFileUploader"] li,
div[data-testid="stBottom"] [data-testid="stFileUploaderFile"],
div[data-testid="stBottom"] [data-testid="stFileUploader"] > label {
    display: none !important;
}

/* Jadikan kotak upload sebagai Tombol Bulat dengan Logo Kamera Keren */
div[data-testid="stBottom"] [data-testid="stFileUploaderDropzone"] {
    width: 46px !important;
    height: 46px !important;
    min-height: 46px !important;
    padding: 0 !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%) !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    position: relative !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}

div[data-testid="stBottom"] [data-testid="stFileUploaderDropzone"]:hover {
    transform: scale(1.08) !important;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25) !important;
}

/* Sembunyikan teks instruksi bawaan di dalam dropzone */
div[data-testid="stBottom"] [data-testid="stFileUploaderDropzone"] > div {
    opacity: 0 !important;
    width: 100% !important;
    height: 100% !important;
    position: absolute !important;
    inset: 0 !important;
}

/* Tampilkan Ikon Lensa Kamera Putih Tajam di tengah lingkaran */
div[data-testid="stBottom"] [data-testid="stFileUploaderDropzone"]::before {
    content: "" !important;
    width: 22px !important;
    height: 22px !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://w3.org' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z'/%3E%3Ccircle cx='12' cy='13' r='3.5'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    background-size: contain !important;
    pointer-events: none !important;
}
</style>
""", unsafe_allow_html=True)

# 3. Header Minimalis di Bagian Atas
col_title, col_clear = st.columns([4, 1.3])
with col_title:
    st.markdown("#### **Rionex**")
with col_clear:
    if st.button("Reset", use_container_width=True):
        st.session_state.messages = []
        st.session_state.cam_key += 1
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
if "cam_key" not in st.session_state:
    st.session_state.cam_key = 0

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

# 7. Bar Bawah: Kotak Ketik (+ Galeri) & Tombol Kamera Keren
with st._bottom:
    col_input, col_cam = st.columns([6.5, 1])
    with col_input:
        prompt_data = st.chat_input(
            "Tanya Rionex...",
            accept_file=True,
            file_type=["jpg", "jpeg", "png", "webp"]
        )
    with col_cam:
        foto_langsung = st.file_uploader(
            "Kamera",
            type=["jpg", "jpeg", "png", "webp"],
            key=f"cam_native_{st.session_state.cam_key}",
            label_visibility="collapsed"
        )

# Mengaktifkan kamera belakang HP secara langsung saat tombol kamera ditekan
components.html("""
<script>
const setNativeCamera = () => {
    const inputs = window.parent.document.querySelectorAll('div[data-testid="stBottom"] input[type="file"]');
    inputs.forEach(input => {
        if (!input.hasAttribute('capture')) {
            input.setAttribute('capture', 'environment');
        }
    });
};
setNativeCamera();
setInterval(setNativeCamera, 1000);
</script>
""", height=0)

# Pratinjau mini rapi di atas kotak ketik jika foto sudah dijepret dari kamera HP
if foto_langsung is not None:
    gambar_preview = Image.open(foto_langsung)
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 3.5, 1.2])
        with c1:
            st.image(gambar_preview, width=55)
        with c2:
            st.caption("Foto siap dikirim. Ketik pertanyaan di bawah.")
        with c3:
            if st.button("Batal"):
                st.session_state.cam_key += 1
                st.rerun()

# 8. Proses Pengiriman Pesan
if prompt_data:
    teks_pesan = prompt_data.text
    file_galeri = prompt_data.files if prompt_data.files else None

    gambar_terpilih = None
    if file_galeri is not None:
        gambar_terpilih = Image.open(file_galeri)
    elif foto_langsung is not None:
        gambar_terpilih = Image.open(foto_langsung)
        st.session_state.cam_key += 1

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
                if foto_langsung is not None:
                    st.rerun()
            except Exception as e:
