from django.contrib.auth.models import Group, User
from django.contrib.auth import logout as django_logout
from django.db.models import F
from rest_framework import permissions, viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from catalogo.authentication import BearerTokenAuthentication
from catalogo.models import Categoria, Proveedor, Producto, MovimientoInventario
from catalogo.serializers import (
    UserSerializer, GroupSerializer,
    RegisterSerializer, MeUserSerializer, MeUserUpdateSerializer,
    CategoriaSerializer, ProveedorSerializer,
    ProductoSerializer, MovimientoInventarioSerializer
)


# ==========================================
# VISTAS DE USUARIOS Y ROLES (ADMIN / DRF)
# ==========================================

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar usuarios del sistema.
    """
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar grupos y roles del sistema.
    """
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


# ==========================================
# ENDPOINTS DE AUTENTICACIÓN
# ==========================================

class CustomAuthToken(ObtainAuthToken):
    """
    POST: Obtiene el token de autenticación enviando 'username' y 'password'.
    Retorna: token, user_id, username, email.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email
        }, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):
    """
    POST: Registra un nuevo usuario en la plataforma y retorna su token de acceso.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Usuario registrado exitosamente.",
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeAPIView(APIView):
    """
    GET, PATCH, PUT, POST: Obtener o actualizar el perfil del usuario autenticado.
    Soporta autenticación con 'Bearer <token>' o 'Token <token>'.
    """
    authentication_classes = [TokenAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MeUserSerializer(request.user)
        data = serializer.data
        if request.auth:
            data["auth_token"] = str(request.auth)
        return Response(data)

    def patch(self, request):
        serializer = MeUserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = MeUserSerializer(request.user).data
            if request.auth:
                data["auth_token"] = str(request.auth)
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return self.patch(request)

    def post(self, request):
        return self.patch(request)


class ResetTokenAPIView(APIView):
    """
    POST: Invalida el token actual y genera uno nuevo para el usuario autenticado.
    """
    authentication_classes = [TokenAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        Token.objects.filter(user=user).delete()
        new_token = Token.objects.create(user=user)
        return Response({
            "detail": "Token renovado exitosamente.",
            "token": new_token.key,
            "user_id": user.pk,
            "username": user.username
        }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    """
    POST, GET: Cierra la sesión y destruye el token activo.
    """
    authentication_classes = [TokenAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        Token.objects.filter(user=request.user).delete()
        django_logout(request)
        return Response({
            "detail": "Sesión cerrada exitosamente. Token eliminado."
        }, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


# ==========================================
# VIEWSETS DEL CATÁLOGO DE INVENTARIO
# ==========================================

class CategoriaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para administración de Categorías.
    Soporta filtros, búsquedas y ordenamiento.
    """
    queryset = Categoria.objects.all().order_by('nombre')
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre', 'codigo', 'descripcion']
    ordering_fields = ['nombre', 'codigo', 'fecha_creacion']


class ProveedorViewSet(viewsets.ModelViewSet):
    """
    API endpoint para administración y relaciones con Proveedores.
    Soporta filtros, búsquedas y ordenamiento.
    """
    queryset = Proveedor.objects.all().order_by('nombre_empresa')
    serializer_class = ProveedorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre_empresa', 'rfc_o_identificacion', 'contacto_nombre', 'email', 'telefono']
    ordering_fields = ['nombre_empresa', 'fecha_registro']


class ProductoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para el Catálogo de Productos.
    - Filtro por categoría y proveedor: ?categoria=1&proveedor=2
    - Búsqueda textual: ?search=taladro
    - Filtro por precio: ?min_precio=100&max_precio=500
    - Filtro de existencias bajas: ?bajo_stock=true
    - Ordenamiento: ?ordering=-precio o ?ordering=stock_actual
    """
    queryset = Producto.objects.select_related('categoria', 'proveedor').all().order_by('-fecha_creacion')
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'proveedor', 'activo']
    search_fields = ['sku', 'nombre', 'descripcion', 'categoria__nombre', 'proveedor__nombre_empresa']
    ordering_fields = ['precio', 'stock_actual', 'nombre', 'sku', 'fecha_creacion']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro de productos con stock bajo o agotado
        bajo_stock = self.request.query_params.get('bajo_stock')
        if bajo_stock and bajo_stock.lower() in ['true', '1']:
            queryset = queryset.filter(stock_actual__lte=F('stock_minimo'))

        # Filtro por rango de precio
        min_precio = self.request.query_params.get('min_precio')
        max_precio = self.request.query_params.get('max_precio')
        if min_precio is not None and min_precio != '':
            queryset = queryset.filter(precio__gte=min_precio)
        if max_precio is not None and max_precio != '':
            queryset = queryset.filter(precio__lte=max_precio)

        return queryset

    @action(detail=False, methods=['get'])
    def bajo_stock(self, request):
        """
        Endpoint rápido para listar productos que requieren reabastecimiento (stock_actual <= stock_minimo).
        GET /api/productos/bajo_stock/
        """
        productos_alerta = self.get_queryset().filter(stock_actual__lte=F('stock_minimo'))
        page = self.paginate_queryset(productos_alerta)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(productos_alerta, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def ajustar_stock(self, request, pk=None):
        """
        Endpoint directo para registrar una entrada, salida o ajuste sobre este producto específico.
        POST /api/productos/{id}/ajustar_stock/
        Body:
        {
            "tipo_movimiento": "ENTRADA", // "ENTRADA", "SALIDA", "AJUSTE"
            "cantidad": 10,
            "motivo": "Recepción de mercancía por pedido #458"
        }
        """
        producto = self.get_object()
        data = request.data.copy()
        data['producto'] = producto.id

        serializer = MovimientoInventarioSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            movimiento = serializer.save()
            producto.refresh_from_db()
            return Response({
                "detail": f"Stock actualizado exitosamente. Nuevo stock actual: {producto.stock_actual}.",
                "producto": ProductoSerializer(producto, context={'request': request}).data,
                "movimiento": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    """
    API endpoint para consultar y registrar movimientos históricos de existencias.
    """
    queryset = MovimientoInventario.objects.select_related('producto', 'usuario').all().order_by('-fecha')
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['producto', 'tipo_movimiento']
    search_fields = ['motivo', 'producto__sku', 'producto__nombre', 'usuario__username']
    ordering_fields = ['fecha', 'cantidad']

    def perform_create(self, serializer):
        serializer.save()
