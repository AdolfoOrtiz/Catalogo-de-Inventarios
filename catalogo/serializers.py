from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.db import transaction

from .models import Categoria, Proveedor, Producto, MovimientoInventario


# ==========================================
# SERIALIZERS DE USUARIOS Y AUTENTICACIÓN
# ==========================================

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "id", "username", "email", "groups"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "id", "name"]


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="Este correo electrónico ya está registrado."
        )]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "password", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", "")
        )
        return user


class MeUserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "groups",
            "date_joined",
        ]
        read_only_fields = fields


class MeUserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=False,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="Este correo electrónico ya está registrado por otro usuario."
        )]
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        ]
        extra_kwargs = {
            "username": {"required": False},
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# ==========================================
# SERIALIZERS AUXILIARES (ANIDADOS)
# ==========================================

class CategoriaNestedSerializer(serializers.ModelSerializer):
    """Serializer anidado para mostrar datos resumidos de la categoría."""
    class Meta:
        model = Categoria
        fields = ['id', 'codigo', 'nombre']


class ProveedorNestedSerializer(serializers.ModelSerializer):
    """Serializer anidado para mostrar datos resumidos del proveedor."""
    class Meta:
        model = Proveedor
        fields = ['id', 'nombre_empresa', 'contacto_nombre', 'email', 'telefono']


class ProductoNestedSerializer(serializers.ModelSerializer):
    """Serializer anidado de producto para listar en categorías o movimientos."""
    class Meta:
        model = Producto
        fields = ['id', 'sku', 'nombre', 'precio', 'stock_actual', 'activo']


# ==========================================
# SERIALIZERS PRINCIPALES DEL CATÁLOGO
# ==========================================

class CategoriaSerializer(serializers.ModelSerializer):
    total_productos = serializers.IntegerField(source='productos.count', read_only=True)
    productos = ProductoNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Categoria
        fields = [
            'id', 
            'nombre', 
            'codigo', 
            'descripcion', 
            'activo', 
            'fecha_creacion', 
            'total_productos',
            'productos'
        ]

    def validate_codigo(self, value):
        return value.strip().upper()


class ProveedorSerializer(serializers.ModelSerializer):
    total_productos = serializers.IntegerField(source='productos.count', read_only=True)
    productos = ProductoNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Proveedor
        fields = [
            'id',
            'nombre_empresa',
            'rfc_o_identificacion',
            'contacto_nombre',
            'email',
            'telefono',
            'direccion',
            'sitio_web',
            'activo',
            'fecha_registro',
            'total_productos',
            'productos'
        ]

    def validate_rfc_o_identificacion(self, value):
        return value.strip().upper()


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializer para Producto.
    Acepta IDs de 'categoria' y 'proveedor' para creación y actualización (escritura).
    Expone objetos anidados 'categoria_detalle' y 'proveedor_detalle' para consulta (lectura).
    """
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        required=True
    )
    proveedor = serializers.PrimaryKeyRelatedField(
        queryset=Proveedor.objects.all(),
        required=False,
        allow_null=True
    )
    # Serializers anidados de lectura
    categoria_detalle = CategoriaNestedSerializer(source='categoria', read_only=True)
    proveedor_detalle = ProveedorNestedSerializer(source='proveedor', read_only=True)
    
    # Propiedades calculadas
    tiene_stock_bajo = serializers.BooleanField(read_only=True)
    estado_stock = serializers.CharField(read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id',
            'sku',
            'nombre',
            'descripcion',
            'precio',
            'costo',
            'stock_actual',
            'stock_minimo',
            'categoria',
            'categoria_detalle',
            'proveedor',
            'proveedor_detalle',
            'imagen',
            'activo',
            'tiene_stock_bajo',
            'estado_stock',
            'fecha_creacion',
            'fecha_actualizacion',
        ]

    def validate_sku(self, value):
        sku_clean = value.strip().upper()
        if len(sku_clean) < 3:
            raise serializers.ValidationError("El SKU debe tener al menos 3 caracteres.")
        return sku_clean

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio de venta debe ser mayor a 0.")
        return value

    def validate(self, attrs):
        costo = attrs.get('costo')
        precio = attrs.get('precio')
        if costo is not None and precio is not None and costo > precio:
            # Advertencia lógica: aunque en algunos negocios ocurre, se suele validar o registrar
            pass
        return attrs


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    """
    Serializer para registrar movimientos de existencias.
    Controla atómicamente el stock del producto asegurando consistencia.
    """
    producto = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(),
        required=True
    )
    producto_detalle = ProductoNestedSerializer(source='producto', read_only=True)
    usuario_nombre = serializers.ReadOnlyField(source='usuario.username')
    stock_previo = serializers.IntegerField(read_only=True)
    stock_resultante = serializers.IntegerField(read_only=True)

    class Meta:
        model = MovimientoInventario
        fields = [
            'id',
            'producto',
            'producto_detalle',
            'tipo_movimiento',
            'cantidad',
            'stock_previo',
            'stock_resultante',
            'motivo',
            'usuario',
            'usuario_nombre',
            'fecha',
        ]
        read_only_fields = ['stock_previo', 'stock_resultante', 'usuario', 'fecha']

    def validate(self, attrs):
        producto = attrs.get('producto')
        tipo = attrs.get('tipo_movimiento')
        cantidad = attrs.get('cantidad')

        if tipo == 'SALIDA':
            if cantidad > producto.stock_actual:
                raise serializers.ValidationError({
                    'cantidad': f'No hay suficiente stock para la salida. Stock actual: {producto.stock_actual}, solicitado: {cantidad}.'
                })
        return attrs

    def create(self, validated_data):
        producto = validated_data['producto']
        tipo = validated_data['tipo_movimiento']
        cantidad = validated_data['cantidad']
        request = self.context.get('request')
        usuario = request.user if request and request.user.is_authenticated else None

        with transaction.atomic():
            # Bloqueamos el producto para actualización segura
            prod = Producto.objects.select_for_update().get(pk=producto.pk)
            stock_previo = prod.stock_actual

            if tipo == 'ENTRADA':
                stock_resultante = stock_previo + cantidad
            elif tipo == 'SALIDA':
                stock_resultante = stock_previo - cantidad
            elif tipo == 'AJUSTE':
                stock_resultante = cantidad
            else:
                stock_resultante = stock_previo

            prod.stock_actual = stock_resultante
            prod.save()

            movimiento = MovimientoInventario.objects.create(
                producto=prod,
                tipo_movimiento=tipo,
                cantidad=cantidad,
                stock_previo=stock_previo,
                stock_resultante=stock_resultante,
                motivo=validated_data['motivo'],
                usuario=usuario
            )

        return movimiento
