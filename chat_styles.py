import streamlit as st

def aplicar_chat():
    st.markdown("""
        <style>
        /* --- 1. AJUSTE DE PANTALLA --- */
        .stApp { padding-top: 80px; padding-bottom: 120px; }
        
        /* --- 2. CABECERA --- */
        .header-fixed {
            position: fixed; top: 0; left: 0; width: 100%; height: 70px;
            background-color: white; z-index: 1000;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
            display: flex; align-items: center; padding: 0 5%;
        }

        /* --- 3. BARRA DE CHAT PRO (CLIP INTEGRADO) --- */
        /* Contenedor del input de Streamlit */
        div[data-testid="stChatInput"] {
            position: fixed; bottom: 30px; z-index: 999;
            width: 80% !important; left: 50% !important;
            transform: translateX(-50%) !important;
            background-color: white !important;
            border-radius: 15px !important;
            padding-left: 50px !important; /* Espacio para el + */
        }

        /* El botón "+" o Clip (Popover) */
        /* Lo movemos con absolute para que entre en la barra */
        div[data-testid="stChatInput"] + div, 
        .stPopover {
            position: fixed;
            bottom: 42px; /* Ajuste manual para que quede centrado en la barra */
            left: calc(10% + 25px); /* Depende del ancho del 80% */
            z-index: 1001;
        }
        
        /* Ocultar iconos de material que fallan (smart_toy, etc) */
        span[data-testid="stWidgetLabel"] { display: none !important; }

        /* --- 4. BOTÓN X FLOTANTE (REAL) --- */
        #finalizar-link {
            position: fixed; bottom: 40px; left: 40px;
            width: 60px; height: 60px;
            background-color: #FF4B4B; color: white;
            border-radius: 50%; display: flex;
            align-items: center; justify-content: center;
            font-size: 40px; font-weight: bold;
            text-decoration: none; z-index: 1002;
            box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.4);
            transition: 0.3s;
        }
        #finalizar-link:hover {
            transform: scale(1.1) rotate(90deg);
            background-color: #e04141;
        }
        #finalizar-link:hover::after {
            content: 'Finalizar Chat';
            position: absolute; left: 70px;
            background: #333; color: white;
            font-size: 14px; padding: 5px 10px;
            border-radius: 5px; white-space: nowrap;
        }
        </style>
    """, unsafe_allow_html=True)