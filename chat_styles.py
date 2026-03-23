import streamlit as st

def aplicar_chat():
    st.markdown("""
        <style>
        /* --- 1. HEADER (Logo Izquierda) --- */
        .header-fixed {
            position: fixed; top: 0; left: 0; width: 100%; height: 70px;
            background: white; z-index: 1000; display: flex;
            align-items: center; padding: 0 5%; border-bottom: 1px solid #EEE;
        }
        .logo-header { max-height: 50px; width: auto; }

        /* --- 2. TARJETA DE USUARIO Y CONTADOR --- */
        .user-card {
            margin-top: 80px; background: white; padding: 15px;
            border-radius: 10px; border-left: 5px solid #0E3255;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            display: flex; justify-content: space-between; align-items: center;
        }

        /* --- 3. BARRA DE CHAT (Clip integrado a la izquierda) --- */
        div[data-testid="stChatInput"] {
            padding-left: 55px !important; /* Espacio para el clip */
        }
        .stPopover {
            position: fixed !important;
            bottom: 42px !important; /* Ajuste para alinear con la flecha */
            left: calc(10% + 25px) !important; 
            z-index: 1001 !important;
        }
        .stPopover button {
            background: transparent !important;
            color: #0E3255 !important;
            border: none !important;
            font-size: 22px !important;
        }

        /* --- 4. BOTÓN X FLOTANTE ROJO (Inferior Izquierda) --- */
        #btn-exit-flotante {
            position: fixed; bottom: 30px; left: 30px;
            width: 65px; height: 65px; background: #FF4B4B;
            border-radius: 50%; display: flex; align-items: center;
            justify-content: center; color: white; font-size: 35px;
            text-decoration: none; z-index: 1005; font-weight: bold;
            box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
            transition: 0.3s ease;
        }
        #btn-exit-flotante:hover { transform: scale(1.1) rotate(90deg); background: #E04141; }
        #btn-exit-flotante:hover::after {
            content: 'Finalizar chat'; position: absolute; left: 80px;
            background: #333; color: white; padding: 5px 12px;
            border-radius: 5px; font-size: 14px; white-space: nowrap;
        }

        /* --- 5. LIMPIEZA DE ICONOS BASURA (smart_toy, etc) --- */
        [data-testid="stIconMaterial"], span[data-testid="stWidgetLabel"], .st-emotion-cache-1ae8k9u { 
            display: none !important; 
        }
        </style>
    """, unsafe_allow_html=True)