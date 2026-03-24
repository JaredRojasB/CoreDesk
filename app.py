import os
import re
import time
import json
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

    if "ticket_history" not in st.session_state:
        st.session_state.ticket_history = []

    if "ultimo_analisis_ticket" not in st.session_state:
        st.session_state.ultimo_analisis_ticket = None


# =========================================================
# 3. LÓGICA HÍBRIDA DE CLASIFICACIÓN
# =========================================================
def normalizar_texto(texto: str) -> str:
    return " ".join(texto.lower().strip().split())


def analizar_prioridad_por_palabras_clave(prompt_usuario: str):
    """
    Regla rápida por palabras clave.
    Sirve como respaldo y como primera estimación.
    """
    texto = normalizar_texto(prompt_usuario)

    palabras_criticas = [
        "no puedo trabajar", "no enciende", "equipo no enciende", "huele a quemado",
        "pantalla rota", "se rompio la pantalla", "pantalla quebrada", "quebrada",
        "disco dañado", "disco danado", "motherboard", "placa madre", "fuente dañada",
        "fuente danada", "ram dañada", "ram danada", "aumentar ram", "cambiar ram",
        "cambiar disco", "disco duro roto", "ssd roto", "hace ruido el disco",
        "equipo quemado", "equipo se apaga solo", "se apaga solo", "pantallazo azul constante",
        "blue screen", "pantalla azul constante", "equipo muerto", "no arranca"
    ]

    palabras_altas = [
        "sin internet", "no tengo internet", "outlook no abre", "no puedo entrar",
        "no tengo acceso", "error constante", "pantalla azul", "muy lento",
        "equipo muy lento", "no abre office", "correo no funciona", "vpn no conecta",
        "no puedo conectarme", "se reinicia", "se traba mucho"
    ]

    palabras_medias = [
        "impresora", "audio", "camara", "cámara", "office", "excel", "word",
        "instalar programa", "instalar software", "configurar", "microfono", "micrófono",
        "periférico", "periferico", "monitor", "teclado", "mouse"
    ]

    palabras_bajas = [
        "duda", "consulta", "como", "cómo", "firma", "configurar firma",
        "cambiar fondo", "personalizar", "quiero saber", "informacion", "información"
    ]

    categoria = "Software"
    prioridad = "Media"
    escalado = False
    motivo = "Caso general pendiente de validación."
    confianza = "media"

    if any(p in texto for p in palabras_criticas):
        prioridad = "Crítica"
        escalado = True
        categoria = "Hardware"
        motivo = "Se detectó una posible falla física o caso que requiere revisión presencial."
        confianza = "alta"
    elif any(p in texto for p in palabras_altas):
        prioridad = "Alta"
        categoria = "Software/Acceso/Red"
        motivo = "Se detectó una afectación importante al trabajo del usuario."
        confianza = "media"
    elif any(p in texto for p in palabras_medias):
        prioridad = "Media"
        categoria = "Soporte general"
        motivo = "Caso operativo que probablemente puede resolverse por guía remota."
        confianza = "media"
    elif any(p in texto for p in palabras_bajas):
        prioridad = "Baja"
        categoria = "Consulta"
        motivo = "Se detectó una solicitud informativa o de baja urgencia."
        confianza = "media"

    return {
        "categoria": categoria,
        "prioridad": prioridad,
        "escalado": escalado,
        "motivo_escalado": motivo,
        "confianza": confianza,
        "fuente": "palabras_clave"
    }


