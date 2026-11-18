import io
import urllib.parse
import requests
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from google import genai
from google.genai import types

st.set_page_config(page_title="Rionex - Dikembangkan oleh Rio Ferdian", page_icon="⚡", layout="centered")

st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
div[class*="viewerBadge"], div[data-testid="stStatusWidget"], [data-testid="manage-app-button"], .stAppDeployButton {display: none !important;}
[data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {display: none !important;}
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background-color: #F4F4F5 !important;
    color: #0F172A !important;
    border-radius: 20px !important;
    padding: 12px 18px !important;
    margin-left: auto !important;
    max-width: 80% !important;
    width: fit-content !important;
}
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background-color: transparent !important;
    color: #0F172A !important;
    padding: 8px 4px !important;
    max-width: 100% !important;
}
div[data-testid="stHorizontalBlock"] {flex-direction: row !important; flex-wrap: nowrap !important; align-items: center !important; gap: 8px !important;}
div[data-testid="stColumn"] {min-width: 0 !important;}
div[data-testid="stBottom"] div[data-testid="stColumn"]:nth-child(2) {flex: 0 0 46px !important; width: 46px !important; max-width: 46px !important;}
div[data-testid="stBottom"] [data-testid="stPopover"] > button {
    width: 44px !important; height: 44px !important; min-height: 44px !important; padding: 0 !important;
    border-radius: 50% !important; background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%) !important;
    border: none !important; box-shadow: 0 3px 10px rgba(37, 99, 235, 0.3) !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
    color: transparent !important; font-size: 0 !important; position: relative !important;
}
div[data-testid="stBottom"] [data-testid="stPopover"] > button p, div[data-testid="stBottom"] [data-testid="stPopover"] > button svg {display: none !important;}
div[data-testid="stBottom"] [data-testid="stPopover"] > button::after {
    content: "" !important; width: 22px !important; height: 22px !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://w3.org' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z'/%3E%3Ccircle cx='12' cy='13' r='3.5'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important; background-position: center !important; background-size: contain !important;
}
</style>
""", unsafe_allow_html=True)

IDENTITAS = "Kamu adalah Rionex, asisten AI generasi terbaru yang cerdas, ramah, dan membantu. Jika ada yang bertanya siapa namamu, jawablah Rionex. Jika ada yang bertanya siapa pencipta, pemilik, atau pengembangmu, jawablah dengan bangga bahwa kamu dikembangkan oleh Rio Ferdian. Jawablah selalu menggunakan bahasa Indonesia yang baik dan mudah dimengerti."

if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
if "chat" not in st.session_state:
    st.session_state.chat = st.session_state.client.chats.create(model="gemini-3.5-flash-lite", config=types.GenerateContentConfig(system_instruction=IDENTITAS, temperature=0.7))
if "messages" not in st.session_state:
    st.session_state.messages = []
if "upload_key" not in st.session_state:
    st.session_state.upload_key = 0

col_title, col_clear = st.columns([4, 1.3])
with col_title:
    st.markdown("#### **Rionex**")
with col_clear:
    if st.button("Reset", use_container_width=True):
        st.session_state.messages = []
        st.session_state.upload_key += 1
        st.session_state.chat = st.session_state.client.chats.create(model="gemini-3.5-flash-lite", config=types.GenerateContentConfig(system_instruction=IDENTITAS, temperature=0.7))
        st.rerun()

if len(st.session_state.messages) == 0:
    st.markdown("<br><br><h2 style='text-align: center; font-weight: 600;'>Halo, ada yang bisa Rionex bantu?</h2><p style='text-align: center; color: gray; font-size: 14px;'>Dikembangkan oleh Rio Ferdian</p>", unsafe_allow_html=True)

for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg.get("image") is not None:
            st.image(msg["image"], width=280)
            if msg["role"] == "assistant":
                buf = io.BytesIO()
                msg["image"].save(buf, format="PNG")
                st.download_button("⬇️ Unduh Gambar", data=buf.getvalue(), file_name=f"rionex_{idx}.png", mime="image/png", key=f"dl_{idx}")
        if msg.get("content"):
            st.markdown(msg["content"])

with st._bottom:
    col_input, col_cam = st.columns([6.5, 1])
    with col_input:
        prompt_data = st.chat_input("Tanya Rionex atau minta buatkan gambar...", accept_file=True, file_type=["jpg", "jpeg", "png", "webp"])
    with col_cam:
        with st.popover("📷", help="Kamera & Galeri"):
            st.markdown("**Pilih Sumber Foto**")
            foto_cam = st.file_uploader("📸 Ambil Foto (Kamera)", type=["jpg", "jpeg", "png", "webp"], key=f"cam_{st.session_state.upload_key}")
            foto_gal = st.file_uploader("🖼️ Pilih dari Galeri", type=["jpg", "jpeg", "png", "webp"], key=f"gal_{st.session_state.upload_key}")

components.html("<script>setInterval(()=>{document.querySelectorAll('[data-testid=\"stPopoverBody\"]').forEach(p=>{const i=p.querySelectorAll('input[type=\"file\"]');if(i.length>0&&!i.hasAttribute('capture'))i.setAttribute('capture','environment');});},800);</script>", height=0)

foto_menu = foto_cam if foto_cam is not None else foto_gal
if foto_menu is not None:
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 3.5, 1.2])
        c1.image(Image.open(foto_menu), width=55)
        c2.caption("Foto siap dikirim. Ketik pesan di bawah.")
        if c3.button("Batal"):
            st.session_state.upload_key += 1
            st.rerun()

if prompt_data:
    teks = prompt_data.text
    file_in = prompt_data.files if prompt_data.files else None
    gambar = Image.open(file_in) if file_in is not None else (Image.open(foto_menu) if foto_menu is not None else None)
    if not teks and gambar:
        teks = "Jelaskan isi gambar ini secara detail."

    with st.chat_message("user"):
        if gambar is not None:
            st.image(gambar, width=250)
        if teks:
            st.markdown(teks)
    st.session_state.messages.append({"role": "user", "content": teks, "image": gambar})

    kata_gambar = ["buatkan gambar", "buat gambar", "bikin gambar", "bikinkan gambar", "buatkan saya gambar", "buatin gambar", "gambarkan", "gambarin", "lukiskan", "buatkan foto", "bikin foto"]
    minta_gambar = gambar is None and any(k in teks.lower() for k in kata_gambar)

    with st.chat_message("assistant"):
        if minta_gambar:
            with st.spinner("Rionex sedang menggambar..."):
                try:
                    tr = st.session_state.client.models.generate_content(model="gemini-3.5-flash-lite", contents=f"Translate this image request into a short English visual prompt. Output ONLY the English prompt: {teks}")
                    url = f"https://pollinations.ai{urllib.parse.quote(tr.text.strip())}?width=768&height=768&nologo=true"
                    img_out = Image.open(io.BytesIO(requests.get(url, timeout=30).content))
                    st.image(img_out, width=280)
                    st.markdown("Ini gambar yang sudah Rionex buatkan untukmu!")
                    buf = io.BytesIO()
                    img_out.save(buf, format="PNG")
                    st.download_button("⬇️ Unduh Gambar", data=buf.getvalue(), file_name="rionex_image.png", mime="image/png", key=f"dl_now_{len(st.session_state.messages)}")
                    st.session_state.messages.append({"role": "assistant", "content": "Ini gambar yang sudah Rionex buatkan untukmu!", "image": img_out})
                except Exception as e:
                    st.error(f"Gagal membuat gambar: {e}")
        else:
            with st.spinner("Rionex sedang berpikir..."):
                try:
                    res = st.session_state.chat.send_message([gambar, teks] if gambar is not None else teks)
                    st.markdown(res.text)
                    st.session_state.messages.append({"role": "assistant", "content": res.text})
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
