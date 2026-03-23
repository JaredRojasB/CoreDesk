import streamlit as st
import google.generativeai as genai
import os, time
from PIL import Image

# IMPORTAMOS TUS ARCHIVOS RESPETANDO LOS NOMBRES
import auth_styles
import chat_styles
import auth

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support", layout="wide")

# IA Setup
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None

try: logo_img = Image.open("logo.png")
except: logo_img = None

# --- NAVEGACIÓN ---

if st.session_state.user_data is None:
    # APLICAR ESTILOS DE REGISTRO
    auth_styles.aplicar_auth()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_img: st.image(logo_img, use_container_width=True)
        st.markdown("<h1 class='core-title-auth'>CoreDesk</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            st.subheader("📝 Apertura de Ticket")
            nombre = st.text_input("Nombre Completo:")
            empresa = st.text_input("Empresa / Departamento:")
            correo = st.text_input("Correo Electrónico:")
            
            if st.form_submit_button("INICIAR SOPORTE"):
                if nombre and empresa and "@" in correo:
                    st.session_state.user_data = {
                        "nombre": nombre, "empresa": empresa, 
                        "inicio": time.time()
                    }
                    st.rerun()
                else: st.error("❌ Datos incompletos")

else:
    # APLICAR ESTILOS DE CHAT
    chat_styles.aplicar_chat()
    
    # 1. Header Fijo (HTML)
    t_min = int((time.time() - st.session_state.user_data['inicio']) / 60)
    st.markdown(f"""
        <div class="header-fixed">
            <div style="font-weight:bold; color:#0E3255; font-size:22px;">🛡️ CoreDesk Support</div>
            <div style="color:#6c757d; font-weight:bold;">⏱️ Activo: {t_min} min</div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Tarjeta Usuario
    st.markdown(f"""
        <div class="user-card">
            <span style="color:#6c757d; font-size:12px;">INFORMACIÓN DEL TICKET</span>
            <hr style="margin:8px 0; border:0; border-top:1px solid #EEE;">
            👤 <b>{st.session_state.user_data['nombre']}</b> | 🏢 {st.session_state.user_data['empresa']}
        </div>
    """, unsafe_allow_html=True)

    # 3. Bienvenida (Solo una vez)
    if not st.session_state.messages:
        bienvenida = f"¡Hola **{st.session_state.user_data['nombre']}**! Soy tu Asistente IA de CoreDesk. ¿En qué puedo ayudarte hoy en **{st.session_state.user_data['empresa']}**?"
        st.session_state.messages.append({"role": "assistant", "content": bienvenida})

    # 4. Historial
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # 5. Entrada de Chat con Popover (Clip)
    c_clip, c_txt = st.columns([1, 15])
    with c_clip:
        with st.popover("📎"):
            st.button("📷 Subir Imagen", disabled=True)

    if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("CoreDesk AI analizando..."):
                ctx = f"Eres Soporte CoreDesk. Guía paso a paso a {st.session_state.user_data['nombre']}. Sé procedimental (ej. Win+R, Ctrl+K). Pregunta al final si funcionó."
                res = model.start_chat(history=[]).send_message(f"{ctx}\n{prompt}").text
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})
        st.rerun()

    # 6. Botón X Flotante (Enlace de salida)
    st.markdown('<a href="/" target="_self" id="btn-exit">×</a>', unsafe_allow_html=True)