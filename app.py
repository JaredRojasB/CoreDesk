import streamlit.components.v1 as components
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
# 3. UTILIDADES
# =========================================================
def normalizar_texto(texto: str) -> str:
    return " ".join(texto.lower().strip().split())


def formatear_tiempo_sesion(segundos_totales: int) -> str:
    minutos = segundos_totales // 60
    segundos = segundos_totales % 60
    return f"{minutos:02d}:{segundos:02d}"


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


# =========================================================
# 4. LÓGICA HÍBRIDA DE CLASIFICACIÓN
# =========================================================
def analizar_prioridad_por_palabras_clave(prompt_usuario: str):
    """
    Regla rápida por palabras clave.
    Clasifica entre:
    - resoluble por chat
    - intentar remoto y escalar si falla
    - escalar inmediato
    """
    texto = normalizar_texto(prompt_usuario)

    palabras_escalado_inmediato = [
        "pantalla rota", "se rompio la pantalla", "pantalla quebrada", "quebrada",
        "huele a quemado", "olor a quemado", "equipo quemado",
        "motherboard", "placa madre", "fuente dañada", "fuente danada",
        "ram dañada", "ram danada", "aumentar ram", "cambiar ram",
        "cambiar disco", "disco duro roto", "ssd roto", "hace ruido el disco",
        "disco dañado", "disco danado", "liquido derramado", "se mojo",
        "se cayó", "se cayo", "golpe fuerte", "pieza rota", "carcasa rota",
        "pantalla estrellada", "bisagra rota", "tecla rota"
    ]

    palabras_escalar_si_falla = [
        "no enciende", "equipo no enciende", "no arranca", "equipo muerto",
        "pantalla azul", "pantallazo azul constante", "blue screen",
        "equipo se apaga solo", "se apaga solo", "se reinicia",
        "sin internet", "no tengo internet", "outlook no abre", "no puedo entrar",
        "no tengo acceso", "correo no funciona", "vpn no conecta",
        "no puedo conectarme", "error constante", "equipo muy lento",
        "muy lento", "se traba mucho", "impresora no imprime", "luz roja parpadeante",
        "no da imagen", "no prende bien", "no inicia windows"
    ]

    palabras_medias = [
        "impresora", "audio", "camara", "cámara", "office", "excel", "word",
        "instalar programa", "instalar software", "configurar", "microfono", "micrófono",
        "periférico", "periferico", "monitor", "teclado", "mouse", "firma",
        "correo", "outlook", "teams", "zoom"
    ]

    palabras_bajas = [
        "duda", "consulta", "como", "cómo", "configurar firma",
        "cambiar fondo", "personalizar", "quiero saber", "informacion", "información"
    ]

    categoria = "Software"
    prioridad = "Media"
    escalado_inmediato = False
    escalar_si_falla = False
    motivo = "Caso general pendiente de validación."
    confianza = "media"

    if any(p in texto for p in palabras_escalado_inmediato):
        prioridad = "Crítica"
        categoria = "Hardware"
        escalado_inmediato = True
        escalar_si_falla = False
        motivo = "Se detectó un caso físico o presencial que requiere intervención técnica directa."
        confianza = "alta"

    elif any(p in texto for p in palabras_escalar_si_falla):
        prioridad = "Alta"
        categoria = "Soporte general"
        escalado_inmediato = False
        escalar_si_falla = True
        motivo = "Primero pueden intentarse pruebas remotas seguras; si no funcionan, debe escalarse."
        confianza = "media"

    elif any(p in texto for p in palabras_medias):
        prioridad = "Media"
        categoria = "Soporte general"
        escalado_inmediato = False
        escalar_si_falla = False
        motivo = "Caso operativo que probablemente puede resolverse por guía remota."
        confianza = "media"

    elif any(p in texto for p in palabras_bajas):
        prioridad = "Baja"
        categoria = "Consulta"
        escalado_inmediato = False
        escalar_si_falla = False
        motivo = "Se detectó una solicitud informativa o de baja urgencia."
        confianza = "media"

    return {
        "categoria": categoria,
        "prioridad": prioridad,
        "escalado_inmediato": escalado_inmediato,
        "escalar_si_falla": escalar_si_falla,
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
- escalado_inmediato
- escalar_si_falla
- motivo_escalado
- confianza

Reglas:
- categoria debe ser una de estas:
  "Hardware", "Software", "Red", "Acceso", "Correo", "Consulta", "Otro"

- prioridad debe ser una de estas:
  "Baja", "Media", "Alta", "Crítica"

- escalado_inmediato debe ser true o false
- escalar_si_falla debe ser true o false

- motivo_escalado debe explicar brevemente la decisión
- confianza debe ser una de estas:
  "baja", "media", "alta"

Criterios IMPORTANTES:
1. escalado_inmediato = true SOLO si el caso parece físico, riesgoso o claramente presencial:
   - pantalla rota
   - olor a quemado
   - piezas dañadas
   - aumento/cambio de RAM o disco
   - motherboard
   - fallas eléctricas
   - daño físico
   - ruido mecánico del disco
   - líquido derramado
2. escalar_si_falla = true si el caso parece serio, pero todavía admite pruebas remotas iniciales seguras:
   - no enciende
   - no arranca
   - pantalla azul
   - equipo lento
   - sin internet
   - Outlook no abre
   - errores de acceso
   - impresora no imprime
3. Si puede resolverse completamente por chat, ambos deben ser false.
4. Nunca pongas escalado_inmediato y escalar_si_falla como true al mismo tiempo.

TICKET:
{prompt_usuario}
"""
    respuesta = st.session_state.model.generate_content(instruccion)
    texto = respuesta.text.strip()
    texto = texto.replace("```json", "").replace("```", "").strip()
    data = json.loads(texto)

    return {
        "categoria": str(data.get("categoria", "Otro")).strip(),
        "prioridad": str(data.get("prioridad", "Media")).strip(),
        "escalado_inmediato": bool(data.get("escalado_inmediato", False)),
        "escalar_si_falla": bool(data.get("escalar_si_falla", False)),
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

        prioridad_orden = {"Baja": 1, "Media": 2, "Alta": 3, "Crítica": 4}

        prioridad_base = prioridad_orden.get(analisis_base["prioridad"], 2)
        prioridad_ia = prioridad_orden.get(analisis_ia["prioridad"], 2)

        prioridad_final = analisis_ia["prioridad"] if prioridad_ia >= prioridad_base else analisis_base["prioridad"]
        categoria_final = analisis_ia["categoria"] or analisis_base["categoria"]

        escalado_inmediato_final = (
            analisis_base["escalado_inmediato"] or analisis_ia["escalado_inmediato"]
        )

        escalar_si_falla_final = False
        if not escalado_inmediato_final:
            escalar_si_falla_final = (
                analisis_base["escalar_si_falla"] or analisis_ia["escalar_si_falla"]
            )

        if escalado_inmediato_final:
            motivo_final = (
                analisis_ia["motivo_escalado"]
                if analisis_ia["escalado_inmediato"]
                else analisis_base["motivo_escalado"]
            )
        elif escalar_si_falla_final:
            motivo_final = (
                analisis_ia["motivo_escalado"]
                if analisis_ia["escalar_si_falla"]
                else analisis_base["motivo_escalado"]
            )
        else:
            motivo_final = analisis_ia["motivo_escalado"] or analisis_base["motivo_escalado"]

        return {
            "categoria": categoria_final,
            "prioridad": prioridad_final,
            "escalado_inmediato": escalado_inmediato_final,
            "escalar_si_falla": escalar_si_falla_final,
            "motivo_escalado": motivo_final,
            "confianza": analisis_ia["confianza"],
            "fuente": "hibrido"
        }

    except Exception:
        return analisis_base


def construir_prompt_soporte_hibrido(nombre_usuario, prompt_usuario, analisis_ticket):
    categoria = analisis_ticket["categoria"]
    prioridad = analisis_ticket["prioridad"]
    escalado_inmediato = analisis_ticket["escalado_inmediato"]
    escalar_si_falla = analisis_ticket["escalar_si_falla"]
    motivo_escalado = analisis_ticket["motivo_escalado"]

    if escalado_inmediato:
        modo = f"""
IMPORTANTE:
Este ticket fue clasificado como ESCALADO INMEDIATO.

CATEGORÍA DETECTADA: {categoria}
PRIORIDAD DETECTADA: {prioridad}
MOTIVO: {motivo_escalado}

INSTRUCCIONES ESPECIALES:
1. NO intentes resolverlo por completo como si fuera 100% remoto.
2. Explica brevemente por qué requiere revisión técnica/presencial.
3. Puedes dar recomendaciones seguras y básicas mientras espera soporte.
4. No prometas reparación inmediata.
5. Sé claro, profesional y tranquilizador.
"""
    elif escalar_si_falla:
        modo = f"""
IMPORTANTE:
Este ticket NO debe escalarse de inmediato.
Primero deben intentarse pruebas remotas iniciales seguras.

CATEGORÍA DETECTADA: {categoria}
PRIORIDAD DETECTADA: {prioridad}
MOTIVO: {motivo_escalado}

INSTRUCCIONES ESPECIALES:
1. Da pasos iniciales simples, seguros y muy claros.
2. Prioriza verificaciones básicas primero.
3. Al final, indica claramente que si esas pruebas no funcionan, el caso deberá escalarse a soporte técnico.
4. No declares escalamiento inmediato desde el inicio.
"""
    else:
        modo = f"""
CATEGORÍA DETECTADA: {categoria}
PRIORIDAD DETECTADA: {prioridad}

INSTRUCCIONES ESPECIALES:
1. Este caso puede intentarse resolver por soporte remoto.
2. Responde paso a paso de forma muy específica.
3. Prioriza verificaciones simples primero.
"""

    return f"""
Eres un agente de soporte técnico llamado CoreDesk AI y estás ayudando a {nombre_usuario}.

{modo}

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
    escalado_inmediato = "Sí" if analisis["escalado_inmediato"] else "No"
    escalar_si_falla = "Sí" if analisis["escalar_si_falla"] else "No"

    return (
        f"**Clasificación del ticket**\n\n"
        f"- Categoría: **{analisis['categoria']}**\n"
        f"- Prioridad: **{analisis['prioridad']}**\n"
        f"- Escalado inmediato: **{escalado_inmediato}**\n"
        f"- Escalar si falla: **{escalar_si_falla}**\n"
        f"- Motivo: {analisis['motivo_escalado']}"
    )


# =========================================================
# 5. MENSAJES DE ERROR
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


# =========================================================
# 6. CIERRE DE CHAT
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
# 7. INTERFAZ CHAT
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


def mover_vista_al_inicio_respuesta():
    components.html(
        """
        <script>
            const doc = window.parent.document;
            const win = window.parent;

            const restoreScroll = () => {
                const markers = doc.querySelectorAll('.assistant-start-marker');
                if (!markers.length) return;

                const lastMarker = markers[markers.length - 1];
                const rect = lastMarker.getBoundingClientRect();
                const targetTop = win.scrollY + rect.top - 110;

                // Quita foco del input para que no empuje la vista hacia abajo
                if (doc.activeElement) {
                    doc.activeElement.blur();
                }

                // Fuerza scroll al inicio de la respuesta
                win.scrollTo({
                    top: Math.max(0, targetTop),
                    behavior: "auto"
                });
            };

            setTimeout(restoreScroll, 50);
            setTimeout(restoreScroll, 150);
            setTimeout(restoreScroll, 300);
            setTimeout(restoreScroll, 600);
            setTimeout(restoreScroll, 1000);
        </script>
        """,
        height=0,
    )

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

        with st.chat_message("assistant", avatar=avatar):
            st.markdown('<div class="assistant-start-marker"></div>', unsafe_allow_html=True)

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

                    # 4. Encabezado visual según estrategia
                    if analisis_ticket["escalado_inmediato"]:
                        encabezado = (
                            f"🟠 **Este caso fue marcado para escalamiento técnico inmediato.**\n\n"
                            f"**Prioridad:** {analisis_ticket['prioridad']}\n\n"
                            f"**Motivo:** {analisis_ticket['motivo_escalado']}\n\n"
                        )
                        texto_respuesta = encabezado + texto_respuesta

                    elif analisis_ticket["escalar_si_falla"]:
                        encabezado = (
                            f"🟡 **Este caso primero intentará resolverse por chat.**\n\n"
                            f"**Prioridad:** {analisis_ticket['prioridad']}\n\n"
                            f"**Nota:** si las pruebas iniciales no funcionan, el caso deberá escalarse.\n\n"
                        )
                        texto_respuesta = encabezado + texto_respuesta

                    st.markdown(texto_respuesta)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": texto_respuesta
                    })

                    mover_vista_al_inicio_respuesta()

                except Exception as e:
                    mensaje_error = construir_mensaje_error_amigable(e)
                    st.markdown(mensaje_error)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": mensaje_error
                    })


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
# 8. FUNCIÓN PRINCIPAL
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
# 9. EJECUCIÓN
# =========================================================
if __name__ == "__main__":
    main()