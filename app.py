import streamlit as st
import google.generativeai as genai
import os
import time
import pandas as pd
from PIL import Image

# IMPORTAMOS TUS ESTILOS (Asegúrate de que existan estos archivos)
import global_styles
import auth_styles
import chat_styles

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support", page_icon="🛡️", layout="wide")
global_styles.aplicar_globales()

# IA Setup
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Session State (Variables críticas)
if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None
if "chat_iniciado" not in st.session_state: st.session_state.chat_iniciado = False

# Carga de Logo
try:
    logo_img = Image.open("logo.png")
except:
    logo_img = None

# --- 2. LÓGICA DE NAVEGACIÓN ---

if not st.session_state.chat_iniciado:
    # --- PANTALLA DE REGISTRO ---
    auth_styles.aplicar_auth()
    
    col_inic1, col_inic2, col_inic3 = st.columns([1, 2, 1])
    with col_inic2:
        if logo_img: st.image(logo_img, use_container_width=True)
        st.markdown("<p class='core-title-main' style='color:#0E3255; text-align:center; font-size:50px; font-weight:bold;'>CoreDesk</p>", unsafe_allow_html=True)
        
        with st.form("registro_ticket"):
            st.subheader("📝 Apertura de Ticket")
            nombre = st.text_input("Nombre Completo:")
            empresa = st.text_input("Empresa / Departamento:")
            correo = st.text_input("Correo Electrónico:")
            submit = st.form_submit_button("INICIAR SOPORTE")
            
            if submit:
                if nombre and empresa and "@" in correo:
                    # GUARDAMOS TODO ANTES DE REINICIAR
                    st.session_state.user_data = {
                        "nombre": nombre, 
                        "empresa": empresa, 
                        "correo": correo,
                        "inicio_time": time.time()
                    }
                    st.session_state.chat_iniciado = True
                    st.rerun()
                else:
                    st.error("❌ Por favor, llena los datos correctamente.")

else:
    # --- PANTALLA DE CHAT ACTIVA ---
    chat_styles.aplicar_chat()
    
    # Header con Logo
    head_l, head_r = st.columns([8, 1])
    with head_l:
        if logo_img: st.image(logo_img, width=120)
    
    # Tarjeta de Usuario con Contador
    tiempo_transcurrido = int((time.time() - st.session_state.user_data['inicio_time']) / 60)
    st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.05); border-left: 5px solid #0E3255; display: flex; justify-content: space-between;">
            <div>👤 <b>{st.session_state.user_data['nombre']}</b> | 🏢 {st.session_state.user_data['empresa']}</div>
            <div style="color: #6c757d;">⏱️ Activo: {tiempo_transcurrido} min</div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Bienvenida Única
    if len(st.session_state.messages) == 0:
        msg_inicio = f"Hola **{st.session_state.user_data['nombre']}**, soy tu Asistente de CoreDesk. ¿Cuál es el problema en **{st.session_state.user_data['empresa']}**?"
        st.session_state.messages.append({"role": "assistant", "content": msg_inicio})

    # Historial
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # Input con el '+' integrado (Usando columnas pegadas)
    c_clip, c_txt = st.columns([1, 15])
    with c_clip:
        with st.popover("📎"):
            st.button("📷 Imagen", disabled=True)
    
    with c_txt:
        if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun() # Forzamos recarga para mostrar mensaje del usuario

    # Lógica de respuesta IA (Si el último mensaje es del usuario)
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            with st.spinner("CoreDesk AI analizando..."):
                try:
                    usr_nombre = st.session_state.user_data['nombre']
                    prompt_actual = st.session_state.messages[-1]["content"]
                    
                    sys_prompt = f"Eres Soporte CoreDesk. Guía paso a paso a {usr_nombre}. Sé procedimental (ej. Win+R, Ctrl+C). Pregunta al final si funcionó."
                    res = model.start_chat(history=[]).send_message(f"{sys_prompt}\n{prompt_actual}").text
                    
                    st.markdown(res)
                    st.session_state.messages.append({"role": "assistant", "content": res})
                except Exception as e:
                    st.error(f"Error: {e}")

    # Botón Flotante de Finalizar (X Roja)
    st.markdown("""
        <a href="/" target="_self" style="position: fixed; bottom: 40px; left: 40px; width: 60px; height: 60px; background-color: #FF4B4B; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0px 4px 10px rgba(0,0,0,0.2); z-index: 1000;" title="Finalizar Chat">
            <span style="color: white; font-size: 35px; font-weight: bold;">×</span>
        </a>
    """, unsafe_allow_html=True)