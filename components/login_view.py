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
                '<div class="login-field-label">Empresa o área</div>',
                unsafe_allow_html=True
            )
            empresa = st.text_input(
                "Empresa o área",
                label_visibility="collapsed",
                placeholder="Ej. Soporte, RH, Finanzas"
            )

            btn_left, btn_center, btn_right = st.columns([1, 1.2, 1])
            with btn_center:
                enviado = st.form_submit_button("Comenzar soporte")

            if enviado:
                if nombre and empresa:
                    st.session_state.user_data = {
                        "nombre": nombre,
                        "empresa": empresa,
                        "inicio": time.time()
                    }
                else:
                    st.warning("Por favor completa ambos campos para continuar.")

        st.markdown('</div>', unsafe_allow_html=True)