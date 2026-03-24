import os
import re
import time
from pathlib import Path
from PIL import Image

import streamlit as st
import google.generativeai as genai

from components.login_view import mostrar_registro


# =========================================================
# 1. CONFIGURACIÓN GENERAL
# =========================================================
st.set_page_config(
    page_title="CoreDesk Support",
    page_icon="🛡️",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent


# =========================================================
# 2. FUNCIONES BASE
# =========================================================
def cargar_logo():
    ruta_logo = BASE_DIR / "assets" / "logo.png"
    try:
        return Image.open(ruta_logo)
    except FileNotFoundError:
        return None
    except Exception:
        return None


def aplicar_estilos():
    ruta_css = BASE_DIR / "styles" / "main.css"
    try:
        with open(ruta_css, "r", encoding="utf-8") as archivo_css:
            css = archivo_css.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"No se encontró el archivo: {ruta_css}")


def configurar_modelo():
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
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "user_data" not in st.session_state:
        st.session_state.user_data = None

    if "bienvenida_enviada" not in st.session_state:
        st.session_state.bienvenida_enviada = False

    if "cerrando_chat" not in st.session_state:
        st.session_state.cerrando_chat = False


def construir_prompt_soporte(nombre_usuario, prompt_usuario):
    return f"""
Eres un agente de soporte técnico llamado CoreDesk AI y estás ayudando a {nombre_usuario}.

REGLAS IMPORTANTES DE RESPUESTA:
1. Responde siempre en español.
2. Explica todo paso a paso, como si la persona no supiera casi nada de computadoras.
3. Nunca des pasos ambiguos como "revisa la carpeta" o "abre configuración" sin explicar exactamente cómo hacerlo.
4. Cuando menciones una ruta o una carpeta, explica cómo llegar:
   - qué tecla presionar
   - qué escribir
   - dónde dar clic
   - qué debería ver el usuario
5. Usa formato visual ordenado con títulos y viñetas.
6. Usa emojis simples para hacer clara la respuesta, por ejemplo:
   - 🟢 para pasos recomendados
   - 🔴 para advertencias o errores
   - 🟡 para verificaciones
   - 📂 para rutas o carpetas
   - ⚙️ para configuración
7. Si el problema requiere varios pasos, sepáralos por secciones y especifica la sección.
8. Si hay riesgo de que el usuario se equivoque, adviértelo claramente.
9. No respondas de forma genérica. Sé específico y accionable.
10. Si el usuario habla de hardware físico, daño físico, pantalla rota, aumento de RAM, piezas, reparación, motherboard, disco dañado o algo que requiera revisión presencial, aclara que probablemente será necesario escalar con soporte técnico presencial.

ESTRUCTURA QUE DEBES SEGUIR SIEMPRE:
- Una línea breve de diagnóstico inicial
- Sección: "🟡 Qué está pasando"
- Sección: "🟢 Qué debes hacer paso a paso"
- Sección: "🔴 Qué no debes hacer" (solo si aplica)
- Sección: "🔵 Qué necesito que me confirmes al final"

INFORMACIÓN TÉCNICA EXTRA:
- Si no estás seguro del diagnóstico, dilo con honestidad y guía al usuario en verificaciones simples primero.

PROBLEMA DEL USUARIO:
{prompt_usuario}
"""


def extraer_segundos_espera(error_texto: str):
    if not error_texto:
        return None

    patron_retry = re.search(r"retry in ([0-9]+(?:\.[0-9]+)?)s", error_texto, re.IGNORECASE)
    if patron_retry:
        return max(1, round(float(patron_retry.group(1))))

    patron_seconds = re.search(r"seconds:\s*([0-9]+)", error_texto, re.IGNORECASE)
    if patron_seconds:
        return max(1, int(patron_seconds.group(1)))

    return None


def construir_mensaje_error_amigable(error: Exception):
    texto_error = str(error).lower()

    if "429" in texto_error or "quota" in texto_error or "rate limit" in texto_error:
        segundos = extraer_segundos_espera(str(error))

        if segundos:
            return (
                f"🟡 **CoreDesk AI alcanzó temporalmente su límite de solicitudes.**\n\n"
                f"Por favor espera aproximadamente **{segundos} segundos** y vuelve a intentarlo.\n\n"
                f"Tu mensaje se recibió correctamente, pero la IA no pudo responder en este momento."
            )
        else:
            return (
                "🟡 **CoreDesk AI alcanzó temporalmente su límite de solicitudes.**\n\n"
                "Por favor espera unos momentos y vuelve a intentarlo.\n\n"
                "Tu mensaje se recibió correctamente, pero la IA no pudo responder en este momento."
            )

    return (
        "🔴 **Ocurrió un problema al generar la respuesta de CoreDesk AI.**\n\n"
        "Intenta nuevamente en unos momentos. Si no funciona, contacta a IT vía correo."
    )


def formatear_tiempo_sesion(segundos_totales: int) -> str:
    minutos = segundos_totales // 60
    segundos = segundos_totales % 60
    return f"{minutos:02d}:{segundos:02d}"


