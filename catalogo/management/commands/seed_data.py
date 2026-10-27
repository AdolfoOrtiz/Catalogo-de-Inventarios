from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from decimal import Decimal
from catalogo.models import Categoria, Proveedor, Producto, MovimientoInventario


class Command(BaseCommand):
    help = "Puebla la base de datos con usuarios, categorías, proveedores y productos iniciales."

    def handle(self, *args, **options):
        self.stdout.write("Creando usuarios iniciales...")
        # Superusuario
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@inventario.com",
                "first_name": "Administrador",
                "last_name": "Principal",
                "is_staff": True,
                "is_superuser": True
            }
        )
        if created:
            admin_user.set_password("admin12345")
            admin_user.save()
        admin_token, _ = Token.objects.get_or_create(user=admin_user)

        # Usuario estándar
        user1, created = User.objects.get_or_create(
            username="vendedor1",
            defaults={
                "email": "vendedor1@inventario.com",
                "first_name": "Carlos",
                "last_name": "López"
            }
        )
        if created:
            user1.set_password("vendedor12345")
            user1.save()
        user1_token, _ = Token.objects.get_or_create(user=user1)

        self.stdout.write(f"  - Admin: admin / admin12345 (Token: {admin_token.key})")
        self.stdout.write(f"  - Vendedor: vendedor1 / vendedor12345 (Token: {user1_token.key})")

        self.stdout.write("Creando categorías...")
        cat_tec, _ = Categoria.objects.get_or_create(
            codigo="CAT-TEC",
            defaults={
                "nombre": "Tecnología y Computación",
                "descripcion": "Laptops, periféricos, monitores y componentes de hardware."
            }
        )
        cat_ofi, _ = Categoria.objects.get_or_create(
            codigo="CAT-OFI",
            defaults={
                "nombre": "Mobiliario y Oficina",
                "descripcion": "Sillas ergonómicas, escritorios y accesorios de oficina."
            }
        )
        cat_her, _ = Categoria.objects.get_or_create(
            codigo="CAT-HER",
            defaults={
                "nombre": "Herramientas y Mantenimiento",
                "descripcion": "Herramientas eléctricas y manuales para talleres."
            }
        )
        cat_red, _ = Categoria.objects.get_or_create(
            codigo="CAT-RED",
            defaults={
                "nombre": "Redes y Telecomunicaciones",
                "descripcion": "Routers, switches, cableado estructurado y racks."
            }
        )

        self.stdout.write("Creando proveedores...")
        prov_dell, _ = Proveedor.objects.get_or_create(
            rfc_o_identificacion="DEL890123MX1",
            defaults={
                "nombre_empresa": "Dell Technologies México",
                "contacto_nombre": "Mariana Gómez",
                "email": "ventas@dell-dist.com.mx",
                "telefono": "+52 55 5000 1100",
                "direccion": "Av. Paseo de la Reforma 250, CDMX",
                "sitio_web": "https://www.dell.com/mx"
            }
        )
        prov_cisco, _ = Proveedor.objects.get_or_create(
            rfc_o_identificacion="CIS920415US9",
            defaults={
                "nombre_empresa": "Cisco Systems Distribución",
                "contacto_nombre": "Roberto Morales",
                "email": "soporte@cisco-dist.com",
                "telefono": "+52 81 8300 4500",
                "direccion": "San Pedro Garza García, Nuevo León",
                "sitio_web": "https://www.cisco.com"
            }
        )
        prov_ofi, _ = Proveedor.objects.get_or_create(
            rfc_o_identificacion="OFI781109KL2",
            defaults={
                "nombre_empresa": "Equipos de Oficina San Marcos",
                "contacto_nombre": "Ana Sofía Vega",
                "email": "contacto@sanmarcosoficina.com",
                "telefono": "+52 449 912 3456",
                "direccion": "Av. López Mateos 104, Aguascalientes",
                "sitio_web": "https://www.sanmarcosoficina.com"
            }
        )
        prov_mak, _ = Proveedor.objects.get_or_create(
            rfc_o_identificacion="MAK840502TR8",
            defaults={
                "nombre_empresa": "Makita Herramientas Industriales",
                "contacto_nombre": "Eduardo Ramos",
                "email": "atencion@makita-dist.com",
                "telefono": "+52 33 3612 9000",
                "direccion": "Guadalajara, Jalisco",
                "sitio_web": "https://www.makita.com.mx"
            }
        )

        self.stdout.write("Creando productos con diferentes niveles de stock...")
        productos_data = [
            {
                "sku": "LAP-DELL-XPS15",
                "nombre": "Laptop Dell XPS 15 Intel i7 32GB RAM",
                "descripcion": "Laptop de alto rendimiento para desarrolladores y diseñadores gráficos.",
                "precio": Decimal("34999.00"),
                "costo": Decimal("28500.00"),
                "stock_actual": 8,
                "stock_minimo": 3,
                "categoria": cat_tec,
                "proveedor": prov_dell,
            },
            {
                "sku": "MON-DELL-4K27",
                "nombre": "Monitor Dell UltraSharp 27 pulgadas 4K",
                "descripcion": "Monitor IPS 4K UHD con puerto USB-C y 99% sRGB.",
                "precio": Decimal("11499.00"),
                "costo": Decimal("8900.00"),
                "stock_actual": 2,  # ⚠️ Stock bajo (menor a minimo 4)
                "stock_minimo": 4,
                "categoria": cat_tec,
                "proveedor": prov_dell,
            },
            {
                "sku": "SWT-CIS-24P",
                "nombre": "Switch Cisco Catalyst 24 Puertos Gigabit PoE+",
                "descripcion": "Switch gestionable capa 2/3 ideal para infraestructura de oficinas medianas.",
                "precio": Decimal("18750.00"),
                "costo": Decimal("14200.00"),
                "stock_actual": 5,
                "stock_minimo": 2,
                "categoria": cat_red,
                "proveedor": prov_cisco,
            },
            {
                "sku": "ROU-CIS-ISR",
                "nombre": "Router Cisco Gigabit Ethernet con VPN y Firewall",
                "descripcion": "Enrutador de alta seguridad con soporte VPN IPSec y filtrado avanzado.",
                "precio": Decimal("14200.00"),
                "costo": Decimal("10800.00"),
                "stock_actual": 1,  # ⚠️ Stock bajo (menor a minimo 3)
                "stock_minimo": 3,
                "categoria": cat_red,
                "proveedor": prov_cisco,
            },
            {
                "sku": "SIL-ERG-PRO",
                "nombre": "Silla Ergonómica de Malla Ejecutiva con Soporte Lumbar",
                "descripcion": "Silla ajustable en altura, brazos 3D y cabecera abatible con certificación ANSI/BIFMA.",
                "precio": Decimal("4890.00"),
                "costo": Decimal("3100.00"),
                "stock_actual": 15,
                "stock_minimo": 5,
                "categoria": cat_ofi,
                "proveedor": prov_ofi,
            },
            {
                "sku": "ESC-AJU-ELE",
                "nombre": "Escritorio Elevable Eléctrico Standing Desk 140x70",
                "descripcion": "Escritorio motorizado con 4 memorias de altura y soporte hasta 80kg.",
                "precio": Decimal("7999.00"),
                "costo": Decimal("5400.00"),
                "stock_actual": 0,  # ⚠️ AGOTADO
                "stock_minimo": 2,
                "categoria": cat_ofi,
                "proveedor": prov_ofi,
            },
            {
                "sku": "TAL-MAK-18V",
                "nombre": "Rotomartillo Inalámbrico Makita 18V Brushless",
                "descripcion": "Taladro atornillador percutor de 1/2 pulgada con 2 baterías de 5Ah y estuche.",
                "precio": Decimal("5650.00"),
                "costo": Decimal("4200.00"),
                "stock_actual": 12,
                "stock_minimo": 4,
                "categoria": cat_her,
                "proveedor": prov_mak,
            },
            {
                "sku": "ESM-MAK-412",
                "nombre": "Esmeriladora Angular Makita 4-1/2 Pulgadas 840W",
                "descripcion": "Esmeriladora compacta con mango ergonómico y guarda de seguridad.",
                "precio": Decimal("1890.00"),
                "costo": Decimal("1350.00"),
                "stock_actual": 3,  # ⚠️ Stock bajo (minimo 5)
                "stock_minimo": 5,
                "categoria": cat_her,
                "proveedor": prov_mak,
            },
        ]

        for p_data in productos_data:
            sku = p_data.pop("sku")
            prod, _ = Producto.objects.get_or_create(sku=sku, defaults=p_data)

        self.stdout.write("Registrando movimientos iniciales de existencias...")
        # Movimiento de entrada
        prod_lap = Producto.objects.get(sku="LAP-DELL-XPS15")
        MovimientoInventario.objects.get_or_create(
            producto=prod_lap,
            motivo="Inventario inicial por factura F-2026-001",
            defaults={
                "tipo_movimiento": "ENTRADA",
                "cantidad": 8,
                "stock_previo": 0,
                "stock_resultante": 8,
                "usuario": admin_user
            }
        )

        self.stdout.write(self.style.SUCCESS("¡Base de datos poblada exitosamente!"))