def analizar_ticket_con_ia(prompt_usuario: str):
    """
    Pide a Gemini una clasificación estructurada del ticket.
    """
    instruccion = f"""
Analiza el siguiente ticket de soporte y responde SOLO en JSON válido.

Debes devolver exactamente estas claves:
- categoria
- prioridad
- escalado
- motivo_escalado
- confianza

Reglas:
- categoria debe ser una de estas:
  "Hardware", "Software", "Red", "Acceso", "Correo", "Consulta", "Otro"

- prioridad debe ser una de estas:
  "Baja", "Media", "Alta", "Crítica"

- escalado debe ser true o false

- motivo_escalado debe explicar brevemente por qué se escala o por qué no

- confianza debe ser una de estas:
  "baja", "media", "alta"

Criterios importantes:
- Escala si el caso parece requerir revisión física, piezas, daño físico, pantalla rota,
  no enciende, aumento de RAM, disco duro/SSD, motherboard, olor a quemado, fallas eléctricas,
  problemas físicos de laptop/PC, reparación presencial.
- No escales si el caso parece resoluble por pasos remotos.

TICKET:
{prompt_usuario}
"""
    respuesta = st.session_state.model.generate_content(instruccion)
    texto = respuesta.text.strip()

    # Intenta limpiar respuesta si viene dentro de ```json
    texto = texto.replace("```json", "").replace("```", "").strip()
    data = json.loads(texto)

    return {
        "categoria": str(data.get("categoria", "Otro")).strip(),
        "prioridad": str(data.get("prioridad", "Media")).strip(),
        "escalado": bool(data.get("escalado", False)),
        "motivo_escalado": str(data.get("motivo_escalado", "Sin motivo especificado.")).strip(),
        "confianza": str(data.get("confianza", "media")).strip(),
        "fuente": "ia"
    }


def analizar_ticket_hibrido(prompt_usuario: str):
    """
    Primero estima por palabras clave.
    Luego intenta validarlo con IA.
    Si IA falla, se queda con la estimación local.
    """
    analisis_base = analizar_prioridad_por_palabras_clave(prompt_usuario)

    try:
        analisis_ia = analizar_ticket_con_ia(prompt_usuario)

        # Si la IA detecta algo más serio, respetamos la IA
        prioridad_orden = {"Baja": 1, "Media": 2, "Alta": 3, "Crítica": 4}

        prioridad_base = prioridad_orden.get(analisis_base["prioridad"], 2)
        prioridad_ia = prioridad_orden.get(analisis_ia["prioridad"], 2)

        # Escalado conservador: si cualquiera detecta escalado, escalamos
        escalado_final = analisis_base["escalado"] or analisis_ia["escalado"]

        # Prioridad más alta gana
        prioridad_final = analisis_ia["prioridad"] if prioridad_ia >= prioridad_base else analisis_base["prioridad"]

        # Categoría IA si existe
        categoria_final = analisis_ia["categoria"] or analisis_base["categoria"]

        # Motivo: si escala IA, usamos el de IA; si no, el base
        if analisis_ia["escalado"]:
            motivo_final = analisis_ia["motivo_escalado"]
        elif analisis_base["escalado"]:
            motivo_final = analisis_base["motivo_escalado"]
        else:
            motivo_final = analisis_ia["motivo_escalado"] or analisis_base["motivo_escalado"]

        return {
            "categoria": categoria_final,
            "prioridad": prioridad_final,
            "escalado": escalado_final,
            "motivo_escalado": motivo_final,
            "confianza": analisis_ia["confianza"],
            "fuente": "hibrido"
        }

    except Exception:
        return analisis_base


def construir_prompt_soporte_hibrido(nombre_usuario, prompt_usuario, analisis_ticket):
    categoria = analisis_ticket["categoria"]
    prioridad = analisis_ticket["prioridad"]
    escalado = analisis_ticket["escalado"]
    motivo_escalado = analisis_ticket["motivo_escalado"]

    modo_escalado = ""
    if escalado:
        modo_escalado = f"""
IMPORTANTE:
Este ticket YA fue clasificado como caso ESCALADO.

CATEGORÍA DETECTADA: {categoria}
PRIORIDAD DETECTADA: {prioridad}
MOTIVO DE ESCALAMIENTO: {motivo_escalado}

INSTRUCCIONES ESPECIALES:
1. NO intentes resolver por completo el caso como si fuera 100% remoto.
2. Explica brevemente por qué se escalará a soporte técnico.
3. Puedes dar recomendaciones preventivas o inmediatas simples y seguras.
4. No prometas reparación inmediata.
5. Indica claramente que el caso requiere revisión técnica/presencial o seguimiento especializado.
6. Sé claro, profesional y tranquilizador.
"""
    else:
        modo_escalado = f"""
CATEGORÍA DETECTADA: {categoria}
PRIORIDAD DETECTADA: {prioridad}

INSTRUCCIONES ESPECIALES:
1. Este caso puede intentarse resolver por soporte remoto.
2. Responde paso a paso de forma muy específica.
3. Prioriza verificaciones simples primero.
"""

    return f"""
Eres un agente de soporte técnico llamado CoreDesk AI y estás ayudando a {nombre_usuario}.

{modo_escalado}

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

ESTRUCTURA QUE DEBES SEGUIR SIEMPRE:
- Una línea breve de diagnóstico inicial
- Sección: "🟡 Qué está pasando"
- Sección: "🟢 Qué debes hacer paso a paso"
- Sección: "🔴 Qué no debes hacer" (solo si aplica)
- Sección: "🔵 Qué necesito que me confirmes al final"

PROBLEMA DEL USUARIO:
{prompt_usuario}
"""


