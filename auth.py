import streamlit as st
import re
import time

def es_correo_valido(correo):
    patron = r'^[a-zA-Z0-9_.+-]+@(gmail\.com|outlook\.com|hotmail\.com)$'
    return re.match(patron, correo)

def mostrar_registro():
    st.markdown("---")
    col_f1, col_f2, col_f3 = st.columns([1, 3, 1])
    with col_f2:
        with st.form("registro_form"):
            st.subheader("📝 Apertura de Ticket")
            nombre = st.text_input("Nombre Completo:")
            empresa = st.text_input("Empresa / Departamento:")
            correo = st.text_input("Correo Electrónico:")
            
            btn_ingresar = st.form_submit_button("INICIAR SOPORTE")
            
            if btn_ingresar:
                with st.spinner("Validando con el servidor..."):
                    time.sleep(1.2)
                    if not nombre or not empresa or not correo:
                        st.error("❌ Llena todos los campos.")
                    elif not es_correo_valido(correo):
                        st.error("❌ Correo no válido (Gmail/Outlook/Hotmail).")
                    else:
                        st.session_state.user_data = {"nombre": nombre, "empresa": empresa, "correo": correo}
                        st.rerun()