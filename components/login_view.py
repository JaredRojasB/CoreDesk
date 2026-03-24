import re
import time
from pathlib import Path
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent


def aplicar_estilos_login():
    ruta_css = BASE_DIR / "styles" / "login.css"
    try:
        with open(ruta_css, "r", encoding="utf-8") as archivo_css:
            css = archivo_css.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"No se encontró el archivo: {ruta_css}")


def limpiar_texto(texto: str) -> str:
    """
    Quita espacios al inicio/final
    y convierte múltiples espacios internos en uno solo.
    """
    return " ".join(texto.strip().split())


def limpiar_correo(correo: str) -> str:
    """
    Quita TODOS los espacios del correo
    y lo pasa a minúsculas.
    """
    return "".join(correo.strip().split()).lower()


def correo_valido(correo: str) -> bool:
    patron = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(patron, correo))


def mostrar_registro(logo_img):
    aplicar_estilos_login()

    outer_left, outer_center, outer_right = st.columns([1, 2.4, 1])

    with outer_center:
        st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)

        if logo_img:
            st.image(logo_img, width=650)

        st.markdown(
            """
            <div class="login-brand-block">
                <p class="login-subtitle">
                    Ingresa tus datos para comenzar una sesión de soporte técnico con CoreDesk.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("registro", border=False):
            st.markdown(
                '<div class="login-field-label">Nombre completo</div>',
                unsafe_allow_html=True
            )
            nombre = st.text_input(
                "Nombre completo",
                label_visibility="collapsed",
                placeholder="Escribe tu nombre completo"
            )

            st.markdown(
                '<div class="login-field-label">Correo electrónico</div>',
                unsafe_allow_html=True
            )
            correo = st.text_input(
                "Correo electrónico",
                label_visibility="collapsed",
                placeholder="ejemplo@empresa.com"
            )

            st.markdown(
                '<div class="login-field-label">Empresa</div>',
                unsafe_allow_html=True
            )
            empresa = st.text_input(
                "Empresa",
                label_visibility="collapsed",
                placeholder="Ej. Meztal, Kare, TrustWell, WaterMark"
            )

            btn_left, btn_center, btn_right = st.columns([1, 1.2, 1])
            with btn_center:
                enviado = st.form_submit_button("Comenzar soporte")

            if enviado:
                nombre_limpio = limpiar_texto(nombre)
                correo_limpio = limpiar_correo(correo)
                empresa_limpia = limpiar_texto(empresa)

                if not nombre_limpio or not correo_limpio or not empresa_limpia:
                    st.warning("Por favor completa todos los campos para continuar.")
                elif not correo_valido(correo_limpio):
                    st.warning("Por favor escribe un correo electrónico válido.")
                else:
                    st.session_state.user_data = {
                        "nombre": nombre_limpio,
                        "correo": correo_limpio,
                        "empresa": empresa_limpia,
                        "inicio": time.time()
                    }

        st.markdown('</div>', unsafe_allow_html=True)