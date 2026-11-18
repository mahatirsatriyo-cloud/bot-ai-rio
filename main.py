import io
import urllib.parse
import requests
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from google import genai
from google.genai import types

# 1. Konfigurasi Halaman Web
st.set_page_config(page_title="Rionex - Dikembangkan oleh Rio Ferdian", page_icon="⚡", layout="centered")

# 2. CSS Kustom: Tema Putih Bersih & Tata Letak Chat Modern
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
div[class*="viewerBadge"],
div[data-testid="stStatusWidget"],
[data-testid="manage-app-button"],
.stAppDeployButton {
    display: none !important;
}

/* Sembunyikan ikon avatar bulat saja tanpa menyembunyikan isi pesan */
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {
    display: none !important;
}

/* Gelembung pesan Pengguna (rata kanan) */
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background-color: #F4F4F5 !important;
    color: #0F172A !important;
    border-radius: 20px !important;
    padding: 12px 18px !important;
    margin-left: auto !important;
    max-width: 80% !important;
    width: fit-content !important;
}

/* Jawaban AI (tampil penuh dan jelas di kiri) */
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background-color: transparent !important;
    color: #0F172A !important;
    padding: 8px 4px !important;
    max-width: 100% !important;
}

/* Pastikan baris header & bar input bawah selalu sejajar rapi */
div[data-testid="stHorizontalBlock"] {
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: 8px !important;
}

div[data-testid="stColumn"] {
    min-width: 0 !important;
}

/* Kunci ukuran kolom tombol kamera di bar bawah */
div[data-testid="stBottom"] div[data-testid="stColumn"]:nth-child(2) {
    flex: 0 0 46px !important;
    width: 46px !important;
    max-width: 46px !important;
}

/* Tombol Bulat Kamera Biru Modern */
div[data-testid="stBottom"] [data-testid="stPopover"] > button {
    width: 44px !important;
    height: 44px !important;
    min-height: 44px !important;
    padding: 0 !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%) !important;
    border: none !important;
    box-shadow: 0 3px 10px rgba(37, 99, 235, 0.3) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    color: transparent !important;
    font-size: 0 !important;
    position: relative !important;
}

div[data-testid="stBottom"] [data-testid="stPopover"] > button p,
div[data-testid="stBottom"] [data-testid="stPopover"] > button svg {
    display: none !important;
}

div[data-testid="stBottom"] [data-testid="stPopover"] > button::after {
    content: "" !important;
    width: 22px !important;
    height: 22px !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://w3.org' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z'/%3E%3Ccircle cx='12' cy='13' r='3.5'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    background-size: contain !important;
}
</style>
""", unsafe_allow_html=True)

# 3. Header Minimalis
col_title, col_clear = st.columns([4, 1.3])
with col_title:
    st.markdown("#### **Rionex**")
with col_clear:
    if st.button("Reset", use_container_width=True):
        st.session_state.messages = []
        st.session_state.upload_key += 1
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
if "upload_key" not in st.session_state:
    st.session_state.upload_key = 0

def cek_permintaan_gambar(teks):
    kata_kunci = [
        "buatkan gambar", "buat gambar", "bikin gambar", "bikinkan gambar",
        "buatkan saya gambar", "buatin gambar", "gambarkan", "gambarin",
        "lukiskan", "generate image", "create image", "buatkan foto", "bikin foto"
    ]
    teks_kecil = teks.lower()
    return any(kata in teks_kecil for kata in kata_kunci)

# 5. Layar Sambutan Bersih
if len(st.session_state.messages) == 0:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; font-weight: 600;'>Halo, ada yang bisa Rionex bantu?</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; font-size: 14px;'>Dikembangkan oleh Rio Ferdian</p>", unsafe_allow_html=True)

# 6. Menampilkan Riwayat Obrolan Sebelumnya
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        if "image" in message and message["image"] is not None:
            st.image(message["image"], width=280)
            if message["role"] == "assistant":
                buf = io.BytesIO()
                message["image"].save(buf, format="PNG")
                st.download_button(
                    label="⬇️ Unduh Gambar",
                    data=buf.getvalue(),
                    file_name=f"rionex_image_{idx}.png",
                    mime="image/png",
                    key=f"dl_btn_{idx}"
                )
        if message["content"]:
            st.markdown(message["content"])

# 7. Bar Bawah: Kotak Ketik & Tombol Kamera dengan Pilihan
foto_kamera = None
foto_galeri_menu = None

with st._bottom:
    col_input, col_cam = st.columns([6.5, 1])
    with col_input:
        prompt_data = st.chat_input(
            "Tanya Rionex atau minta buatkan gambar...",
            accept_file=True,
            file_type=["jpg", "jpeg", "png", "webp"]
        )
    with col_cam:
        with st.popover("📷", help="Kamera & Galeri"):
            st.markdown("**Pilih Sumber Foto**")
            foto_kamera = st.file_uploader(
                "📸 Ambil Foto (Kamera)",
                type=["jpg", "jpeg", "png", "webp"],
                key=f"cam_{st.session_state.upload_key}"
            )
            foto_galeri_menu = st.file_uploader(
                "🖼️ Pilih dari Galeri",
                type=["jpg", "jpeg", "png", "webp"],
                key=f"gal_{st.session_state.upload_key}"
            )

components.html("""
<script>
const setCameraOnly = () => {
    const popovers = window.parent.document.querySelectorAll('[data-testid="stPopoverBody"]');
    popovers.forEach(pop => {
        const inputs = pop.querySelectorAll('input[type="file"]');
        if (inputs.length > 0 && !inputs.hasAttribute('capture')) {
            inputs.setAttribute('capture', 'environment');
        }
    });
};
setCameraOnly();
setInterval(setCameraOnly, 800);
</script>
""", height=0)

foto_dari_menu = foto_kamera if foto_kamera is not None else foto_galeri_menu

if foto_dari_menu is not None:
    gambar_preview = Image.open(foto_dari_menu)
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 3.5, 1.2])
        with c1:
            st.image(gambar_preview, width=55)
        with c2:
            st.caption("Foto siap dikirim. Ketik pesan di bawah.")
        with c3:
            if st.button("Batal"):
                st.session_state.upload_key += 1
                st.rerun()

# 8. Proses Pengiriman Pesan & Tampilkan Langsung Tanpa Memutus Layar
if prompt_data:
    teks_pesan = prompt_data.text
    file_chat_input = prompt_data.files if prompt_data.files else None

    gambar_terpilih = None
    if file_chat_input is not None:
        gambar_terpilih = Image.open(file_chat_input)
    elif foto_dari_menu is not None:
        gambar_terpilih = Image.open(foto_dari_menu)

    if not teks_pesan and gambar_terpilih:
        teks_pesan = "Jelaskan isi gambar ini secara detail."

    # Tampilkan pesan pengguna langsung
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

    # Tampilkan balasan AI langsung di bawahnya
    with st.chat_message("assistant"):
