from django.contrib import admin
from django.utils.html import format_html
from catalogo.models import Categoria, Proveedor, Producto, MovimientoInventario

admin.site.site_header = "Administración - Catálogo de Inventario"
admin.site.site_title = "Panel Catálogo e Inventario"
admin.site.index_title = "Gestión de Productos, Proveedores y Existencias"


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nombre', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre', 'codigo', 'descripcion')
    ordering = ('nombre',)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_empresa', 'rfc_o_identificacion', 'contacto_nombre', 'email', 'telefono', 'activo')
    list_filter = ('activo', 'fecha_registro')
    search_fields = ('nombre_empresa', 'rfc_o_identificacion', 'contacto_nombre', 'email')
    ordering = ('nombre_empresa',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'sku', 
        'nombre', 
        'categoria', 
        'proveedor', 
        'precio', 
        'costo', 
        'stock_actual', 
        'stock_minimo', 
        'alerta_stock', 
        'activo'
    )
    list_filter = ('categoria', 'proveedor', 'activo', 'fecha_creacion')
    search_fields = ('sku', 'nombre', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    ordering = ('-fecha_creacion',)

    @admin.display(description="Estado de Stock")
    def alerta_stock(self, obj):
        if obj.stock_actual == 0:
            return format_html('<span style="color: red; font-weight: bold;">AGOTADO (0)</span>')
        elif obj.stock_actual <= obj.stock_minimo:
            return format_html('<span style="color: orange; font-weight: bold;">STOCK BAJO ({})</span>', obj.stock_actual)
        return format_html('<span style="color: green; font-weight: bold;">NORMAL ({})</span>', obj.stock_actual)


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'fecha', 
        'tipo_movimiento', 
        'producto', 
        'cantidad', 
        'stock_previo', 
        'stock_resultante', 
        'usuario', 
        'motivo'
    )
    list_filter = ('tipo_movimiento', 'fecha')
    search_fields = ('producto__sku', 'producto__nombre', 'motivo', 'usuario__username')
    readonly_fields = ('fecha', 'stock_previo', 'stock_resultante')
    ordering = ('-fecha',)
