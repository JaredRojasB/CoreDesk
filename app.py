import streamlit as st
import google.generativeai as genai
import os
# Borra load_dotenv si quieres, Streamlit no lo necesita para los Secrets

# --- CONFIGURACIÓN DE IA (Modo Nube) ---
# Intentamos leer de Streamlit Secrets (Nube) o de .env (Local)
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("No se encontró la configuración de la API Key.")
    st.stop()

genai.configure(api_key=api_key)

# 2. Inicializar el historial del chat y datos del usuario
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# --- PANTALLA DE REGISTRO ---
if st.session_state.user_data is None:
    st.title("🛡️ Registro de Incidencia - CoreDesk")
    with st.form("registro"):
        nombre = st.text_input("Nombre Completo:")
        empresa = st.text_input("Empresa:")
        submit = st.form_submit_button("Entrar al Soporte")
        
        if submit:
            if nombre and empresa:
                st.session_state.user_data = {"nombre": nombre, "empresa": empresa}
                st.rerun()
            else:
                st.error("Por favor llena todos los campos.")
else:
    # --- INTERFAZ DE CHAT ---
    st.title(f"🖥️ CoreDesk Support")
    st.caption(f"Usuario: {st.session_state.user_data['nombre']} | Empresa: {st.session_state.user_data['empresa']}")

    # Mostrar mensajes previos
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada del chat
    if prompt := st.chat_input("¿En qué puedo ayudarte hoy?"):
        # Mostrar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Respuesta de la IA
        with st.chat_message("assistant"):
            with st.spinner("CoreDesk está pensando..."):
                # Incluimos el contexto en las instrucciones
                contexto = f"Eres el asistente de soporte técnico de CoreDesk. Atiendes a {st.session_state.user_data['nombre']} de la empresa {st.session_state.user_data['empresa']}. Si el usuario dice que algo no funcionó, ofrece alternativas técnicas más profundas."
                
                # Enviamos todo el historial para que tenga memoria
                chat = model.start_chat(history=[])
                response = chat.send_message(f"{contexto}\nUsuario dice: {prompt}")
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

    # Botón para cerrar ticket/limpiar
    if st.sidebar.button("Cerrar Ticket y Salir"):
        st.session_state.user_data = None
        st.session_state.messages = []
        st.rerun()