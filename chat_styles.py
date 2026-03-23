import streamlit as st

def aplicar_chat():
    st.markdown("""
        <style>
        /* ==========================================
           1. CABECERA FIJA Y LOGO (Izq)
           ========================================== */
        .stApp { padding-top: 80px; padding-bottom: 120px; } /* Espacio para header y input */

        .header-fixed {
            position: fixed; top: 0; left: 0; width: 100%; height: 70px;
            background-color: white; z-index: 999;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.03);
            display: flex; align-items: center; padding: 0 5%;
        }
        .logo-chat { max-height: 50px; width: auto; }

        /* ==========================================
           2. TARJETA DE USUARIO CON CONTADOR
           ========================================== */
        .user-card-formal {
            background-color: #ffffff; padding: 15px 20px;
            border-radius: 12px; box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
            border-left: 5px solid #0E3255; margin-bottom: 25px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .user-card-data { color: #0E3255; font-size: 16px; font-weight: 600; }
        .counter-box { text-align: right; color: #6c757d; font-size: 12px; }

        /* ==========================================
           3. IDENTIDAD DE CHAT (Burbujas)
           ========================================== */
        .stChatMessage { 
            border-radius: 20px; background-color: #fcfcfc;
            box-shadow: 0px 1px 4px rgba(0,0,0,0.02); margin-bottom: 12px;
        }

        /* ==========================================
           4. BARRA DE CHAT FIJA CON EL CLIP INTEGRADO
           ========================================= */
        div[data-testid="stChatInput"] {
            position: fixed; bottom: 30px; z-index: 998;
            background-color: white; border-top: 1px solid #eee;
            padding: 10px 0; width: 85%;
            left: 50%; transform: translateX(-50%);
            border-radius: 15px; box-shadow: 0px -5px 15px rgba(0,0,0,0.03);
            padding-left: 55px !important; /* Espacio para el clip dentro */
        }

        /* El clip (Popover) LITERALMENTE dentro del input (al inicio) */
        button[data-testid="stBaseButton-headerNoPadding"] {
            position: absolute; left: 10px; top: 50%;
            transform: translateY(-50%);
            border-radius: 5px; background-color: transparent !important;
            color: #0E3255 !important; /* Azul CoreDesk */
            font-size: 20px !important; z-index: 1000;
        }

        /* ==========================================
           5. BOTÓN FLOTANTE 'X' (FIX DEFINITIVO)
           ========================================= */
        /* Usamos CSS crudo para crear el botón, no un botón de Streamlit */
        #finalizar-btn-flotante {
            position: fixed;
            bottom: 40px;
            left: 40px;
            width: 70px;
            height: 70px;
            background-color: #FF4B4B;
            border-radius: 50%;
            box-shadow: 0px 5px 15px rgba(255, 75, 75, 0.4);
            cursor: pointer;
            z-index: 1001;
            transition: 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            border: none;
        }
        
        /* La X enorme dentro del botón */
        #finalizar-btn-flotante::before {
            content: '×'; /* Carácter de multiplicación */
            color: white; font-size: 50px; font-weight: 300;
        }

        /* LEYENDA FLOTANTE AL PASAR EL MOUSE (Hover) */
        #finalizar-btn-flotante:hover::after {
            content: 'Finalizar chat';
            position: absolute; left: 85px;
            background-color: #333; color: white;
            padding: 5px 12px; border-radius: 5px;
            font-size: 14px; white-space: nowrap;
        }

        #finalizar-btn-flotante:hover {
            transform: scale(1.1) rotate(90deg); /* Gira y crece */
            background-color: #e04141;
        }
        </style>
    """, unsafe_allow_html=True)