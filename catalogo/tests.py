from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from decimal import Decimal
from catalogo.models import Categoria, Proveedor, Producto, MovimientoInventario


class CatalogoAPITests(APITestCase):
    def setUp(self):
        # Usuario de pruebas
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)

        # Datos de prueba
        self.categoria = Categoria.objects.create(
            codigo="CAT-TEST",
            nombre="Electrónica de Prueba",
            descripcion="Categoría para testing"
        )
        self.proveedor = Proveedor.objects.create(
            nombre_empresa="Proveedor Test S.A.",
            rfc_o_identificacion="TES123456ABC",
            contacto_nombre="Juan Pérez",
            email="juan@provtest.com",
            telefono="5551234567"
        )
        self.producto = Producto.objects.create(
            sku="SKU-TEST-001",
            nombre="Teclado Mecánico RGB",
            descripcion="Teclado switches azules",
            precio=Decimal("1200.00"),
            costo=Decimal("800.00"),
            stock_actual=10,
            stock_minimo=3,
            categoria=self.categoria,
            proveedor=self.proveedor
        )

    # ==========================
    # TESTS DE AUTENTICACIÓN
    # ==========================
    def test_register_user(self):
        self.client.credentials()  # Desautenticar
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!",
            "first_name": "Nuevo",
            "last_name": "Usuario"
        }
        response = self.client.post("/api/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("user_id", response.data)

    def test_custom_token_login(self):
        self.client.credentials()
        data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        response = self.client.post("/api/custom-token/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["token"], self.token.key)

    def test_me_endpoint(self):
        response = self.client.get("/api/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["auth_token"], self.token.key)

    def test_logout(self):
        response = self.client.post("/api/logout/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # El token debe haber sido eliminado
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())

    # ==========================
    # TESTS DE CATEGORÍAS
    # ==========================
    def test_list_categorias(self):
        response = self.client.get("/api/categorias/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_categoria(self):
        data = {
            "codigo": "CAT-NEW",
            "nombre": "Nueva Categoria",
            "descripcion": "Descripción de prueba"
        }
        response = self.client.post("/api/categorias/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["codigo"], "CAT-NEW")

    # ==========================
    # TESTS DE PROVEEDORES
    # ==========================
    def test_create_proveedor(self):
        data = {
            "nombre_empresa": "Distribuidor Alfa S.A.",
            "rfc_o_identificacion": "ALF990101XYZ",
            "contacto_nombre": "Carlos Méndez",
            "email": "contacto@alfa.com",
            "telefono": "4491122334"
        }
        response = self.client.post("/api/proveedores/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["rfc_o_identificacion"], "ALF990101XYZ")

    # ==========================
    # TESTS DE PRODUCTOS (NESTED & FILTERS)
    # ==========================
    def test_create_producto_with_nested_response(self):
        data = {
            "sku": "SKU-TEST-002",
            "nombre": "Mouse Inalámbrico",
            "descripcion": "Mouse ergonómico 2.4GHz",
            "precio": "450.00",
            "costo": "250.00",
            "stock_actual": 20,
            "stock_minimo": 5,
            "categoria": self.categoria.id,
            "proveedor": self.proveedor.id
        }
        response = self.client.post("/api/productos/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["sku"], "SKU-TEST-002")
        # Verificar serialización anidada
        self.assertIn("categoria_detalle", response.data)
        self.assertEqual(response.data["categoria_detalle"]["nombre"], self.categoria.nombre)
        self.assertIn("proveedor_detalle", response.data)
        self.assertEqual(response.data["proveedor_detalle"]["nombre_empresa"], self.proveedor.nombre_empresa)

    def test_filter_and_search_productos(self):
        # Crear un producto de baja existencia
        Producto.objects.create(
            sku="SKU-BAJO-01",
            nombre="Monitor Usado",
            descripcion="Monitor de exhibición",
            precio=Decimal("2500.00"),
            costo=Decimal("1500.00"),
            stock_actual=1,
            stock_minimo=3,
            categoria=self.categoria,
            proveedor=self.proveedor
        )

        # Búsqueda por texto
        response = self.client.get("/api/productos/?search=Monitor")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        # Filtro por bajo_stock
        response_bajo = self.client.get("/api/productos/?bajo_stock=true")
        self.assertEqual(response_bajo.status_code, status.HTTP_200_OK)
        self.assertEqual(response_bajo.data["count"], 1)
        self.assertEqual(response_bajo.data["results"][0]["sku"], "SKU-BAJO-01")

        # Endpoint custom action /bajo_stock/
        response_action = self.client.get("/api/productos/bajo_stock/")
        self.assertEqual(response_action.status_code, status.HTTP_200_OK)
        self.assertEqual(response_action.data["count"], 1)

    # ==========================
    # TESTS DE MOVIMIENTOS Y EXISTENCIAS
    # ==========================
    def test_movimiento_entrada(self):
        data = {
            "producto": self.producto.id,
            "tipo_movimiento": "ENTRADA",
            "cantidad": 5,
            "motivo": "Compra de reabastecimiento"
        }
        response = self.client.post("/api/movimientos/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, 15)  # 10 + 5
        self.assertEqual(response.data["stock_previo"], 10)
        self.assertEqual(response.data["stock_resultante"], 15)

    def test_movimiento_salida(self):
        data = {
            "producto": self.producto.id,
            "tipo_movimiento": "SALIDA",
            "cantidad": 4,
            "motivo": "Venta en mostrador #1024"
        }
        response = self.client.post("/api/movimientos/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, 6)  # 10 - 4

    def test_movimiento_salida_insuficiente_falla(self):
        # Intentar sacar 20 unidades cuando solo hay 10
        data = {
            "producto": self.producto.id,
            "tipo_movimiento": "SALIDA",
            "cantidad": 20,
            "motivo": "Pedido cancelable"
        }
        response = self.client.post("/api/movimientos/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cantidad", response.data)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, 10)  # No cambia

    def test_ajustar_stock_action(self):
        url = f"/api/productos/{self.producto.id}/ajustar_stock/"
        data = {
            "tipo_movimiento": "ENTRADA",
            "cantidad": 7,
            "motivo": "Ajuste directo de prueba"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, 17)