def construir_resumen_analisis(analisis):
    etiqueta_escalado = "Sí" if analisis["escalado"] else "No"
    return (
        f"**Clasificación del ticket**\n\n"
        f"- Categoría: **{analisis['categoria']}**\n"
        f"- Prioridad: **{analisis['prioridad']}**\n"
        f"- Escalado: **{etiqueta_escalado}**\n"
        f"- Motivo: {analisis['motivo_escalado']}"
    )


# =========================================================
# 4. MENSAJES DE ERROR
# =========================================================
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


# =========================================================
# 5. CIERRE DE CHAT
# =========================================================
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


def cerrar_chat():
    st.session_state.cerrando_chat = True
    mostrar_overlay_cierre()
    time.sleep(0.9)

    st.session_state.user_data = None
    st.session_state.messages = []
    st.session_state.bienvenida_enviada = False
    st.session_state.ultimo_analisis_ticket = None
    st.session_state.ticket_history = []
    st.session_state.cerrando_chat = False
    st.rerun()


# =========================================================
# 6. INTERFAZ CHAT
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

        analisis = st.session_state.ultimo_analisis_ticket
        if analisis:
            st.info(construir_resumen_analisis(analisis))

        col1, col2, col3 = st.columns([1, 1.1, 1])
        with col2:
            if st.button("Finalizar este chat", key="finalizar-btn", use_container_width=True):
                cerrar_chat()

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
                    # 1. Analizar ticket
                    analisis_ticket = analizar_ticket_hibrido(prompt)
                    st.session_state.ultimo_analisis_ticket = analisis_ticket

                    st.session_state.ticket_history.append({
                        "timestamp": time.time(),
                        "problema": prompt,
                        "analisis": analisis_ticket
                    })

                    # 2. Construir prompt según resultado
                    nombre_usuario = st.session_state.user_data["nombre"]
                    prompt_final = construir_prompt_soporte_hibrido(
                        nombre_usuario,
                        prompt,
                        analisis_ticket
                    )

                    # 3. Generar respuesta
                    respuesta = st.session_state.model.generate_content(prompt_final)
                    texto_respuesta = respuesta.text

                    # 4. Si el ticket fue escalado, prepend visual útil
                    if analisis_ticket["escalado"]:
                        encabezado = (
                            f"🟠 **Este caso fue marcado para escalamiento técnico.**\n\n"
                            f"**Prioridad:** {analisis_ticket['prioridad']}\n\n"
                            f"**Motivo:** {analisis_ticket['motivo_escalado']}\n\n"
                        )
                        texto_respuesta = encabezado + texto_respuesta

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

    if st.session_state.cerrando_chat:
        mostrar_overlay_cierre()


# =========================================================
# 7. FUNCIÓN PRINCIPAL
# =========================================================
def main():
    logo_img = cargar_logo()
    aplicar_estilos()
    configurar_modelo()
    inicializar_sesion()

    if st.session_state.user_data is None:
        mostrar_registro(logo_img)
    else:
        mostrar_chat()
        procesar_input_usuario()


# =========================================================
# 8. EJECUCIÓN
# =========================================================
if __name__ == "__main__":
    main()