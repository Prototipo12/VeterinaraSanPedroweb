import pandas as pd
import streamlit as st
import datetime
import numpy as np
import requests
import json


# 1. EXCEPCIONES PERSONALIZADAS (Excepciones)

class ErrorDatoInvalido(Exception):
    """Excepción lanzada cuando los datos de entrada no son válidos."""
    pass

class ErrorStockCritico(Exception):
    """Excepción lanzada cuando el stock alcanza niveles críticos."""
    pass

# GESTIÓN DE USUARIOS

class Usuario:
    """Clase base para representar a un usuario del sistema."""
    def __init__(self, id_usuario, username, password, role):
        self.id_usuario = int(id_usuario)
        self.username = str(username).strip().lower()
        self.password = str(password).strip()
        self.role = str(role).strip().lower() # 'admin' o 'estudiante'

    def verificar_credenciales(self, user, pwd):
        return self.username == str(user).strip().lower() and self.password == str(pwd).strip()#dverifica lso credenciales segun el app scrip


class GestorUsuarios:
    """Clase que administra la colección de usuarios conectada a Google Sheets y Apps Script."""
    def __init__(self, url_usuarios_sheets=None, url_apps_script=None):
        self.url_sheets = url_usuarios_sheets
        self.url_apps_script = url_apps_script
        self.usuarios = []
        self.cargar_usuarios()

    def cargar_usuarios(self):
        """Carga los usuarios desde la fuente web pública de Google Sheets."""
        try:
            if self.url_sheets:
                df_users = pd.read_csv(self.url_sheets)
                self.usuarios = []
                for _, row in df_users.iterrows():
                    self.usuarios.append(
                        Usuario(row['ID'], row['Usuario'], row['Clave'], row['Rol'])
                    )
            else:
                raise Exception("Sin URL")
        except Exception as e:
            # Respaldo por defecto si falla la red
            self.usuarios = [
                Usuario(1, "UserAdmin", "adminVet1", "admin"),
                Usuario(2, "Userprac", "practicante2026", "estudiante")
            ]

    def autenticar(self, username, password):
        """Verifica las credenciales del usuario."""
        for user_obj in self.usuarios:
            if user_obj.verificar_credenciales(username, password):
                return user_obj.role
        return None

    def registrar_practicante(self, username, password):
        """Registra un nuevo practicante enviándolo a Google Apps Script para que se guarde en el Sheet."""
        username_limpio = str(username).strip().lower()
        
        for user_obj in self.usuarios:
            if user_obj.username == username_limpio:
                raise ErrorDatoInvalido("El nombre de usuario ya existe en el sistema.")
        
        if not username or not password:
            raise ErrorDatoInvalido("El usuario y la contraseña no pueden estar vacíos.")

        # Estructura de datos para el Apps Script
        payload = {
            "action": "registrar_usuario",
            "username": username_limpio,
            "password": str(password).strip(),
            "role": "estudiante"
        }

        try:
            if self.url_apps_script:
                # esto envia la petición POST al Apps Script
                response = requests.post(self.url_apps_script, json=payload)
                resultado = response.json()
                
                if resultado.get("status") == "success":
                    # Recarga la lista desde Sheets para traer el nuevo usuario registrado
                    self.cargar_usuarios()
                    return True
                else:
                    raise Exception("Error en el servidor de Apps Script.")
            else:
                raise Exception("Falta configurar la URL de Apps Script.")
        except Exception as err:
            raise ErrorDatoInvalido(f"No se pudo guardar en Google Sheets: {err}")

# 2. CLASES, HERENCIA Y POLIMORFISMO

class Producto:
    """Clase base que representa un producto general de la veterinaria."""
    def __init__(self, nombre, categoria, precio, cantidad):
        self.nombre = str(nombre).lower().strip()
        self.categoria = str(categoria).strip()
        
        # Control de excepciones en atributos numéricos
        try:
            self.precio = float(precio)
            self.cantidad = int(cantidad)
            if self.precio < 0 or self.cantidad < 0:
                raise ErrorDatoInvalido("El precio y la cantidad no pueden ser negativos.")
        except ValueError:
            raise ErrorDatoInvalido("Precio o cantidad deben ser valores numéricos válidos.")

    def evaluar_alerta(self):
        """Método base para evaluar alertas de stock (Polimorfismo)."""
        return self.cantidad < 5

    def obtener_detalles(self):
        return f"Producto: {self.nombre} | Categoría: {self.categoria} | Stock: {self.cantidad}"


