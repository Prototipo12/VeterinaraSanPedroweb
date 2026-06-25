import streamlit as st
import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def apply_custom_styles():
    try:
        img_base64 = get_base64_image("assets/images/animales.png")
        background_style = f"""
            background-image: url("data:image/png;base64,{img_base64}");
            background-size: 500px !important;
            background-position: top left;
            background-repeat: repeat !important;
            background-attachment: fixed;
        """
    except FileNotFoundError:
        background_style = "background-color: #F4F7F0 !important;"

    st.markdown(f"""
        <style>
        /* Fondo general */
        html, body, [data-testid="stAppViewContainer"], .stApp {{ {background_style} color: #2D3436 !important; }}
        
        /* Estilos de Gráficos y Métricas */
        div[data-testid="stMetric"], .stDataFrame, div[data-testid="stTable"], div[class*="stPlotlyChart"] {{
            background-color: #F4F7F0 !important;
            border-radius: 15px !important;
            padding: 15px !important;
            border: 2px solid #E9EDDF !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.02) !important;
        }}

        /* Títulos internos */
        .stApp h1, .stApp h2, .stApp h3, [data-testid="stMarkdownContainer"] h1 {{
            color: #3A4A02 !important; font-size: 32px !important; font-weight: 900 !important;
        }}

        /* --- BARRA LATERAL (SIDEBAR) CORREGIDA --- */
        [data-testid="stSidebar"] {{ 
            background-color: #F8F9F7 !important; 
            border-right: 1px solid #E9EDDF !important;
            padding-top: 10px !important;
        }}
        
        /* Eliminación de la caja de usuario */
        .sidebar-user-info {{ 
            padding: 10px 20px !important; 
            margin-bottom: 30px !important; 
            border-bottom: 1px solid #E9EDDF !important;
        }}

        /* SEPARACIÓN DE TABS (Forzando 50px de espacio vertical) */
        div[data-testid="stSidebar"] div[role="radiogroup"] {{
            display: flex !important;
            flex-direction: column !important;
            gap: 50px !important; /* Espacio real entre tabs */
            margin-top: 30px !important;
        }}

        div[data-testid="stSidebar"] div[role="radiogroup"] label {{ 
            background-color: transparent !important; 
            border: none !important; 
            margin: 0px !important; 
            padding: 0 !important; 
        }}
        
        div[data-testid="stSidebar"] div[role="radiogroup"] label p {{ 
            color: #4A4E4D !important; 
            font-size: 18px !important; 
            font-weight: 600 !important; 
        }}
        
        div[data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] p {{ 
            color: #5D7503 !important; 
            font-weight: 900 !important; 
        }}
        
        div[data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"]::before {{ 
            content: "•"; color: #5D7503; margin-right: 15px; font-weight: bold; font-size: 20px;
        }}
        </style>
    """, unsafe_allow_html=True)

def render_header(user_name):
    st.markdown(f"""
    <div style="text-align: center; padding: 0 10px 10px 10px;">
        <h1 style="color: #5D7503; font-size: 24px; font-weight: 900; margin: 0;">Veterinaria SP</h1>
    </div>
    """, unsafe_allow_html=True)