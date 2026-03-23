import streamlit as st
import google.generativeai as genai
import os
import time
from PIL import Image

import auth_styles
import chat_styles
import auth

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support", page_icon="🛡️", layout="wide")

# IA Setup - FIX DEL MODELO NOT FOUND
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
# Usamos el nombre de modelo completo para evitar el error NotFound
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None

# Carga de Logo
try: logo_img = Image.open("logo.png")
except: logo_img = None

# --- NAVEGACIÓN ---

# CASO A: Pantalla de Registro
if st.session_state.user_data is None:
    auth_styles.aplicar_auth()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_img: st.image(logo_img, use_container_width=True)
        st.markdown("<h1 style='text-align:center; color:#0E3255;'>CoreDesk</h1>", unsafe_allow_html=True)
        auth.mostrar_registro()

# CASO B: Pantalla de Chat Activa
else:
    chat_styles.aplicar_chat()
    
    # Header Simple
    col_logo, col_timer = st.columns([8, 1])
    with col_logo:
        if logo_img: st.image(logo_img, width=120)
    with col_timer:
        t_min = int((time.time() - st.session_state.user_data['inicio']) / 60)
        st.write(f"⏱️ {t_min} min")

    # Tarjeta Usuario
    st.markdown(f"""
        <div style="background:white; padding:15px; border-radius:10px; border-left:5px solid #0E3255; box-shadow:0 2px 5px rgba(0,0,0,0.05); margin-top:20px;">
            👤 <b>{st.session_state.user_data['nombre']}</b> | 🏢 {st.session_state.user_data['empresa']}
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Historial de Chat (Con Avatares para evitar cuadros naranjas)
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="🤖" if m["role"]=="assistant" else "👤"):
            st.markdown(m["content"])

    # Chat Input Estándar
    if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Respuesta de la IA (Lógica estable de tu código anterior)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("CoreDesk AI analizando..."):
                try:
                    # PROMPT IA EXTREMADAMENTE ESPECÍFICO Y AMIGABLE
                    system_prompt = f"""
                    Eres Soporte Técnico de CoreDesk. Estás ayudando a {st.session_state.user_data['nombre']} de {st.session_state.user_data['empresa']}.

                    REGLAS DE RESPUESTA PARA NOVATOS:
                    1. Identifícate como 'Asistente IA de CoreDesk'.
                    2. Responde con un tono EXTREMADAMENTE AMABLE, PACIENTE y FORMAL. No uses jergas técnicas sin explicarlas.
                    3. Responde con un formato de 'GUÍA PASO A PASO'. Usa números.
                    4. Para cada acción, explica EXACTAMENTE cómo hacerlo. Ejemplos de formato:
                       - 'Abre el Explorador de Archivos (la **carpeta naranja que aparece en la barra de tareas** en la parte inferior de tu pantalla)'.
                       - 'En tu teclado, mantén presionada la tecla **Ctrl** y, sin soltarla, presiona la tecla **R** (Ctrl+R)'.
                    5. Usa negritas para resaltar botones o teclas.
                    6. Al final de tu respuesta, pregunta EXACTAMENTE: "¿Te funcionó la información que te di?"
                    """
                    # Generación directa para máxima estabilidad
                    chat_session = model.start_chat(history=[])
                    full_query = f"{system_prompt}\n\nProblema del usuario: {prompt}"
                    response = chat_session.send_message(full_query)
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error de conexión con la IA. Intenta de nuevo. Detalles: {e}")