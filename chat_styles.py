import streamlit as st

def aplicar_chat():
    st.markdown("""
        <style>
        /* --- 1. LIMPIEZA DE BASURA (smart_toy, expand_more, etc) --- */
        span[data-testid="stWidgetLabel"], 
        .st-emotion-cache-1ae8k9u, 
        .st-emotion-cache-1p6f584 { 
            display: none !important; 
        }

        /* --- 2. BARRA DE CHAT FIJA Y LIMPIA --- */
        div[data-testid="stChatInput"] {
            position: fixed !important;
            bottom: 30px !important;
            background-color: white !important;
            border: 1px solid #ddd !important;
            border-radius: 15px !important;
            z-index: 999 !important;
            width: 70% !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            padding-left: 50px !important; /* Espacio para el clip */
        }

        /* --- 3. EL BOTÓN '+' (Clip) DENTRO DE LA BARRA --- */
        /* Forzamos que el popover del clip flote a la izquierda del input */
        .stPopover {
            position: fixed !important;
            bottom: 42px !important;
            left: calc(15% + 15px) !important;
            z-index: 1000 !important;
        }
        
        .stPopover button {
            background-color: transparent !important;
            border: none !important;
            color: #0E3255 !important;
            font-size: 20px !important;
        }

        /* --- 4. BOTÓN X FLOTANTE (Real y Animado) --- */
        #finalizar-link {
            position: fixed !important;
            bottom: 40px !important;
            left: 40px !important;
            width: 65px !important;
            height: 65px !important;
            background-color: #FF4B4B !important;
            color: white !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 40px !important;
            font-weight: bold !important;
            text-decoration: none !important;
            z-index: 1001 !important;
            box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.4) !important;
            transition: 0.3s !important;
        }

        #finalizar-link:hover {
            transform: scale(1.1) rotate(90deg) !important;
        }

        #finalizar-link:hover::after {
            content: 'Finalizar Chat' !important;
            position: absolute !important;
            left: 75px !important;
            background: #333 !important;
            color: white !important;
            padding: 5px 12px !important;
            border-radius: 5px !important;
            font-size: 14px !important;
            white-space: nowrap !important;
        }

        /* --- 5. TARJETA DE USUARIO --- */
        .user-card-pro {
            background: white !important;
            border-radius: 12px !important;
            padding: 15px !important;
            border-left: 6px solid #0E3255 !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
            margin-top: 10px !important;
        }
        </style>
    """, unsafe_allow_html=True)