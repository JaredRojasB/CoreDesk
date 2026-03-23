import streamlit as st
import google.generativeai as genai
import os
import time
from PIL import Image

# MÓDULOS DE ESTILO MODULARES
import global_styles
import auth_styles
import chat_styles
import auth # Lógica de Login

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support", page_icon="🛡️", layout="wide")
global_styles.aplicar_globales() # Pintura Global (blanco)

# IA Setup
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None
# El interruptor para la animación de carga (UX Fix de validación)
if "cargando_inicio" not in st.session_state: st.session_state.cargando_inicio = False

# Carga de Logo
try: logo_img = Image.open("logo.png")
except: logo_img = None

# --- 2. LÓGICA DE NAVEGACIÓN ---

# CASO A: Pantalla de Registro
if st.session_state.user_data is None:
    auth_styles.aplicar_auth() # CSS Exclusivo de Registro (independiente)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_img: st.image(logo_img, use_container_width=True)
        st.markdown("<p class='core-title-main' style='color:#0E3255; text-align:center;'>CoreDesk</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6c757d;'>Intelligent IT Management System</p>", unsafe_allow_html=True)
        
        # auth.mostrar_registro() lo integramos aquí para manejar el spinner
        st.markdown("---")
        with st.form("registro_form"):
            st.subheader("📝 Apertura de Ticket")
            nombre = st.text_input("Nombre Completo:")
            empresa = st.text_input("Empresa / Departamento:")
            correo = st.text_input("Correo Electrónico (Gmail, Outlook, Hotmail):")
            
            btn_ingresar = st.form_submit_button("INICIAR SOPORTE")
            
            if btn_ingresar:
                # Activamos el interruptor ANTES de validar (UX Fix)
                st.session_state.cargando_inicio = True

        # Si el interruptor está activo, mostramos el spinner y LUEGO validamos (UX Fix)
        if st.session_state.cargando_inicio:
            with st.spinner("Validando ticket con el servidor de CoreDesk..."):
                time.sleep(1.5) # Pausa estratégica
                
                if not nombre or not empresa or not correo:
                    st.error("❌ Por favor, llena todos los campos.")
                    st.session_state.cargando_inicio = False # Apagamos carga
                elif not auth.es_correo_valido(correo):
                    st.error("❌ Correo no válido (Usa Gmail, Outlook o Hotmail).")
                    st.session_state.cargando_inicio = False # Apagamos carga
                else:
                    # Todo bien, concedemos acceso
                    st.session_state.user_data = {"nombre": nombre, "empresa": empresa, "correo": correo, "inicio": time.time()}
                    st.session_state.cargando_inicio = False
                    st.success("✅ Datos autorizados.")
                    st.rerun()

# CASO B: Pantalla de Chat Activa
else:
    chat_styles.aplicar_chat() # ¡BUM! Aplicamos CSS Exclusivo de Chat
    
    # 1. Header Fijo (Solo Logo Izq)
    st.markdown('<div class="header-fixed">', unsafe_allow_html=True)
    col_h1, col_h2 = st.columns([1, 8])
    with col_h1:
        if logo_img: st.image(logo_img, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Tarjeta de Usuario Formal con CONTADOR
    minutos_activos = int((time.time() - st.session_state.user_data['inicio']) / 60)
    st.markdown(f"""
        <div class="user-card-formal">
            <div class="user-card-data">
                👤 {st.session_state.user_data['nombre']} | 🏢 {st.session_state.user_data['empresa']}
            </div>
            <div class="counter-box">
                Tiempo de Ticket<br>
                <b>⏱️ {minutos_activos} min.</b>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # BIENVENIDA DE LA IA (Fix Duplicado)
    # Solo se ejecuta si NO hay mensajes en el historial.
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            bienvenida = f"""
            👋 ¡Hola, {st.session_state.user_data['nombre']}! Bienvenido al Soporte Técnico de CoreDesk.
            Estoy aquí para ayudarte a resolver cualquier problema de TI que tengas en {st.session_state.user_data['empresa']}.
            
            **¿Cuál es el inconveniente técnico que presentas el día de hoy?** Describe tu problema paso a paso.
            """
            st.markdown(bienvenida)
            st.session_state.messages.append({"role": "assistant", "content": bienvenida})

    # 3. Historial de Chat (Con burbujas)
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # 4. Barra de Chat FIJA Abajo con el CLIP INTEGRADO (Controlado por CSS)
    col_clip, col_txt = st.columns([1, 15])
    with col_clip:
        # Usamos popover para el clip 📎, ahora azul marino y DENTRO de la barra
        menu_archivos = st.popover("📎")
        with menu_archivos:
            st.write("Adjuntar Evidencia")
            st.button("📷 Imagen del problema", disabled=True)

    with col_txt:
        if prompt := st.chat_input("Escribe tu duda técnica aquí...", key="chat_input"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("CoreDesk AI analizando..."):
                    try:
                        system_prompt = f"""
                        Eres Soporte Senior de CoreDesk. Guía paso a paso a {st.session_state.user_data['nombre']} de {st.session_state.user_data['empresa']}.
                        REGLAS DE RESPUESTA:
                        1. Identifícate como 'Asistente IA de CoreDesk'.
                        2. Responde con un formato de 'GUÍA PASO A PASO EXTREMADAMENTE ESPECÍFICA'.
                        3. Si le pides borrar archivos, no digas 'bórralos'. Di: 'Abre el Explorador (Win+E), navega a X, presiona Ctrl+K'.
                        4. Al final pregunta EXACTAMENTE: '¿Te funcionó la información que te di?'
                        """
                        chat = model.start_chat(history=[])
                        response = chat.send_message(f"{system_prompt}\nProblema: {prompt}")
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Error de conexión: {e}")

    # 5. BOTÓN FLOTANTE 'X' (FIX DEFINITIVO - HTML Puro)
    # No usamos st.button, usamos un enlace HTML que Streamlit detecta.
    if st.markdown('<button id="finalizar-btn-flotante"></button>', unsafe_allow_html=True):
        # Lógica de cierre (Streamlit detecta si el markdown 'button' fue clickeado)
        # Hack para Streamlit: usamos un link invisible que recarga la página
        if st.markdown('<a href="/" target="_self" id="finalizar-btn-flotante"></a>', unsafe_allow_html=True):
            st.session_state.user_data = None
            st.session_state.messages = []
            st.rerun()