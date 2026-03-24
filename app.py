import os
import time
from PIL import Image

import streamlit as st
import google.generativeai as genai


# =========================================================
# 1. CONFIGURACIÓN GENERAL
# =========================================================
st.set_page_config(
    page_title="CoreDesk Support",
    page_icon="🛡️",
    layout="wide"
)


# =========================================================
# 2. FUNCIONES BASE
# =========================================================
def cargar_logo():
    """Carga el logo desde assets/logo.png si existe."""
    try:
        return Image.open("assets/logo.png")
    except FileNotFoundError:
        return None
    except Exception:
        return None


def aplicar_estilos():
    """Carga los estilos desde styles/main.css."""
    try:
        with open("styles/main.css", "r", encoding="utf-8") as archivo_css:
            css = archivo_css.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("No se encontró el archivo styles/main.css")


def configurar_modelo():
    """Configura Gemini y guarda el modelo en session_state."""
    api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not api_key:
        st.error("No se encontró GOOGLE_API_KEY en secrets o variables de entorno.")
        st.stop()

    genai.configure(api_key=api_key)

    if "model" not in st.session_state:
        try:
            modelos = [
                m.name
                for m in genai.list_models()
                if "generateContent" in m.supported_generation_methods
            ]

            if not modelos:
                st.error("No se encontraron modelos disponibles de Gemini.")
                st.stop()

            nombre_modelo = next(
                (m for m in modelos if "flash" in m.lower()),
                modelos[0]
            )

            st.session_state.model = genai.GenerativeModel(nombre_modelo)

        except Exception as e:
            st.error(f"Error al configurar el modelo: {e}")
            st.stop()


def inicializar_sesion():
    """Inicializa variables necesarias en session_state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "user_data" not in st.session_state:
        st.session_state.user_data = None

    if "bienvenida_enviada" not in st.session_state:
        st.session_state.bienvenida_enviada = False


# =========================================================
# 3. FUNCIONES DE INTERFAZ
# =========================================================
def mostrar_registro(logo_img):
    """Muestra la pantalla de registro/inicio."""
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if logo_img:
            st.image(logo_img, width=150)

        st.markdown(
            "<h1 style='color:#0E3255; text-align:center;'>CoreDesk</h1>",
            unsafe_allow_html=True
        )

        with st.form("registro"):
            nombre = st.text_input("Nombre Completo:")
            empresa = st.text_input("Empresa:")

            if st.form_submit_button("INGRESAR AL SISTEMA"):
                if nombre and empresa:
                    st.session_state.user_data = {
                        "nombre": nombre,
                        "empresa": empresa,
                        "inicio": time.time()
                    }
                    st.rerun()
                else:
                    st.warning("Por favor completa ambos campos.")


def mostrar_header_chat(logo_img):
    """Muestra el header fijo del chat."""
    st.markdown(
        """
        <div style="
            position:fixed;
            top:0;
            left:0;
            width:100%;
            height:70px;
            background:white;
            z-index:999;
            display:flex;
            align-items:center;
            padding:0 5%;
            border-bottom:1px solid #EEE;
        ">
        """,
        unsafe_allow_html=True
    )

    if logo_img:
        st.image(logo_img, width=140)

    inicio_t = st.session_state.user_data.get("inicio", time.time())
    t_min = int((time.time() - inicio_t) / 60)

    st.markdown(
        f"""
        <div style="margin-left:auto;color:#6c757d;font-weight:bold;">
            ⏱️ {t_min} min activo
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # Margen para no chocar con el header
    st.markdown('<div style="margin-top: 90px;"></div>', unsafe_allow_html=True)


def mostrar_tarjeta_usuario():
    """Muestra la tarjeta con los datos del usuario."""
    nombre = st.session_state.user_data["nombre"]
    empresa = st.session_state.user_data["empresa"]

    st.markdown(f"""
        <div style="
            background:#F0F4F8;
            padding:18px;
            border-radius:12px;
            border-left:6px solid #0E3255;
            box-shadow:0 4px 12px rgba(0,0,0,0.08);
            margin-bottom: 20px;
            font-size: 16px;
        ">
            👤 <b>{nombre}</b> &nbsp;&nbsp;|&nbsp;&nbsp; 🏢 {empresa}
        </div>
    """, unsafe_allow_html=True)

    st.divider()


def enviar_bienvenida_si_falta():
    """Agrega el mensaje de bienvenida solo una vez."""
    if not st.session_state.bienvenida_enviada:
        nombre = st.session_state.user_data["nombre"]
        saludo = (
            f"¡Hola **{nombre}**! 👋 Bienvenido al soporte técnico de CoreDesk. "
            f"¿En qué puedo ayudarte?"
        )
        st.session_state.messages.append({
            "role": "assistant",
            "content": saludo
        })
        st.session_state.bienvenida_enviada = True


def mostrar_historial():
    """Muestra todos los mensajes guardados en la sesión."""
    for mensaje in st.session_state.messages:
        rol = mensaje["role"]
        avatar = "🧑" if rol == "user" else "🛠️"

        with st.chat_message(rol, avatar=avatar):
            st.markdown(mensaje["content"])


def procesar_input_usuario():
    """Procesa el nuevo mensaje del usuario y genera respuesta de IA."""
    prompt = st.chat_input("Escribe tu duda técnica aquí...")

    if prompt:
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🛠️"):
            with st.spinner("CoreDesk AI analizando..."):
                try:
                    nombre_usuario = st.session_state.user_data["nombre"]

                    contexto = (
                        f"Eres experto de CoreDesk ayudando a {nombre_usuario}. "
                        f"Explica paso a paso. "
                        f"3 pitidos largos y 2 cortos indican error de memoria RAM."
                    )

                    respuesta = st.session_state.model.generate_content(
                        f"{contexto}\n\nProblema: {prompt}"
                    )

                    texto_respuesta = respuesta.text
                    st.markdown(texto_respuesta)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": texto_respuesta
                    })

                except Exception as e:
                    st.error(f"Error: {e}")

        st.rerun()


def mostrar_boton_finalizar():
    """Muestra el botón para finalizar el chat y reinicia la sesión."""
    if st.button("Finalizar Chat", key="finalizar-btn"):
        st.session_state.user_data = None
        st.session_state.messages = []
        st.session_state.bienvenida_enviada = False
        st.rerun()


def mostrar_chat(logo_img):
    """Agrupa toda la vista del chat."""
    mostrar_header_chat(logo_img)
    mostrar_tarjeta_usuario()
    enviar_bienvenida_si_falta()
    mostrar_historial()
    procesar_input_usuario()
    mostrar_boton_finalizar()


# =========================================================
# 4. FUNCIÓN PRINCIPAL
# =========================================================
def main():
    logo_img = cargar_logo()
    aplicar_estilos()
    configurar_modelo()
    inicializar_sesion()

    if st.session_state.user_data is None:
        mostrar_registro(logo_img)
    else:
        mostrar_chat(logo_img)


# =========================================================
# 5. EJECUCIÓN
# =========================================================
if __name__ == "__main__":
    main()