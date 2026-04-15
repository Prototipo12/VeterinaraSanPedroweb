import pandas as pd

def load_data(url):
    """Carga y limpia los datos base"""
    df = pd.read_csv(url)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes_Año'] = df['Fecha'].dt.to_period('M').astype(str)
    return df

def get_ventas_analisis(df):
    """Filtra solo las salidas (ventas) y calcula montos"""
    ventas = df[df['Cantidad'] < 0].copy()
    ventas['Monto'] = ventas['Cantidad'].abs() * ventas['Precio']
    return ventas

def get_resumen_inventario(df):
    """Agrupa por producto para ver el stock actual"""
    return df.groupby(['Codigo', 'Nombre', 'Categoria', 'Precio']).agg({'Cantidad': 'sum'}).reset_index()

def get_pivot_estacionalidad(ventas_df):
    """Crea la matriz para el análisis mensual por producto"""
    return ventas_df.pivot_table(index='Nombre', columns='Mes_Año', values='Monto', aggfunc='sum').fillna(0)