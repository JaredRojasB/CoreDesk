import streamlit as st

def aplicar_estilos_chat():
    """Estilos EXCLUSIVOS para la interfaz de chat activa"""
    st.markdown("""
        <style>
        /* ==========================================
           1. CABECERA FIJA (Header)
           ========================================== */
        .header-fixed {
            position: fixed; top: 0; left: 0; width: 100%; height: 80px;
            background-color: white; z-index: 1000;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.03);
            display: flex; align-items: center;
            justify-content: space-between; padding: 0 5%;
        }

        /* Logo LEGISLBLE (120px) y a la Izquierda */
        .logo-chat-legible {
            max-height: 120px; /* Tamaño perfecto y equilibrado */
            width: auto;
        }

        /* Botón Finalizar ROJO (Forzado con !important) */
        /* Detectamos el tipo secondary de Streamlit y lo cambiamos */
        button[kind="secondary"] {
            background-color: #FF4B4B !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.6rem 1.5rem !important;
            font-weight: bold !important;
            font-size: 15px !important;
            transition: 0.3s;
        }
        button[kind="secondary"]:hover {
            background-color: #e04141 !important;
        }

        /* ==========================================
           2. IDENTIDAD DE CHAT (Grid y burbujas)
           ========================================== */
        /* Agregamos padding al fondo de la app para no tapar los mensajes fijos */
        .main { padding-top: 100px; padding-bottom: 160px; }

        /* Estilo de burbujas de chat limpias (como te gustaba antes) */
        .stChatMessage { 
            border-radius: 20px; 
            background-color: #fcfcfc;
            box-shadow: 0px 1px 4px rgba(0,0,0,0.03);
            margin-bottom: 12px;
        }

        /* Contenedor del nombre de usuario sutil arriba */
        .user-tag-chat {
            color: #6c757d; font-size: 14px;
            text-align: left; margin-bottom: 15px;
        }

        /* ==========================================
           3. BARRA DE CHAT FIJA ABAJO CON EL CLIP
           ========================================== */
        div[data-testid="stChatInput"] {
            position: fixed; bottom: 30px; z-index: 999;
            background-color: white; border-top: 1px solid #ddd;
            padding: 10px 0; width: 85%; /* Ancho controlado */
            left: 50%; transform: translateX(-50%);
            border-radius: 15px; box-shadow: 0px -5px 15px rgba(0,0,0,0.05);
        }

        /* Estilo del clip (Popover) integrado visualmente en la barra */
        button[data-testid="stBaseButton-headerNoPadding"] {
            border-radius: 5px;
            background-color: #e9ecef !important;
            color: #495057 !important;
        }
        </style>
    """, unsafe_allow_html=True)