def mostrar_overlay_cierre():
    st.markdown(
        """
        <div class="closing-overlay">
            <div class="closing-modal">
                <div class="closing-spinner"></div>
                <div class="closing-title">Cerrando el chat</div>
                <div class="closing-subtitle">Gracias por usar CoreDesk</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def iniciar_cierre_chat():
    st.session_state.cerrando_chat = True
    st.rerun()


def procesar_cierre_chat():
    """
    Segunda fase del cierre:
    muestra solo el overlay, espera y luego limpia sesión.
    """
    mostrar_overlay_cierre()
    time.sleep(1.2)

    st.session_state.user_data = None
    st.session_state.messages = []
    st.session_state.bienvenida_enviada = False
    st.session_state.cerrando_chat = False
    st.rerun()


# =========================================================
# 3. INTERFAZ CHAT
# =========================================================
def mostrar_header_chat():
    inicio_t = st.session_state.user_data.get("inicio", time.time())
    segundos = int(time.time() - inicio_t)
    tiempo_texto = formatear_tiempo_sesion(segundos)

    st.markdown(
        f"""
        <div id="top-chat"></div>
        <div class="coredesk-header-shell">
            <div class="coredesk-header-fixed">
                <div class="coredesk-header-content">
                    <div class="coredesk-header-brand">
                        CoreDesk Support
                    </div>
                    <div class="coredesk-header-right">
                        <span class="coredesk-header-divider"></span>
                        <span class="coredesk-header-timer">⏱ {tiempo_texto} en sesión</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="coredesk-header-spacer"></div>
        """,
        unsafe_allow_html=True
    )


def mostrar_tarjeta_usuario():
    user = st.session_state.user_data
    nombre = user.get("nombre", "Sin nombre")
    empresa = user.get("empresa", "Sin empresa")
    correo = user.get("correo", "Sin correo")

    with st.container():
        st.markdown('<div class="session-card-hook"></div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="session-card-title">Sesión activa</div>
            <div class="session-card-row"><span class="session-card-label">👤 Atendiendo a:</span> <span class="session-card-value">{nombre}</span></div>
            <div class="session-card-row"><span class="session-card-label">🏢 Empresa:</span> <span class="session-card-value">{empresa}</span></div>
            <div class="session-card-row"><span class="session-card-label">📧 Correo:</span> <span class="session-card-value">{correo}</span></div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([1, 1.1, 1])
        with col2:
            if st.button("Finalizar este chat", key="finalizar-btn", use_container_width=True):
                iniciar_cierre_chat()

    st.divider()


def enviar_bienvenida_si_falta():
    if not st.session_state.bienvenida_enviada:
        nombre = st.session_state.user_data["nombre"]
        saludo = (
            f"¡Hola **{nombre}**! 👋 Bienvenido al soporte técnico de CoreDesk. "
            f"Por favor, describe el problema que tienes con tu equipo y te ayudaremos a resolverlo."
        )
        st.session_state.messages.append({
            "role": "assistant",
            "content": saludo
        })
        st.session_state.bienvenida_enviada = True


def mostrar_historial():
    for mensaje in st.session_state.messages:
        rol = mensaje["role"]

        if rol == "assistant":
            avatar_path = BASE_DIR / "assets" / "bot.png"
            avatar = str(avatar_path) if avatar_path.exists() else None
        else:
            avatar = None

        with st.chat_message(rol, avatar=avatar):
            st.markdown(mensaje["content"])


def procesar_input_usuario():
    prompt = st.chat_input("Escribe aquí")

    if prompt:
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        avatar_path = BASE_DIR / "assets" / "bot.png"
        avatar = str(avatar_path) if avatar_path.exists() else None

        respuesta_generada = False

        with st.chat_message("assistant", avatar=avatar):
            with st.spinner("CoreDesk AI está analizando tu problema..."):
                try:
                    nombre_usuario = st.session_state.user_data["nombre"]
                    prompt_final = construir_prompt_soporte(nombre_usuario, prompt)

                    respuesta = st.session_state.model.generate_content(prompt_final)
                    texto_respuesta = respuesta.text

                    st.markdown(texto_respuesta)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": texto_respuesta
                    })

                    respuesta_generada = True

                except Exception as e:
                    mensaje_error = construir_mensaje_error_amigable(e)
                    st.markdown(mensaje_error)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": mensaje_error
                    })

        if respuesta_generada:
            st.rerun()


def mostrar_boton_subir():
    st.markdown(
        """
        <a href="#top-chat" class="scroll-top-btn" title="Subir al inicio">↑</a>
        """,
        unsafe_allow_html=True
    )


def mostrar_chat():
    mostrar_header_chat()
    mostrar_tarjeta_usuario()
    enviar_bienvenida_si_falta()
    mostrar_historial()
    mostrar_boton_subir()


# =========================================================
# 4. FUNCIÓN PRINCIPAL
# =========================================================
def main():
    logo_img = cargar_logo()
    aplicar_estilos()
    configurar_modelo()
    inicializar_sesion()

    # Si está en proceso de cierre, NO renderizamos chat normal
    if st.session_state.cerrando_chat:
        procesar_cierre_chat()
        st.stop()

    if st.session_state.user_data is None:
        mostrar_registro(logo_img)
    else:
        mostrar_chat()
        procesar_input_usuario()


# =========================================================
# 5. EJECUCIÓN
# =========================================================
if __name__ == "__main__":
    main()