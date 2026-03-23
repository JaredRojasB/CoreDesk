import streamlit as st
import google.generativeai as genai
import os
import time
from PIL import Image

# IMPORTACIÓN DE TUS MÓDULOS LIMPIOS
import global_styles
import auth_styles
import chat_styles

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CoreDesk Support", page_icon="🛡️", layout="wide")

# Aplicamos los estilos base (Blanco y limpieza de iconos basura)
global_styles.aplicar_globales()

# Configuración IA
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None
if "bienvenida_dada" not in st.session_state: st.session_state.bienvenida_dada = False

# Carga de Logo
try:
    logo_img = Image.open("logo.png")
except:
    logo_img = None

# --- LÓGICA DE NAVEGACIÓN ---

if st.session_state.user_data is None:
    # PANTALLA DE REGISTRO
    auth_styles.aplicar_auth()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_img: st.image(logo_img, use_container_width=True)
        st.markdown("<h1 style='text-align:center; color:#0E3255; font-size:50px;'>CoreDesk</h1>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.subheader("📝 Apertura de Ticket")
            nombre = st.text_input("Nombre Completo:")
            empresa = st.text_input("Empresa / Departamento:")
            correo = st.text_input("Correo Electrónico:")
            
            if st.form_submit_button("INICIAR SOPORTE"):
                if nombre and empresa and "@" in correo:
                    st.session_state.user_data = {
                        "nombre": nombre, 
                        "empresa": empresa, 
                        "inicio": time.time()
                    }
                    st.rerun()
                else:
                    st.error("❌ Completa todos los campos.")

else:
    # PANTALLA DE CHAT ACTIVA
    chat_styles.aplicar_chat()
    
    # 1. Header Fijo (Logo Izq | Contador Der)
    t_min = int((time.time() - st.session_state.user_data['inicio']) / 60)
    st.markdown(f"""
        <div class="header-fixed" style="display:flex; justify-content:space-between; align-items:center; padding:0 5%; background:white; height:70px; box-shadow:0 2px 5px rgba(0,0,0,0.05); position:fixed; top:0; left:0; width:100%; z-index:1000;">
            <div style="font-weight:bold; color:#0E3255; font-size:22px;">🛡️ CoreDesk Support</div>
            <div style="color:#6c757d; font-weight:bold;">⏱️ Activo: {t_min} min</div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Tarjeta de Usuario Formal
    st.markdown(f"""
        <div class="user-card-pro" style="background:white; padding:15px; border-radius:10px; border-left:6px solid #0E3255; box-shadow:0 4px 10px rgba(0,0,0,0.05); margin-top:20px;">
            <span style="color:#6c757d; font-size:12px;">SOPORTE TÉCNICO ACTIVO</span><br>
            👤 <b>{st.session_state.user_data['nombre']}</b> | 🏢 {st.session_state.user_data['empresa']}
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 3. Bienvenida Única de la IA
    if not st.session_state.bienvenida_dada:
        with st.chat_message("assistant"):
            msg = f"¡Hola **{st.session_state.user_data['nombre']}**! Soy tu Asistente IA de CoreDesk. ¿En qué puedo ayudarte hoy con el equipo de **{st.session_state.user_data['empresa']}**?"
            st.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.session_state.bienvenida_dada = True

    # 4. Historial de Chat
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # 5. Entrada de Chat con el '+' (Clip)
    c_clip, c_txt = st.columns([1, 15])
    with c_clip:
        with st.popover("📎"):
            st.button("📷 Subir Imagen", disabled=True)
    
    with c_txt:
        if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("CoreDesk AI analizando..."):
                    try:
                        usr = st.session_state.user_data['nombre']
                        # PROMPT ESPECÍFICO Y PROCEDIMENTAL
                        ctx = f"Eres Soporte CoreDesk. Guía paso a paso a {usr}. Sé extremadamente específico (ej: Abre Win+R, escribe 'temp'). Pregunta al final si funcionó."
                        res = model.start_chat(history=[]).send_message(f"{ctx}\n{prompt}").text
                        st.markdown(res)
                        st.session_state.messages.append({"role": "assistant", "content": res})
                    except Exception as e:
                        st.error(f"Error de red: {e}")
            st.rerun()

    # 6. BOTÓN X FLOTANTE (HTML Real)
    # El target="_self" asegura que recargue la página al inicio
    st.markdown('<a href="/" target="_self" id="finalizar-link">×</a>', unsafe_allow_html=True)