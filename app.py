import os
import time
from pathlib import Path
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

BASE_DIR = Path(__file__).resolve().parent


# =========================================================
# 2. FUNCIONES BASE
# =========================================================
def cargar_logo():
    """Carga el logo desde assets/logo.png si existe."""
    ruta_logo = BASE_DIR / "assets" / "logo.png"

    try:
        return Image.open(ruta_logo)
    except FileNotFoundError:
        return None
    except Exception:
        return None


def aplicar_estilos():
    """Carga los estilos desde styles/main.css."""
    ruta_css = BASE_DIR / "styles" / "main.css"

    try:
        with open(ruta_css, "r", encoding="utf-8") as archivo_css:
            css = archivo_css.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"No se encontró el archivo: {ruta_css}")


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


def construir_prompt_soporte(nombre_usuario, prompt_usuario):
    """Construye el prompt principal para respuestas de soporte más claras."""
    return f"""
Eres un agente de soporte técnico llamado CoreDesk AI y estás ayudando a {nombre_usuario}.

REGLAS IMPORTANTES DE RESPUESTA:
1. Responde siempre en español.
2. Explica todo paso a paso, como si la persona no supiera casi nada de computadoras.
3. Nunca des pasos ambiguos como "revisa la carpeta" o "abre configuración" sin explicar exactamente cómo hacerlo.
4. Cuando menciones una ruta o una carpeta, explica cómo llegar:
   - qué tecla presionar,
   - qué escribir,
   - dónde dar clic,
   - qué debería ver el usuario.
5. Usa formato visual ordenado con títulos y viñetas.
6. Usa emojis simples para hacer clara la respuesta, por ejemplo:
   - 🟢 para pasos recomendados
   - 🔴 para advertencias o errores
   - 🟡 para verificaciones
   - 📂 para rutas o carpetas
   - ⚙️ para configuración
7. Si el problema requiere varios pasos, sepáralos por secciones.
8. Si hay riesgo de que el usuario se equivoque, adviértelo claramente.
9. No respondas de forma genérica. Sé específico y accionable.
10. Si el usuario habla de hardware físico, daño físico, pantalla rota, aumento de RAM, piezas, reparación, motherboard, disco dañado o algo que requiera revisión presencial, aclara que probablemente será necesario escalar con soporte técnico presencial.

ESTRUCTURA QUE DEBES SEGUIR SIEMPRE:
- Una línea breve de diagnóstico inicial
- Sección: "🟡 Qué está pasando"
- Sección: "🟢 Qué debes hacer paso a paso"
- Sección: "🔴 Qué no debes hacer" (solo si aplica)
- Sección: "🟡 Qué necesito que me confirmes al final"

INFORMACIÓN TÉCNICA EXTRA:
- Si se menciona "3 pitidos largos y 2 cortos", interprétalo como posible error relacionado con memoria RAM.
- Si no estás seguro del diagnóstico, dilo con honestidad y guía al usuario en verificaciones simples primero.

PROBLEMA DEL USUARIO:
{prompt_usuario}
"""


# =========================================================
# 3. FUNCIONES DE INTERFAZ
# =========================================================
def mostrar_registro(logo_img):
    """Muestra la pantalla de registro/inicio."""
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if logo_img:
            st.image(logo_img, width=170)

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
        <div class="coredesk-header">
            <div class="coredesk-header-inner">
        """,
        unsafe_allow_html=True
    )

    if logo_img:
        st.image(logo_img, width=150)

    inicio_t = st.session_state.user_data.get("inicio", time.time())
    t_min = int((time.time() - inicio_t) / 60)

    st.markdown(
        f"""
                <div class="coredesk-timer">⏱️ {t_min} min activo</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="coredesk-header-spacer"></div>', unsafe_allow_html=True)


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
            f"Cuéntame tu problema y te lo explicaré paso a paso."
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
        avatar = "🤖" if rol == "assistant" else "👤"

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

        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("CoreDesk AI analizando..."):
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

    st.markdown('<div class="coredesk-bottom-space"></div>', unsafe_allow_html=True)

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