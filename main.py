import streamlit as st
import plotly.express as px
from datetime import datetime
import logic 
import style
import pandas as pd

# 1. Configuración de página y estilos
st.set_page_config(page_title="Veterinaria SP", layout="wide", page_icon="🐾")
style.apply_custom_styles()

# --- LÓGICA DE SESIÓN Y MULTICUENTAS ---
if 'auth' not in st.session_state: 
    st.session_state.auth = False
    st.session_state.role = None 

if not st.session_state.auth:
    with st.sidebar:
        st.markdown("### 🔐 Acceso Veterinaria SP")
        u = st.text_input("Usuario")
        p = st.text_input("Clave", type="password")
        
        if st.button("Ingresar", use_container_width=True):
            # CUENTA 1: Administrador (Acceso total)
            if u == "saravialeyva234@gmail.com" and p == "admin2026":
                st.session_state.auth = True
                st.session_state.user = u
                st.session_state.role = "admin"
                st.rerun()
            # CUENTA 2: Estudiante (Restringido)
            elif u == "estudiante@upc.edu.pe" and p == "upc2026":
                st.session_state.auth = True
                st.session_state.user = u
                st.session_state.role = "estudiante"
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
else:
    # --- 2. CONFIGURACIÓN DE URLS (CORREGIDAS) ---
    URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQatK31NMjLR7cXk3RejqLRdDV5Q7-GaGZ7c8_l79nIL_OoacChSSOTQ-ONAFNuKS1l9Lu2CXE25WXc/pub?gid=0&single=true&output=csv"
    # URL Limpia sin caracteres de control
    URL_PRODUCTOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQatK31NMjLR7cXk3RejqLRdDV5Q7-GaGZ7c8_l79nIL_OoacChSSOTQ-ONAFNuKS1l9Lu2CXE25WXc/pub?gid=2137172440&single=true&output=csv"
    
    try:
        data_movimientos = logic.load_data(URL_MOVIMIENTOS)
        ventas_totales = logic.get_ventas_analisis(data_movimientos)
        ahora = datetime.now()
        ventas_mes = ventas_totales[ventas_totales['Fecha'].dt.month == ahora.month]
        
        resumen_stock = pd.read_csv(URL_PRODUCTOS)
        resumen_stock = resumen_stock.rename(columns={'Stock_Actual': 'Cantidad'})

        # --- 3. CABECERA ---
        st.markdown(f"""
            <div style='text-align: center; padding: 20px;'>
                <h1 style='color: #1B5E20; margin-bottom: 0; font-family: sans-serif;'>VETERINARIA SP</h1>
                <p style='color: #666;'>Gestión Profesional de Inventario • {st.session_state.user}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # --- 4. TABS ---
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen", "🏷️ Análisis", "📅 Tendencias", "📦 Inventario"])

        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.session_state.role == "admin":
                    st.metric(label="INGRESOS DEL MES", value=f"S/ {ventas_mes['Monto'].sum():,.2f}")
                else:
                    st.metric(label="INGRESOS DEL MES", value="🔒 Restringido")
                    
            with col2:
                if st.session_state.role == "admin":
                    valor_neto = (resumen_stock['Cantidad'] * resumen_stock['Precio']).sum()
                    st.metric(label="VALOR ALMACÉN", value=f"S/ {valor_neto:,.2f}")
                else:
                    st.metric(label="VALOR ALMACÉN", value="🔒 Restringido")
                    
            with col3:
                st.metric(label="STOCK CRÍTICO", value=len(resumen_stock[resumen_stock['Cantidad'] < 5]))

            st.markdown("<br>", unsafe_allow_html=True)
            c_left, c_right = st.columns([2, 1])
            with c_left:
                st.markdown("<p style='color:#888; font-size:0.9rem; font-weight:600;'>🔥 TOP VENTAS HISTÓRICO</p>", unsafe_allow_html=True)
                top4 = ventas_totales.groupby('Nombre')['Cantidad'].sum().abs().nlargest(4).reset_index()
                fig_top = px.bar(top4, x='Nombre', y='Cantidad', color_discrete_sequence=["#94DD4C"], text_auto=True, template='plotly_white')
                st.plotly_chart(fig_top, use_container_width=True)
            with c_right:
                st.markdown("<p style='color:#888; font-size:0.9rem; font-weight:600;'>⚠️ Bajo en stock</p>", unsafe_allow_html=True)
                st.dataframe(resumen_stock[resumen_stock['Cantidad'] < 5][['Nombre', 'Cantidad']], use_container_width=True, hide_index=True)

        with tab2:
             st.markdown("<br>", unsafe_allow_html=True)
             c1, c2 = st.columns(2)
             with c1:
                # El estudiante ve el gráfico basado en Cantidad, el Admin en Valor Monetario
                valor_col = 'Valor_Neto' if st.session_state.role == "admin" else 'Cantidad'
                if st.session_state.role == "admin":
                    resumen_stock['Valor_Neto'] = resumen_stock['Cantidad'] * resumen_stock['Precio']
                
                fig_pie = px.pie(resumen_stock, values=valor_col, names='Categoria', hole=0.7, 
                                 title=f"Distribución por {valor_col}",
                                 color_discrete_sequence=['#95C06A', '#BDD9A2', '#DEE9CD'], template="plotly_white")
                st.plotly_chart(fig_pie, use_container_width=True)
             with c2:
                ventas_cat = ventas_totales.groupby('Categoria')['Cantidad'].sum().abs().reset_index()
                fig_bar = px.bar(ventas_cat, x='Categoria', y='Cantidad', color_discrete_sequence=['#BDD9A2'], template="plotly_white")
                st.plotly_chart(fig_bar, use_container_width=True)

        with tab3:
            st.markdown("<br>", unsafe_allow_html=True)
            pivot = logic.get_pivot_estacionalidad(ventas_totales)
            if not pivot.empty:
                prod_sel = st.selectbox("Seleccionar item para ver evolución mensual:", pivot.index)
                datos_p = pivot.loc[prod_sel].reset_index()
                datos_p.columns = ['Mes', 'Ventas']
                fig_est = px.line(datos_p, x='Mes', y='Ventas', markers=True, color_discrete_sequence=['#95C06A'], template='plotly_white')
                st.plotly_chart(fig_est, use_container_width=True)

        # --- TAB 4: INVENTARIO BÚSQUEDA REAL-TIME ---
        with tab4:
            st.markdown("<br>", unsafe_allow_html=True)
            busqueda = st.text_input("🔍 Filtrar por nombre...", placeholder="Escribe para buscar...", key="main_search")

            f1, f2, f3 = st.columns(3)
            with f1:
                cat_sel = st.selectbox("Categoría", ["Todas"] + sorted(resumen_stock['Categoria'].unique().tolist()))
            with f2:
                orden_p = st.selectbox("Precio", ["Sin orden", "Menor a Mayor", "Mayor a Menor"])
            with f3:
                orden_s = st.selectbox("Stock", ["Sin orden", "Menor a Mayor", "Mayor a Menor"])

            df_filtered = resumen_stock.copy()
            if busqueda:
                df_filtered = df_filtered[df_filtered['Nombre'].str.contains(busqueda, case=False, na=False)]
            if cat_sel != "Todas":
                df_filtered = df_filtered[df_filtered['Categoria'] == cat_sel]

            # Lógica de Orden
            if orden_p == "Menor a Mayor": df_filtered = df_filtered.sort_values('Precio', ascending=True)
            elif orden_p == "Mayor a Menor": df_filtered = df_filtered.sort_values('Precio', ascending=False)
            if orden_s == "Menor a Mayor": df_filtered = df_filtered.sort_values('Cantidad', ascending=True)
            elif orden_s == "Mayor a Menor": df_filtered = df_filtered.sort_values('Cantidad', ascending=False)

            # Definir columnas visibles según ROL
            cols = ['Nombre', 'Categoria', 'Cantidad']
            if st.session_state.role == "admin":
                cols.insert(2, 'Precio')

            st.dataframe(df_filtered[cols], use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error de conexión: {e}")