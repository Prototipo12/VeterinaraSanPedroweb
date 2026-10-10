import unittest
from logic import Producto, ProductoFarmaceutico, ProductoAccesorio, GestorInventario, ErrorDatoInvalido

class TestVeterinariaPOO(unittest.TestCase):

    def test_creacion_producto_valido(self):
        prod = Producto("Antipulgas", "Farmacia", 45.50, 10)
        self.assertEqual(prod.nombre, "antipulgas")
        self.assertEqual(prod.precio, 45.50)
        self.assertEqual(prod.cantidad, 10)

    def test_excepcion_datos_negativos(self):
        with self.assertRaises(ErrorDatoInvalido):
            Producto("Vacuna", "Farmacia", -10.0, 5)

    def test_herencia_y_polimorfismo(self):
        # Producto farmacéutico tiene umbral de alerta estricto (< 10)
        farma = ProductoFarmaceutico("Amoxicilina", "Farmacia", 20.0, 8, requiere_receta=True)
        self.assertTrue(farma.evaluar_alerta())
        self.assertIn("[FARMACIA]", farma.obtener_detalles())

        # Producto accesorio tiene umbral de alerta menor (< 3)
        acc = ProductoAccesorio("Correa", "Accesorios", 15.0, 5, material="Nylon")
        self.assertFalse(acc.evaluar_alerta())
        self.assertIn("[ACCESORIO]", acc.obtener_detalles())

    def test_gestor_inventario(self):
        gestor = GestorInventario()
        p1 = Producto("Shampoo", "Aseo", 30.0, 2)
        p2 = Producto("Juguete", "Accesorios", 10.0, 4)
        
        gestor.agregar_producto(p1)
        gestor.agregar_producto(p2)
        
        # (30 * 2) + (10 * 4) = 60 + 40 = 100
        self.assertEqual(gestor.obtener_total_inventario(), 100.0)

if __name__ == '__main__':
    unittest.main()