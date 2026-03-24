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

    col1, col2, col3 = st.columns([1, 1.15, 1])

    with col2:
        st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)

        st.markdown('<div class="login-brand-block">', unsafe_allow_html=True)

img_col1, img_col2, img_col3 = st.columns([1, 3, 1])
with img_col2:
    if logo_img:
        st.image(logo_img, width=760)

        st.markdown(
            """
            <p class="login-subtitle">
                Ingresa tus datos para comenzar una sesión de soporte técnico con CoreDesk.
            </p>
            """,
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

        

        with st.form("registro", border=False):
            st.markdown('<div class="login-field-label">Nombre completo</div>', unsafe_allow_html=True)
            nombre = st.text_input(
                "Nombre completo",
                label_visibility="collapsed",
                placeholder="Escribe tu nombre completo"
            )

            st.markdown('<div class="login-field-label">Empresa o área</div>', unsafe_allow_html=True)
            empresa = st.text_input(
                "Empresa o área",
                label_visibility="collapsed",
                placeholder="Ej. Soporte, RH, Finanzas"
            )

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
        st.markdown('</div>', unsafe_allow_html=True)