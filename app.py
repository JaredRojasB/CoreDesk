import streamlit as st
import google.generativeai as genai
import os
import time
from PIL import Image

import global_styles
import auth_styles
import chat_styles

# --- 1. SETUP ---
st.set_page_config(page_title="CoreDesk Support", page_icon="🛡️", layout="wide")
global_styles.aplicar_globales()

api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None

# Intentar cargar logo
try:
    logo_img = Image.open("logo.png")
except:
    logo_img = None

# --- 2. NAVEGACIÓN ---

if st.session_state.user_data is None:
    # --- PANTALLA DE REGISTRO ---
    auth_styles.aplicar_auth()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_img: st.image(logo_img, use_container_width=True)
        st.markdown("<h1 style='text-align:center; color:#0E3255;'>CoreDesk</h1>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            nombre = st.text_input("Nombre:")
            empresa = st.text_input("Empresa:")
            correo = st.text_input("Correo:")
            
            if st.form_submit_button("INICIAR SOPORTE"):
                if nombre and empresa and "@" in correo:
                    # AQUÍ ESTÁ EL FIX: Guardamos como 'inicio'
                    st.session_state.user_data = {
                        "nombre": nombre, 
                        "empresa": empresa, 
                        "inicio": time.time() 
                    }
                    st.rerun()
                else:
                    st.error("❌ Completa los campos correctamente")

else:
    # --- PANTALLA DE CHAT ACTIVA ---
    chat_styles.aplicar_chat()
    
    # 1. Header (Logo a la izquierda y contador a la derecha)
    # Calculamos tiempo transcurrido
    tiempo_min = int((time.time() - st.session_state.user_data['inicio']) / 60)
    
    st.markdown(f"""
        <div class="header-fixed" style="display: flex; justify-content: space-between; align-items: center; padding: 0 5%; background: white; height: 70px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); position: fixed; top: 0; left: 0; width: 100%; z-index: 1000;">
            <div style="font-weight: bold; color: #0E3255; font-size: 20px;">🛡️ CoreDesk Support</div>
            <div style="color: #6c757d;">⏱️ Activo: {tiempo_min} min</div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Tarjeta de Usuario (Presentable)
    st.markdown(f"""
        <div style="background:white; padding:15px; border-radius:10px; border-left:5px solid #0E3255; box-shadow:0 2px 5px rgba(0,0,0,0.05); margin-top: 20px;">
            👤 <b>{st.session_state.user_data['nombre']}</b> | 🏢 {st.session_state.user_data['empresa']}
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 3. Bienvenida Única de la IA
    if not st.session_state.messages:
        bienvenida = f"¡Hola **{st.session_state.user_data['nombre']}**! Soy tu Asistente de CoreDesk. ¿En qué puedo ayudarte hoy con el equipo de **{st.session_state.user_data['empresa']}**?"
        st.session_state.messages.append({"role": "assistant", "content": bienvenida})

    # 4. Historial de Chat
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # 5. Entrada de Chat con el '+' (Clip)
    # El clip ahora está en un popover a la izquierda del input
    c_clip, c_txt = st.columns([1, 15])
    with c_clip:
        with st.popover("📎"):
            st.button("📷 Imagen", disabled=True)
    
    with c_txt:
        if prompt := st.chat_input("Describe tu problema técnico aquí..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Generar respuesta
            with st.chat_message("assistant"):
                with st.spinner("CoreDesk AI analizando..."):
                    try:
                        usr = st.session_state.user_data['nombre']
                        ctx = f"Eres Soporte CoreDesk. Guía paso a paso a {usr}. Sé extremadamente procedimental (ej. Win+R, Ctrl+C). Pregunta al final si funcionó."
                        res = model.start_chat(history=[]).send_message(f"{ctx}\n{prompt}").text
                        st.markdown(res)
                        st.session_state.messages.append({"role": "assistant", "content": res})
                    except Exception as e:
                        st.error(f"Error: {e}")
            st.rerun()

    # 6. BOTÓN X FLOTANTE (Abajo Izquierda)
    # Al dar clic aquí, borramos sesión y regresamos al inicio
    st.markdown('<a href="/" target="_self" id="finalizar-link">×</a>', unsafe_allow_html=True)
    
    # Truco para que el botón de arriba funcione como reset
    if st.button("Finalizar Chat (Reset)", key="finalizar_manual", help="Cerrar Ticket"):
        st.session_state.user_data = None
        st.session_state.messages = []
        st.rerun()