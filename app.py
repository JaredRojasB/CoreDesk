import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
import re
import time
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image

# --- 1. CONFIGURACIÓN ---
# Usamos layout="wide" para tener más espacio en los lados
st.set_page_config(
    page_title="CoreDesk Support AI", 
    page_icon="🛡️", 
    layout="wide"
)

# --- 2. CSS PERSONALIZADO ---
# Aquí controlamos los colores exactos y las formas
st.markdown("""
    <style>
    .stApp {
        background-color: #f4f7f9;
    }
    /* El título de CoreDesk */
    .core-title {
        color: #0E3255;
        font-size: 55px;
        font-weight: 800;
        margin-bottom: 0px;
    }
    /* Estilo general para todos los botones */
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
    /* El botón de Iniciar Soporte */
    div[data-testid="stForm"] .stButton>button {
        background-color: #0E3255;
        color: white;
        height: 3.5em;
        width: 100%;
    }
    /* Estilo para los Chat Bubbles */
    .stChatMessage {
        border-radius: 20px;
    }
    /* El spinner de carga del color de la marca */
    .stSpinner > div {
        border-top-color: #0E3255 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INICIALIZACIÓN ---
load_dotenv()
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Gestión de Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None
if "cargando" not in st.session_state: st.session_state.cargando = False

def es_correo_valido(correo):
    return re.match(r'^[a-zA-Z0-9_.+-]+@(gmail\.com|outlook\.com|hotmail\.com)$', correo)

def guardar_en_bitacora(nombre, empresa, correo, problema, respuesta):
    archivo = "bitacora_coredesk.csv"
    nueva_entrada = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Usuario": nombre, "Empresa": empresa, "Correo": correo,
        "Problema": problema, "Solucion_IA": respuesta.replace('\n', ' ')
    }
    df = pd.DataFrame([nueva_entrada])
    if not os.path.isfile(archivo): df.to_csv(archivo, index=False, encoding='utf-8')
    else: df.to_csv(archivo, mode='a', header=False, index=False, encoding='utf-8')

# --- 4. CABECERA Y BANNER ---
with st.container():
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        try:
            # Buscamos tu logo exactamente como se llama en el explorador
            st.image(Image.open("logo.png"), use_container_width=True)
        except:
            st.markdown("<h1 style='text-align: center;'>🛡️</h1>", unsafe_allow_html=True)
    st.markdown("<p class='core-title' style='text-align: center;'>CoreDesk</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6c757d;'>Sistema de Soporte Técnico Inteligente</p>", unsafe_allow_html=True)

# --- 5. LÓGICA DE REGISTRO ---
if st.session_state.user_data is None:
    st.markdown("---")
    # Centramos el formulario
    col_f1, col_f2, col_f3 = st.columns([1, 3, 1])
    with col_f2:
        with st.form("registro_form"):
            st.subheader("📝 Apertura de Ticket")
            nombre = st.text_input("Nombre Completo:")
            empresa = st.text_input("Empresa / Departamento:")
            correo = st.text_input("Correo Electrónico (Gmail, Outlook, Hotmail):")
            
            btn_ingresar = st.form_submit_button("INICIAR SOPORTE")
            
            if btn_ingresar:
                st.session_state.cargando = True

    # Si se activa la carga, mostramos el spinner azul
    if st.session_state.cargando:
        with st.spinner("Sincronizando ticket con el servidor de CoreDesk..."):
            time.sleep(1.5) # Pausa estratégica
            
            # Recargamos los inputs para leer los valores actuales
            if not nombre or not empresa or not correo:
                st.error("❌ Por favor, llena todos los campos.")
                st.session_state.cargando = False 
            elif not es_correo_valido(correo):
                st.error("❌ El dominio del correo no es válido (Usa Gmail, Outlook o Hotmail).")
                st.session_state.cargando = False 
            else:
                # Todo bien, concedemos acceso
                st.session_state.user_data = {"nombre": nombre, "empresa": empresa, "correo": correo}
                st.session_state.cargando = False
                st.success("✅ Datos autorizados.")
                st.rerun()

# --- 6. INTERFAZ DE CHAT ACTIVA ---
else:
    # 6a. Barra Superior del Chat (Notificación y Botón Finalizar)
    # Creamos dos columnas: una para el texto y una pequeña para el botón
    header_chat_1, header_chat_2 = st.columns([6, 1])
    
    with header_chat_1:
        st.write(f"Conectado como: **{st.session_state.user_data['nombre']}** | {st.session_state.user_data['empresa']}")
    
    with header_chat_2:
        # Aquí está el botón FINALIZAR, lo ponemos en rojo usando CSS en el Session State
        if st.button("FINALIZAR", key="btn_finalizar"):
            with st.spinner("Cerrando ticket..."):
                time.sleep(0.5)
                st.session_state.messages = []
                st.session_state.user_data = None
                st.rerun()
                
    # Aplicamos CSS específico para el botón de finalizar (rojo) y que flote arriba a la derecha
    st.markdown("""
        <style>
        /* El botón de finalizar por su key 'btn_finalizar' */
        div[data-testid="stButton"][aria-label="FINALIZAR"] > button {
            background-color: #d9534f;
            color: red;
            position: absolute;
            top: 10px;
            right: 10px;
            height: 2.5em;
            width: auto;
            border: none;
        }
        div[data-testid="stButton"][aria-label="FINALIZAR"] > button:hover {
            background-color: #c9302c;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 6b. Área de mensajes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 6c. Entrada de Chat Mejorada (Clip para imágenes)
    # Creamos columnas al lado de la entrada de texto
    col_input1, col_input2 = st.columns([1, 20])
    
    with col_input1:
        # Usamos popover para el menú desplegable del clip
        menu_archivos = st.popover("📎", help="Adjuntar archivos")
        with menu_archivos:
            st.write("Selecciona archivo:")
            # Botón inactivo por ahora
            st.button("📷 Imagen del problema (Hardware)", disabled=True)
            # st.button("📄 Logs del sistema", disabled=True) # Idea para el futuro

    with col_input2:
        prompt = st.chat_input("Escribe tu duda técnica aquí...", key="chat_input_val")

    # Lógica de respuesta de la IA (Se ejecuta si hay prompt)
    if prompt:
        # Añadir mensaje del usuario al historial
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generar respuesta de la IA
        with st.chat_message("assistant"):
            with st.spinner("Consultando base de conocimientos técnica..."):
                try:
                    system_prompt = f"""
                    Eres Soporte Senior de CoreDesk. Ayuda a {st.session_state.user_data['nombre']}.
                    Diagnostica el problema y da una guía paso a paso muy específica.
                    Usa negritas para componentes de hardware y comandos.
                    Al final pregunta: '¿Te funcionó la información que te di?'
                    """
                    chat = model.start_chat(history=[])
                    full_prompt = f"{system_prompt}\nProblema: {prompt}"
                    response = chat.send_message(full_prompt)
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                    guardar_en_bitacora(
                        st.session_state.user_data['nombre'], 
                        st.session_state.user_data['empresa'], 
                        st.session_state.user_data['correo'],
                        prompt, 
                        response.text
                    )
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

    # --- BARRA LATERAL (ADMIN) ---
    with st.sidebar:
        st.title("🛡️ Admin Panel")
        st.write("Solo visible para técnicos IT")
        
        st.markdown("---")
        if os.path.exists("bitacora_coredesk.csv"):
            # Usamos el CSV real
            df_log = pd.read_csv("bitacora_coredesk.csv")
            st.download_button(
                label="📥 Descargar Reportes",
                data=df_log.to_csv(index=False).encode('utf-8'),
                file_name="bitacora_coredesk.csv",
                mime="text/csv"
            )
        else:
            st.write("Aún no hay reportes generados.")