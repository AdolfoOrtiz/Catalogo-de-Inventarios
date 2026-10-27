from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Categoria(models.Model):
    """
    Categoría para clasificación de productos en el catálogo de inventario.
    """
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Proveedor(models.Model):
    """
    Proveedor de insumos/productos para el control de inventario.
    """
    nombre_empresa = models.CharField(max_length=150, unique=True, verbose_name="Nombre de Empresa")
    rfc_o_identificacion = models.CharField(max_length=20, unique=True, verbose_name="RFC / Identificación")
    contacto_nombre = models.CharField(max_length=100, verbose_name="Nombre de Contacto")
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=25, verbose_name="Teléfono")
    direccion = models.TextField(blank=True, verbose_name="Dirección")
    sitio_web = models.URLField(blank=True, null=True, verbose_name="Sitio Web")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ["nombre_empresa"]

    def __str__(self):
        return f"{self.nombre_empresa} ({self.contacto_nombre})"


class Producto(models.Model):
    """
    Producto dentro del catálogo de inventario.
    Relacionado con Categoria y Proveedor.
    """
    sku = models.CharField(max_length=30, unique=True, verbose_name="SKU / Código Único")
    nombre = models.CharField(max_length=150, verbose_name="Nombre del Producto")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Precio de Venta"
    )
    costo = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Costo Unitario"
    )
    stock_actual = models.PositiveIntegerField(default=0, verbose_name="Stock Actual")
    stock_minimo = models.PositiveIntegerField(default=5, verbose_name="Stock Mínimo de Alerta")
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="productos",
        verbose_name="Categoría"
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos",
        verbose_name="Proveedor Principal"
    )
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True, verbose_name="Imagen del Producto")
    activo = models.BooleanField(default=True, verbose_name="Activo en Catálogo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-fecha_creacion"]

    @property
    def tiene_stock_bajo(self):
        """Devuelve True si el stock actual es menor o igual al stock mínimo configurado."""
        return self.stock_actual <= self.stock_minimo

    @property
    def estado_stock(self):
        """Etiqueta visual del estado del inventario."""
        if self.stock_actual == 0:
            return "AGOTADO"
        elif self.stock_actual <= self.stock_minimo:
            return "BAJO"
        return "NORMAL"

    def __str__(self):
        return f"[{self.sku}] {self.nombre} (Stock: {self.stock_actual})"


class MovimientoInventario(models.Model):
    """
    Registro histórico de entradas, salidas y ajustes de existencias.
    """
    TIPO_CHOICES = (
        ('ENTRADA', 'Entrada de Stock'),
        ('SALIDA', 'Salida de Stock'),
        ('AJUSTE', 'Ajuste Manual'),
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="movimientos",
        verbose_name="Producto"
    )
    tipo_movimiento = models.CharField(
        max_length=10, 
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Movimiento"
    )
    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Cantidad"
    )
    stock_previo = models.IntegerField(verbose_name="Stock Previo")
    stock_resultante = models.IntegerField(verbose_name="Stock Resultante")
    motivo = models.CharField(max_length=255, verbose_name="Motivo / Referencia")
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimientos_inventario",
        verbose_name="Usuario Responsable"
    )
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del Movimiento")

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.tipo_movimiento} de {self.cantidad} uds - {self.producto.sku} ({self.fecha.strftime('%d/%m/%Y %H:%M')})"
