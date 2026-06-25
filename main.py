import streamlit as st
import plotly.express as px
from datetime import datetime
import pandas as pd
import numpy as np
import logic 
import style

# Confi inicial
st.set_page_config(page_title="Veterinaria SP - Dashboard", layout="wide", page_icon="🐾")

# estilos globales
style.apply_custom_styles()

# Gestion en login
if 'auth' not in st.session_state: 
    st.session_state.auth = False
    st.session_state.role = None

# Autenticacion
if not st.session_state.auth:
    with st.sidebar:
        st.markdown("### 🔐 Acceso al Sistema")
        u = st.text_input("Usuario")
        p = st.text_input("Clave", type="password")
        
        if st.button("Ingresar", use_container_width=True):
            if u == "HYGvets" and p == "adminVet1":
                st.session_state.auth = True
                st.session_state.user = u
                st.session_state.role = "admin"
                st.rerun()
            elif u == "prac20" and p == "practicante2026":
                st.session_state.auth = True
                st.session_state.user = u
                st.session_state.role = "estudiante"
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
else:
    URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQatK31NMjLR7cXk3RejqLRdDV5Q7-GaGZ7c8_l79nIL_OoacChSSOTQ-ONAFNuKS1l9Lu2CXE25WXc/pub?gid=0&single=true&output=csv"
    URL_PRODUCTOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQatK31NMjLR7cXk3RejqLRdDV5Q7-GaGZ7c8_l79nIL_OoacChSSOTQ-ONAFNuKS1l9Lu2CXE25WXc/pub?gid=2137172440&single=true&output=csv"

    try:
        data_movimientos = logic.load_data(URL_MOVIMIENTOS)
        ventas_totales = logic.get_ventas_analisis(data_movimientos)
        ahora = datetime.now()
        ventas_mes = ventas_totales[ventas_totales['Fecha'].dt.month == ahora.month]
        resumen_stock = pd.read_csv(URL_PRODUCTOS)
        resumen_stock = resumen_stock.rename(columns={'Stock_Actual': 'Cantidad'})

        # --- BARRA LATERAL (SIDEBAR) REORGANIZADA CON ESPACIADO ---
        with st.sidebar:
            # 1. Título bien arriba
            style.render_header(st.session_state.user)
            
            # Espaciado extra
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            
            # 2. Bloque de Sesión con margen inferior para separar de los tabs
            st.markdown(f"""
                <div class="sidebar-status" style='margin-bottom: 30px;'>
                    <p style='margin:0; font-size:0.85rem; color:#2D3436; font-weight:bold;'>👤 {st.session_state.user}</p>
                    <p style='margin:0; font-size:0.75rem; color:#636E72;'>ROL: {st.session_state.role.upper()}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # 3. Navegación
            opcion_menu = st.radio(
                "Navegación",
                options=["📊 Resumen General", "🏷️ Inteligencia de Ventas", "📅 Tendencias Históricas", "📦 Inventario"],
                label_visibility="collapsed"
            )
            
            # Espaciado flexible para empujar el botón al final
            st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
            
            # 4. Cerrar sesión
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state.clear()
                st.rerun()

        # --- LÓGICA DE CONTENIDO ---
        if opcion_menu == "📊 Resumen General":
            st.markdown("### 📊 Resumen General")
            
            # Filtros Mes/Año
            anios = sorted(ventas_totales['Fecha'].dt.year.unique(), reverse=True)
            col_f1, col_f2 = st.columns(2)
            with col_f1: anio_sel = st.selectbox("Seleccionar Año:", anios)
            with col_f2: 
                meses_disp = sorted(ventas_totales[ventas_totales['Fecha'].dt.year == anio_sel]['Fecha'].dt.month.unique())
                mes_sel = st.selectbox("Seleccionar Mes:", meses_disp, format_func=lambda x: pd.to_datetime(x, format='%m').strftime('%B'))
            
            datos = ventas_totales[(ventas_totales['Fecha'].dt.year == anio_sel) & (ventas_totales['Fecha'].dt.month == mes_sel)]
            
            # Métricas
            col1, col2, col3 = st.columns(3)
            col1.metric(f"INGRESOS {pd.to_datetime(mes_sel, format='%m').strftime('%B').upper()}", f"S/ {datos['Monto'].sum():,.2f}" if st.session_state.role == "admin" else "🔒")
            col2.metric("VALOR ALMACÉN", f"S/ {(resumen_stock['Cantidad'] * resumen_stock['Precio']).sum():,.2f}")
            col3.metric("PRODUCTOS CRÍTICOS", len(resumen_stock[resumen_stock['Cantidad'] < 5]))

            # Gráfico y Tabla
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"**🔥 TOP PRODUCTOS EN {pd.to_datetime(mes_sel, format='%m').strftime('%B').upper()}**")
                top = np.abs(datos.groupby('Nombre')['Cantidad'].sum()).nlargest(4).reset_index()
                fig = px.bar(top, x='Nombre', y='Cantidad', color='Cantidad', color_continuous_scale='Greens', text_auto=True)
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.markdown("**⚠️ REPOSICIÓN**")
                st.dataframe(resumen_stock[resumen_stock['Cantidad'] < 5][['Nombre', 'Cantidad']], use_container_width=True, hide_index=True)

        elif opcion_menu == "🏷️ Inteligencia de Ventas":
            st.markdown("### 🔍 Inteligencia de Datos")
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                cat_ana = st.multiselect("Categorías:", options=resumen_stock['Categoria'].unique(), default=resumen_stock['Categoria'].unique())
            with c_f2:
                prods_disponibles = resumen_stock[resumen_stock['Categoria'].isin(cat_ana)]['Nombre'].unique()
                prod_ana = st.multiselect("Productos específicos:", options=prods_disponibles, default=None)

            df_v_f = ventas_totales[ventas_totales['Categoria'].isin(cat_ana)].copy()
            if prod_ana:
                df_v_f = df_v_f[df_v_f['Nombre'].isin(prod_ana)]

            if not df_v_f.empty:
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Unidades Vendidas", f"{np.abs(df_v_f['Cantidad'].sum()):,.0f}")
                if st.session_state.role == "admin":
                    m2.metric("Ingreso Total", f"S/ {df_v_f['Monto'].sum():,.2f}")
                    m3.metric("Ticket Promedio", f"S/ {(df_v_f['Monto'].sum()/len(df_v_f)):,.2f}")
                ventas_mensuales = np.abs(df_v_f.groupby(df_v_f['Fecha'].dt.to_period('M'))['Cantidad'].sum())
                prediccion = ventas_mensuales.mean() if not ventas_mensuales.empty else 0
                m4.metric("Predicción Próx. Mes", f"~{prediccion:,.0f} und")

                st.markdown("---")
                g1, g2 = st.columns(2)
                with g1:
                    df_pie = df_v_f.groupby('Categoria')['Cantidad'].sum().abs().reset_index()
                    fig_pie_v = px.pie(df_pie, values='Cantidad', names='Categoria', hole=0.4, title="Mix de Ventas (Porcentaje)")
                    fig_pie_v.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_pie_v, use_container_width=True)
                with g2:
                    top_prod_filtro = df_v_f.groupby('Nombre')['Cantidad'].sum().abs().nlargest(10).reset_index()
                    fig_bar_v = px.bar(top_prod_filtro, x='Cantidad', y='Nombre', orientation='h', title="Top 10 en selección", color='Cantidad', color_continuous_scale='Greens')
                    fig_bar_v.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_bar_v, use_container_width=True)
            else:
                st.warning("Selecciona criterios para ver el análisis.")

        elif opcion_menu == "📅 Tendencias Históricas":
            st.markdown("### 📅 Tendencias Históricas")
            pivot = logic.get_pivot_estacionalidad(ventas_totales)
            if not pivot.empty:
                prod_sel = st.selectbox("Comportamiento mensual de:", pivot.index)
                datos_p = pivot.loc[prod_sel].reset_index()
                datos_p.columns = ['Mes', 'Ventas']
                fig_est = px.line(datos_p, x='Mes', y='Ventas', markers=True, title=f"Histórico: {prod_sel}")
                fig_est.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_est, use_container_width=True)

        elif opcion_menu == "📦 Inventario":
            st.markdown("### 📦 Gestión de Stock - OASIS Pet Tracker")
            busqueda_texto = st.text_input("🔍 Buscar producto por nombre:", placeholder="Escribe el nombre del producto...", key="main_search_v10")
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            with c1:
                categorias = ["Todas"] + sorted(resumen_stock['Categoria'].unique().tolist())
                cat_sel = st.selectbox("Categoría", categorias, key="cat_drop_final")
            with c2:
                ord_stock = st.selectbox("Orden Stock", ["Sin orden", "Menor a Mayor", "Mayor a Menor"], key="stock_drop_final")
            with c3:
                ord_price = st.selectbox("Orden Precio", ["Sin orden", "Menor a Mayor", "Mayor a Menor"], key="price_drop_final")

            df_inv = resumen_stock.copy()
            if busqueda_texto:
                df_inv = df_inv[df_inv['Nombre'].str.contains(busqueda_texto, case=False, na=False)]
            if cat_sel != "Todas":
                df_inv = df_inv[df_inv['Categoria'] == cat_sel]
            if ord_stock == "Menor a Mayor":
                df_inv = df_inv.sort_values('Cantidad', ascending=True)
            elif ord_stock == "Mayor a Menor":
                df_inv = df_inv.sort_values('Cantidad', ascending=False)
            if ord_price == "Menor a Mayor":
                df_inv = df_inv.sort_values('Precio', ascending=True)
            elif ord_price == "Mayor a Menor":
                df_inv = df_inv.sort_values('Precio', ascending=False)

            st.dataframe(df_inv[['Nombre', 'Categoria', 'Precio', 'Cantidad']], use_container_width=True, hide_index=True, column_config={"Precio": st.column_config.NumberColumn("Precio (S/)", format="S/ %.2f"), "Cantidad": st.column_config.NumberColumn("Stock", format="%d und.")})
            st.caption(f"Mostrando {len(df_inv)} productos en inventario.")
            
    except Exception as e:
        st.error(f"Error de conexión: {e}")