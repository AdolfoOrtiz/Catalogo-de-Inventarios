from django.urls import path, include
from rest_framework import routers
from catalogo.views import (
    UserViewSet, GroupViewSet,
    CategoriaViewSet, ProveedorViewSet,
    ProductoViewSet, MovimientoInventarioViewSet
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'proveedores', ProveedorViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'movimientos', MovimientoInventarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