class ProductoFarmaceutico(Producto):
    """Clase derivada (Herencia) para productos de farmacia/medicamentos."""
    def __init__(self, nombre, categoria, precio, cantidad, requiere_receta=True):
        super().__init__(nombre, categoria, precio, cantidad)
        self.requiere_receta = requiere_receta

    # Polimorfismo: Sobrescribe la evaluación de alerta (ej: stock crítico más estricto para fármacos)
    def evaluar_alerta(self):
        return self.cantidad < 10

    def obtener_detalles(self):
        receta_txt = "Sí" if self.requiere_receta else "No"
        return f"[FARMACIA] {super().obtener_detalles()} | Receta: {receta_txt}"


class ProductoAccesorio(Producto):
    """Clase derivada (Herencia) para accesorios y juguetes."""
    def __init__(self, nombre, categoria, precio, cantidad, material="Estándar"):
        super().__init__(nombre, categoria, precio, cantidad)
        self.material = material

    # Polimorfismo
    def evaluar_alerta(self):
        return self.cantidad < 3

    def obtener_detalles(self):
        return f"[ACCESORIO] {super().obtener_detalles()} | Material: {self.material}"


class GestorInventario:
    """Clase que gestiona la relación entre múltiples productos y transacciones (Relación de Asociación)."""
    def __init__(self):
        self.productos = []

    def agregar_producto(self, producto: Producto):
        if not isinstance(producto, Producto):
            raise ErrorDatoInvalido("El objeto debe ser una instancia de la clase Producto.")
        self.productos.append(producto)

    def obtener_total_inventario(self):
        return sum(p.precio * p.cantidad for p in self.productos)


# 3. FUNCIONES DE APOYO PARA STREAMLIT

def load_data(url):
    """
    Carga datos desde un CSV (o Google Sheets) y prepara las fechas.
    Manejo de excepciones integrado.
    """
    try:
        df = pd.read_csv(url)
        
        if 'Nombre' in df.columns:
            df['Nombre'] = df['Nombre'].str.lower().str.strip()
        
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Fecha'])
        
        df['Mes_Año'] = df['Fecha'].dt.to_period('M').astype(str)
        df['Semana'] = df['Fecha'].dt.isocalendar().week
        df['Mes_Num'] = df['Fecha'].dt.month
        df['Año'] = df['Fecha'].dt.year
        
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

def get_ventas_analisis(df):
    """
    Filtra las transacciones que son ventas. 
    Detecta por signo negativo y por etiqueta 'SALIDA'.
    """
    if df.empty: return df

    condicion_venta = (df['Cantidad'] < 0)
    if 'Tipo' in df.columns:
        condicion_venta = condicion_venta | (df['Tipo'].str.upper() == 'SALIDA')
    
    ventas = df[condicion_venta].copy()
    ventas['Monto'] = np.abs(ventas['Cantidad']) * ventas['Precio']
    
    return ventas

def get_ventas_temporales(ventas_df, periodo='mes'):
    if ventas_df.empty: return ventas_df
    hoy = datetime.datetime.now()
    
    if periodo == 'mes':
        return ventas_df[(ventas_df['Mes_Num'] == hoy.month) & (ventas_df['Año'] == hoy.year)]
    elif periodo == 'semana':
        return ventas_df[ventas_df['Semana'] == hoy.isocalendar().week]
    
    return ventas_df

def get_pivot_estacionalidad(ventas_df):
    if ventas_df.empty:
        return pd.DataFrame()
        
    pivot = ventas_df.pivot_table(
        index='Nombre', 
        columns='Mes_Año', 
        values='Monto', 
        aggfunc='sum'
    ).fillna(0)
    
    return np.abs(pivot)