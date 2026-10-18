import argparse
import csv
import json
import os
from datetime import datetime
import zipfile

# Configuración de archivos
ARCHIVO_CLIENTES = 'clientes.csv'
ARCHIVO_PRODUCTOS = 'productos.csv' 
ARCHIVO_PEDIDOS = 'pedidos.json'

# Cabeceras CSV()
CABECERA_CLIENTES = ['id_cliente', 'nombre', 'email', 'telefono', 'direccion', 'localidad', 'provincia', 'codigo_postal']
CABECERA_PRODUCTOS = ['id_producto', 'nombre', 'categoria', 'precio', 'stock']

def verificar_archivos():
    if not os.path.exists(ARCHIVO_CLIENTES):
        with open(ARCHIVO_CLIENTES, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(CABECERA_CLIENTES)

    if not os.path.exists(ARCHIVO_PRODUCTOS):
        with open(ARCHIVO_PRODUCTOS, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(CABECERA_PRODUCTOS)

    if not os.path.exists(ARCHIVO_PEDIDOS):
        with open(ARCHIVO_PEDIDOS, 'w', encoding='utf-8') as f:
            json.dump([], f)

def mostrar_error(operacion, mensaje):
    print(f"## ERROR: {operacion}")
    print(f"\"{mensaje}\"")

def mostrar_exito(operacion):
    print(f"***{operacion} realizada***")

def leer_clientes():
    clientes = []
    with open(ARCHIVO_CLIENTES, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            clientes.append(row)
    return clientes

def escribir_clientes(clientes):
    with open(ARCHIVO_CLIENTES, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CABECERA_CLIENTES, delimiter=';') 
        writer.writeheader()
        writer.writerows(clientes)

def validar_cliente(args):
    if not args.id_cliente or not args.name or not args.email or not args.phone or \
       not args.address or not args.city or not args.province or not args.postal_code:
        print("Faltan datos obligatorios del cliente")
        return False
    
    if '@' not in args.email:
        print("Email inválido")
        return False
    
    if not (9 <= len(args.phone) <= 15):
        print("Teléfono inválido")
        return False
    
    if not (len(args.postal_code) == 5 and args.postal_code.isdigit()):
        print("Código postal inválido")
        return False
    
    return True

def agregar_cliente(args):
    if not validar_cliente(args):
        return
        
    clientes = leer_clientes()
    
    # Verificar si existe el ID
    for cliente in clientes:
        if int(cliente['id_cliente']) == args.id_cliente:
            mostrar_error("agregar_cliente", f"Ya existe un cliente con el ID {args.id_cliente}")
            return
    
    nuevo_cliente = {
        'id_cliente': str(args.id_cliente),
        'nombre': args.name,
        'email': args.email,
        'telefono': args.phone,
        'direccion': args.address,
        'localidad': args.city,
        'provincia': args.province,
        'codigo_postal': args.postal_code
    }
    
    clientes.append(nuevo_cliente)
    escribir_clientes(clientes)
    mostrar_exito("alta cliente")

def editar_cliente(args):
    if not args.id_cliente:
        mostrar_error("editar_cliente", "Se requiere el ID del cliente")
        return
        
    clientes = leer_clientes()
    cliente_encontrado = False
    
    for cliente in clientes:
        if int(cliente['id_cliente']) == args.id_cliente:
            cliente_encontrado = True
            if args.name:
                cliente['nombre'] = args.name
            if args.email:
                if '@' not in args.email:
                    mostrar_error("editar_cliente", "Email inválido")
                    return
                cliente['email'] = args.email
            if args.phone:
                if not (9 <= len(args.phone) <= 15):
                    mostrar_error("editar_cliente", "Teléfono inválido")
                    return
                cliente['telefono'] = args.phone
            if args.address:
                cliente['direccion'] = args.address
            if args.city:
                cliente['localidad'] = args.city
            if args.province:
                cliente['provincia'] = args.province
            if args.postal_code:
                if not (len(args.postal_code) == 5 and args.postal_code.isdigit()):
                    mostrar_error("editar_cliente", "Código postal inválido")
                    return
                cliente['codigo_postal'] = args.postal_code
    
    if not cliente_encontrado:
        mostrar_error("editar_cliente", f"No existe un cliente con el ID {args.id_cliente}")
        return
    
    escribir_clientes(clientes)
    mostrar_exito("modificación cliente")

def tiene_pedidos_activos(id_cliente):
    with open(ARCHIVO_PEDIDOS, 'r', encoding='utf-8') as f:
        pedidos = json.load(f)
        return any(pedido['id_cliente'] == id_cliente and pedido['estado'] == 'en curso' for pedido in pedidos)

def eliminar_cliente(args):
    if not args.id_cliente:
        mostrar_error("eliminar_cliente", "Se requiere el ID del cliente")
        return
    
    if tiene_pedidos_activos(args.id_cliente):
        mostrar_error("eliminar_cliente", f"No se puede eliminar el cliente {args.id_cliente} porque tiene pedidos en curso")
        return
    
    clientes = leer_clientes()
    clientes_actualizados = [c for c in clientes if int(c['id_cliente']) != args.id_cliente]
    
    if len(clientes) == len(clientes_actualizados):
        mostrar_error("eliminar_cliente", f"No existe un cliente con el ID {args.id_cliente}")
        return
    
    escribir_clientes(clientes_actualizados)
    mostrar_exito("eliminación cliente")

def buscar_clientes(args):
    clientes = leer_clientes()
    resultados = []
    
    for cliente in clientes:
        if (args.name is None or args.name.lower() in cliente['nombre'].lower()) and \
        (args.city is None or args.city.lower() in cliente['localidad'].lower()) and \
        (args.email is None or args.email.lower() in cliente['email'].lower()) and \
        (args.province is None or args.province.lower() in cliente['provincia'].lower()):
            resultados.append(cliente)
    
    mostrar_exito("búsqueda cliente")
    if resultados:
        print("\nResultados encontrados:")
        for cliente in resultados:
            print(f"\nID: {cliente['id_cliente']}")
            print(f"Nombre: {cliente['nombre']}")
            print(f"Email: {cliente['email']}")
            print(f"Teléfono: {cliente['telefono']}")
            print(f"Dirección: {cliente['direccion']}")
            print(f"Localidad: {cliente['localidad']}")
            print(f"Provincia: {cliente['provincia']}")
            print(f"Código Postal: {cliente['codigo_postal']}")
    else:
        print("\nNo se encontraron clientes con los criterios especificados")

# gestion de productos
      
def leer_productos():
    productos = []
    with open(ARCHIVO_PRODUCTOS, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f,delimiter=';')
        for row in reader:
            productos.append(row)
    return productos

def escribir_productos(productos):
    with open(ARCHIVO_PRODUCTOS, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CABECERA_PRODUCTOS, delimiter=';')
        writer.writeheader()
        writer.writerows(productos)

def agregar_producto(args):
    # Verificación de datos obligatorios
    if not args.id_producto or not args.name or args.price is None or args.stock is None:
        mostrar_error("agregar_producto", "Faltan datos obligatorios del producto")
        return
            
    if args.price <= 0:
        mostrar_error("agregar_producto", "El precio debe ser positivo")
        return
            
    if args.stock < 0:
        mostrar_error("agregar_producto", "El stock no puede ser negativo")
        return
            
    productos = leer_productos()
    
    # Verificar si existe el ID
    for producto in productos:
        if int(producto['id_producto']) == args.id_producto:
            mostrar_error("agregar_producto", f"Ya existe un producto con el ID {args.id_producto}")
            return
    
    # Si pasa todas las validaciones, crear el nuevo producto
    nuevo_producto = {
        'id_producto': str(args.id_producto),
        'nombre': args.name,
        'categoria': args.category if args.category else "",
        'precio': str(args.price),
        'stock': str(args.stock)
    }
    
    productos.append(nuevo_producto)
    escribir_productos(productos)
    mostrar_exito("alta producto")

def modificar_precio(args):
    if not args.id_producto or not args.price:
        mostrar_error("modificar_precio", "Se requiere ID del producto y nuevo precio")
        return
            
    if args.price <= 0:
        mostrar_error("modificar_precio", "El precio debe ser positivo")
        return
            
    productos = leer_productos()
    producto_encontrado = False
    
    # Solo imprimimos el ID que queremos modificar una vez
    print(f"ID del producto a modificar: {args.id_producto}")
    
    for producto in productos:
        if int(producto['id_producto']) == args.id_producto:
            producto_encontrado = True
            producto['precio'] = str(args.price)
                
    if not producto_encontrado:
        mostrar_error("modificar_precio", f"No existe un producto con el ID {args.id_producto}")
        return
            
    escribir_productos(productos)#escribimos los productos
    mostrar_exito("modificación precio")

def actualizar_stock(args):
    if not args.id_producto or args.quantity is None:
        mostrar_error("actualizar_stock", "Se requiere ID del producto y cantidad")
        return
        
    productos = leer_productos()
    producto_encontrado = False
    
    for producto in productos:
        if int(producto['id_producto']) == args.id_producto:
            producto_encontrado = True
            nuevo_stock = int(producto['stock']) + args.quantity
            if nuevo_stock < 0:
                mostrar_error("actualizar_stock", "El stock no puede ser negativo")
                return
            producto['stock'] = str(nuevo_stock)
            
    if not producto_encontrado:
        mostrar_error("actualizar_stock", f"No existe un producto con el ID {args.id_producto}")
        return
        
    escribir_productos(productos)
    mostrar_exito("actualización stock")

def tiene_pedidos_producto(id_producto):
    with open(ARCHIVO_PEDIDOS, 'r', encoding='utf-8') as f:
        pedidos = json.load(f)
        return any(id_producto in [item['id_producto'] for item in pedido['productos']] and pedido['estado'] == 'en curso' for pedido in pedidos)

def eliminar_producto(args):
    if not args.id_producto:
        mostrar_error("eliminar_producto", "Se requiere el ID del producto")
        return
        
    if tiene_pedidos_producto(args.id_producto):
        mostrar_error("eliminar_producto", f"No se puede eliminar el producto {args.id_producto} porque está en pedidos activos")
        return
        
    productos = leer_productos()
    productos_actualizados = [p for p in productos if int(p['id_producto']) != args.id_producto]
    
    if len(productos) == len(productos_actualizados):
        mostrar_error("eliminar_producto", f"No existe un producto con el ID {args.id_producto}")
        return
        
    escribir_productos(productos_actualizados)
    mostrar_exito("eliminación producto")

def buscar_productos(args):
    productos = leer_productos()
    resultados = []
    
    for producto in productos:
        if ((not args.name or args.name.lower() in producto['nombre'].lower()) and
            (not args.category or args.category.lower() in producto['categoria'].lower())):
            resultados.append(producto)
    
    mostrar_exito("búsqueda producto")
    if resultados:
        print("\nResultados encontrados:")
        for producto in resultados:
            print(f"\nID: {producto['id_producto']}")
            print(f"Nombre: {producto['nombre']}")
            print(f"Categoría: {producto['categoria']}")
            print(f"Precio: {producto['precio']}")
            print(f"Stock: {producto['stock']}")
    else:
        print("\nNo se encontraron productos con los criterios especificados")

#gestion de pedidos
def leer_pedidos():
    if not os.path.exists(ARCHIVO_PEDIDOS):
        return []
    with open(ARCHIVO_PEDIDOS, 'r', encoding='utf-8') as f:
        return json.load(f)

def escribir_pedidos(pedidos):
    with open(ARCHIVO_PEDIDOS, 'w', encoding='utf-8') as f:
        json.dump(pedidos, f, indent=4)

def verificar_cliente_existe(id_cliente):
    clientes = leer_clientes()
    return any(int(cliente['id_cliente']) == id_cliente for cliente in clientes)

def verificar_producto_existe(id_producto):
    productos = leer_productos()
    return any(int(producto['id_producto']) == id_producto for producto in productos)

def parsear_productos(productos_str):
    productos = []
    items = productos_str.split(',')
    for item in items:
        id_prod, cantidad = item.split(':')
        productos.append({
            'id_producto': int(id_prod),
            'cantidad': int(cantidad)
        })
    return productos

def realizar_pedido(args):
    if not args.id_pedido or not args.id_cliente or not args.products:
        mostrar_error("realizar_pedido", "Faltan datos obligatorios del pedido")
        return

    # Verificar que existe el cliente
    if not verificar_cliente_existe(args.id_cliente):
        mostrar_error("realizar_pedido", f"No existe un cliente con el ID {args.id_cliente}")
        return

    # Obtener los productos y sus precios
    productos_db = leer_productos()
    productos_pedido = []
    
    # Parsear la lista de productos del pedido (ej: "1:2,2:3")
    items = args.products.split(',')
    for item in items:
        id_prod, cantidad = map(int, item.split(':'))
        
        # Buscar el producto y su precio en la base de datos
        producto_encontrado = False
        for prod_db in productos_db:
            if int(prod_db['id_producto']) == id_prod:
                producto_encontrado = True
                productos_pedido.append({
                    'id_producto': id_prod,
                    'cantidad': cantidad,
                    'precio': float(prod_db['precio'])  # Guardamos el precio actual
                })
                break
                
        if not producto_encontrado:
            mostrar_error("realizar_pedido", f"No existe el producto con ID {id_prod}")
            return

    # Crear el nuevo pedido
    nuevo_pedido = {
        'id_pedido': args.id_pedido,
        'id_cliente': args.id_cliente,
        'fecha_creacion': datetime.now().strftime("%Y-%m-%d"),
        'fecha_servicio': None,
        'productos': productos_pedido,  # Ahora incluye el precio de cada producto
        'estado': "en curso",
        'observaciones': args.observations if args.observations else ""
    }

    # Guardar el pedido
    pedidos = leer_pedidos()
    if any(pedido['id_pedido'] == args.id_pedido for pedido in pedidos):
        mostrar_error("realizar_pedido", f"Ya existe un pedido con el ID {args.id_pedido}")
        return

    pedidos.append(nuevo_pedido)
    escribir_pedidos(pedidos)
    mostrar_exito("alta pedido")
    

def actualizar_pedido(args):
    if not args.id_pedido:
        mostrar_error("actualizar_pedido", "Se requiere el ID del pedido")
        return

    pedidos = leer_pedidos()
    
    # Buscar el pedido a modificar
    pedido_encontrado = False
    for pedido in pedidos:
        if pedido['id_pedido'] == args.id_pedido:
            if pedido['estado'] != "en curso":
                mostrar_error("actualizar_pedido", "Solo se pueden modificar pedidos en curso")
                return
                
            # Añadir productos
            if args.add_products:
                productos_db = leer_productos()
                items = args.add_products.split(',')
                for item in items:
                    id_prod, cantidad = map(int, item.split(':'))
                    # Buscar precio del producto
                    for prod in productos_db:
                        if int(prod['id_producto']) == id_prod:
                            pedido['productos'].append({
                                'id_producto': id_prod,
                                'cantidad': cantidad,
                                'precio': float(prod['precio'])
                            })
                            
            # Eliminar productos
            if args.remove_products:
                id_eliminar = int(args.remove_products.split(':')[0])
                pedido['productos'] = [p for p in pedido['productos'] 
                                     if p['id_producto'] != id_eliminar]
            
            pedido_encontrado = True
            break
    
    if not pedido_encontrado:
        mostrar_error("actualizar_pedido", f"No existe un pedido con el ID {args.id_pedido}")
        return

    escribir_pedidos(pedidos)
    mostrar_exito("modificación pedido")

def agregar_observacion(args):
    if not args.id_pedido or not args.observations:
        mostrar_error("agregar_observacion", "Se requiere el ID del pedido y la observación")
        return 
    
    pedidos = leer_pedidos()
    pedido_encontrado = False

    for pedido in pedidos:
        if pedido['id_pedido'] == args.id_pedido:
            if pedido['estado'] != "en curso":
                mostrar_error("agregar_observacion", "Solo se pueden añadir observaciones a pedidos en curso")
                return
            
            # Si ya hay una observación, añadir la nueva con un separador
            if pedido['observaciones']:
                pedido['observaciones'] += f" | {args.observations}"
            else:
                # Si no hay observación previa, añadir la nueva directamente
                pedido['observaciones'] = args.observations
                
            pedido_encontrado = True
            break
           
    if not pedido_encontrado:
        mostrar_error("agregar_observacion", f"No existe un pedido con el ID {args.id_pedido}")
        return
    
    escribir_pedidos(pedidos)
    mostrar_exito("añadir observación")


def verificar_stock_suficiente(productos_pedido):
    productos_db = leer_productos()
    for prod_pedido in productos_pedido:
        for producto in productos_db:
            if int(producto['id_producto']) == prod_pedido['id_producto']:
                if int(producto['stock']) < prod_pedido['cantidad']:
                    return False
    return True

def actualizar_stock_productos(productos_pedido):
    productos = leer_productos()
    for prod_pedido in productos_pedido:
        for producto in productos:
            if int(producto['id_producto']) == prod_pedido['id_producto']:
                nuevo_stock = int(producto['stock']) - prod_pedido['cantidad']
                producto['stock'] = str(nuevo_stock)
    escribir_productos(productos)

def servir_pedido(args):
    if not args.id_pedido:
        mostrar_error("servir_pedido", "Se requiere el ID del pedido")
        return

    pedidos = leer_pedidos()
    pedido = None
    for p in pedidos:
        if p['id_pedido'] == args.id_pedido:
            pedido = p
            break

    if not pedido:
        mostrar_error("servir_pedido", f"No existe un pedido con el ID {args.id_pedido}")
        return

    if pedido['estado'] != "en curso":
        mostrar_error("servir_pedido", "Solo se pueden servir pedidos en curso")
        return

    # Verificar que haya stock suficiente
    productos_db = leer_productos()
    for producto_pedido in pedido['productos']:
        for producto in productos_db:
            if int(producto['id_producto']) == producto_pedido['id_producto']:
                if int(producto['stock']) < producto_pedido['cantidad']:
                    mostrar_error("servir_pedido", "No hay stock suficiente")
                    return

    # Actualizar el stock
    for producto_pedido in pedido['productos']:
        for producto in productos_db:
            if int(producto['id_producto']) == producto_pedido['id_producto']:
                nuevo_stock = int(producto['stock']) - producto_pedido['cantidad']
                producto['stock'] = str(nuevo_stock)

    # Actualizar el pedido
    pedido['estado'] = "servido"
    pedido['fecha_servicio'] = datetime.now().strftime("%Y-%m-%d")

    escribir_productos(productos_db)
    escribir_pedidos(pedidos)
    mostrar_exito("servir pedido")

def anular_pedido(args):
    if not args.id_pedido:
        mostrar_error("anular_pedido", "Se requiere el ID del pedido")
        return

    pedidos = leer_pedidos()
    pedido = None
    indice = -1
    for i, p in enumerate(pedidos):
        if p['id_pedido'] == args.id_pedido:
            pedido = p
            indice = i
            break

    if not pedido:
        mostrar_error("anular_pedido", f"No existe un pedido con el ID {args.id_pedido}")
        return

    if pedido['estado'] == "servido":
        mostrar_error("anular_pedido", "No se puede anular un pedido servido")
        return

    pedidos.pop(indice)
    escribir_pedidos(pedidos)
    mostrar_exito("anulación pedido")


def analisis_ventas(args):
    pedidos = leer_pedidos()
    ventas_generadas_mes = 0
    print("ANALISIS DE VENTAS")
    print(f"Productos{'':8}Unidades{'':8}Total Precio")
    print("-" * 44)
    
    # Convertir nombre del mes en inglés a número
    mes_numero = datetime.strptime(args.month, "%B").month#El formato %B le dice a strptime que espere el nombre completo del mes en inglés y .month extrae el número del mes.
    if(mes_numero < 10):
        mes_numero = f"0{mes_numero}"
    
    resumen_ventas = {}
    for pedido in pedidos:
        fecha = pedido['fecha_creacion']
        if fecha.startswith(f"{args.year}-{mes_numero}"):
            for producto in pedido['productos']:
                id_producto = producto['id_producto']
                cantidad = producto['cantidad']
                precio = producto['precio']
                ventas_generadas_mes += float(producto['precio'])*int(producto['cantidad'])
                if id_producto in resumen_ventas:
                    resumen_ventas[id_producto]['unidades'] += cantidad
                    resumen_ventas[id_producto]['total'] += cantidad * precio
                else:
                    resumen_ventas[id_producto] = {'unidades': cantidad, 'total': cantidad * precio}
    resumen_ventas = sorted(resumen_ventas.items(), key=lambda x: x[1]['total'], reverse=True)
    for producto, resumen in resumen_ventas:
        print(f"{producto:<17}{resumen['unidades']:<16}{resumen['total']:.2f}")
        
    print("-" * 44)
    print(f"PRECIO TOTAL MES: {ventas_generadas_mes:.2f}")

def buscar_pedidos(args):
    pedidos = leer_pedidos()
    resultados = []

    for pedido in pedidos:
        if ((not args.id_cliente or pedido['id_cliente'] == args.id_cliente) and
            (not args.status or pedido['estado'] == args.status)):
            resultados.append(pedido)

    mostrar_exito("búsqueda pedido")
    if resultados:
        print("\nResultados encontrados:")
        for pedido in resultados:
            print(f"\nID Pedido: {pedido['id_pedido']}")
            print(f"ID Cliente: {pedido['id_cliente']}")
            print(f"Estado: {pedido['estado']}")
            if 'prioridad' in pedido and pedido['estado'] == "en curso":
                print(f"Prioridad: {pedido['prioridad']}")
            print(f"Fecha creación: {pedido['fecha_creacion']}")
            if pedido['fecha_servicio']:
                print(f"Fecha servicio: {pedido['fecha_servicio']}")
            print("Productos:")
            for producto in pedido['productos']:
                print(f"  - ID: {producto['id_producto']}, Cantidad: {producto['cantidad']}")
            if pedido['observaciones']:
                print(f"Observaciones: {pedido['observaciones']}")
    else:
        print("\nNo se encontraron pedidos con los criterios especificados")


def configurar_parser():
    parser = argparse.ArgumentParser(description='Sistema de Gestión de Ventas')
    
    # Comandos para Gestión de Clientes
    parser.add_argument('--add-customer', action='store_true', help='Añadir nuevo cliente')
    parser.add_argument('--edit-customer', action='store_true', help='Modificar cliente existente')
    parser.add_argument('--delete-customer', action='store_true', help='Eliminar cliente')
    parser.add_argument('--search-customer', action='store_true', help='Buscar clientes')
    
    # Argumentos para clientes
    parser.add_argument('--id_cliente', type=int, help='ID del cliente')
    parser.add_argument('--name', type=str, help='Nombre del cliente')
    parser.add_argument('--email', type=str, help='Email del cliente')
    parser.add_argument('--phone', type=str, help='Teléfono del cliente')
    parser.add_argument('--address', type=str, help='Dirección del cliente')
    parser.add_argument('--city', type=str, help='Ciudad del cliente')
    parser.add_argument('--province', type=str, help='Provincia del cliente')
    parser.add_argument('--postal_code', type=str, help='Código postal del cliente')

    # Comandos para Gestión de Productos
    parser.add_argument('--add-product', action='store_true', help='Añadir nuevo producto')
    parser.add_argument('--edit-product', action='store_true', help='Modificar precio de producto')
    parser.add_argument('--update-stock', action='store_true', help='Actualizar stock de producto')
    parser.add_argument('--delete-product', action='store_true', help='Eliminar producto')
    parser.add_argument('--search-product', action='store_true', help='Buscar productos')
    
    # Argumentos para productos
    parser.add_argument('--id_producto', type=int, help='ID del producto')
    parser.add_argument('--category', type=str, help='Categoría del producto')
    parser.add_argument('--price', type=float, help='Precio del producto')
    parser.add_argument('--stock', type=int, help='Stock del producto')
    parser.add_argument('--quantity', type=int, help='Cantidad a añadir/restar del stock')

    

    # Comandos para Gestión de Pedidos
    parser.add_argument('--make-order', action='store_true', help='Realizar un pedido')
    parser.add_argument('--edit-order', action='store_true', help='Actualizar un pedido')
    parser.add_argument('--serve-order', action='store_true', help='Servir un pedido')
    parser.add_argument('--cancel-order', action='store_true', help='Anular un pedido')
    parser.add_argument('--search-order', action='store_true', help='Buscar pedidos')
    parser.add_argument('--analyze-sales', action='store_true', help='Análisis de ventas')
    parser.add_argument('--add-observation', action= 'store_true', help='Observación a añadir al pedido')

    # Argumentos para pedidos
    parser.add_argument('--id_pedido', type=int, help='ID del pedido')
    parser.add_argument('--products', type=str, help='Lista de productos y cantidades (formato: "id:cantidad,id:cantidad")')
    parser.add_argument('--observations', type=str, help='Observación para el pedido')
    parser.add_argument('--month', type=str, help='Mes para análisis de ventas')
    parser.add_argument('--year', type=str, help='Año para análisis de ventas')
    parser.add_argument('--status', type=str, help='Estado del pedido')
    parser.add_argument('--start_date', type=str, help='Fecha inicio para búsqueda')
    parser.add_argument('--end_date', type=str, help='Fecha fin para búsqueda')
    parser.add_argument('--add-products', type=str, help='Productos a añadir (formato: "id:cantidad,id:cantidad")')
    parser.add_argument('--remove-products', type=str, help='Productos a eliminar (formato: "id:cantidad,id:cantidad")')
    
    #argumento para la copia de seguridad

    parser.add_argument('--backup-data', action='store_true', help='Crear copia de seguridad')
    parser.add_argument('--destination', type=str, help='Carpeta destino del backup')

    #argumento para asignar prioridades 
    parser.add_argument('--set-order-priority', action='store_true', help='Asignar prioridad a un pedido')
    parser.add_argument('--priority', type=str, help='Prioridad del pedido (alta/media/baja)')

    # Comando para producto más vendido
    parser.add_argument('--most-sold-product', action='store_true', help='Mostrar producto más vendido')
    parser.add_argument('--start-date', type=str, help='Fecha inicio (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='Fecha fin (YYYY-MM-DD)')

    #comando para buscar productos cercanos a agotarse
    parser.add_argument('--low-stock-products', action='store_true', help='Buscar productos con stock bajo')
    parser.add_argument('--threshold', type=int, help='Límite de stock para la búsqueda')
    
    #comando consolidar pedidos en uno solo
    parser.add_argument('--merge-orders', action='store_true', help='Consolidar varios pedidos en uno')
    parser.add_argument('--id_pedidos', type=str, help='IDs de pedidos a consolidar (separados por comas)')


    return parser

def crear_backup(args):
    if not args.destination:
        mostrar_error("crear_backup", "Se requiere especificar la carpeta de destino con --destination")
        return
        
    # Verificar que la carpeta existe
    if not os.path.exists(args.destination):
        mostrar_error("crear_backup", "La carpeta backups/ no existe")
        return
    
    # Verificar que los archivos fuente existen y son legibles
    archivos = [ARCHIVO_CLIENTES, ARCHIVO_PRODUCTOS, ARCHIVO_PEDIDOS]
    for archivo in archivos:
        if not os.path.exists(archivo):
            mostrar_error("crear_backup", f"El archivo {archivo} no existe")
            return
        if not os.access(archivo, os.R_OK):
            mostrar_error("crear_backup", f"No hay permisos de lectura en el archivo {archivo}")
            return
    
    # Crear nombre del archivo zip con la fecha y hora actual
    fecha_hora = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    nombre_zip = os.path.join(args.destination, f"{fecha_hora}.zip")
    
    # Crear el archivo zip
    with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for archivo in archivos:
            zipf.write(archivo, os.path.basename(archivo))
    
    # Verificar que el archivo zip se creó correctamente
    if os.path.exists(nombre_zip) and os.path.getsize(nombre_zip) > 0:
        mostrar_exito("backup")
    else:
        mostrar_error("crear_backup", "Error al crear el archivo de backup")
        if os.path.exists(nombre_zip):
            os.remove(nombre_zip)
def asignar_prioridad(args):
    if not args.id_pedido:
        mostrar_error("asignar_prioridad", "Se requiere el ID del pedido")
        return
        
    if not args.priority or args.priority.lower() not in ["alta", "media", "baja"]:
        mostrar_error("asignar_prioridad", "La prioridad debe ser 'alta', 'media' o 'baja'")
        return
    
    pedidos = leer_pedidos()
    pedido_encontrado = False
    
    for pedido in pedidos:
        if pedido['id_pedido'] == args.id_pedido:
            if pedido['estado'] != "en curso":
                mostrar_error("asignar_prioridad", "Solo se puede asignar prioridad a pedidos en curso")
                return
                
            pedido['prioridad'] = args.priority.lower()
            pedido_encontrado = True
            break
            
    if not pedido_encontrado:
        mostrar_error("asignar_prioridad", f"No existe un pedido con el ID {args.id_pedido}")
        return
    
    escribir_pedidos(pedidos)
    mostrar_exito("asignación prioridad")

def obtener_producto_mas_vendido(args):
    if not args.start_date or not args.end_date:
        mostrar_error("obtener_producto_mas_vendido", "Se requiere fecha inicio y fin")
        return
    
    try:
        fecha_inicio = datetime.strptime(args.start_date, "%Y-%m-%d")
        fecha_fin = datetime.strptime(args.end_date, "%Y-%m-%d")
    except ValueError:
        mostrar_error("obtener_producto_mas_vendido", "Formato de fecha incorrecto. Usar YYYY-MM-DD")
        return

    pedidos = leer_pedidos()
    productos = leer_productos()
    ventas_por_producto = {}

    # Contar ventas por producto en el período especificado
    for pedido in pedidos:
        fecha_pedido = datetime.strptime(pedido['fecha_creacion'], "%Y-%m-%d")
        
        if fecha_inicio <= fecha_pedido <= fecha_fin:
            for producto in pedido['productos']:
                id_producto = producto['id_producto']
                cantidad = producto['cantidad']
                
                if id_producto in ventas_por_producto:
                    ventas_por_producto[id_producto] += cantidad
                else:
                    ventas_por_producto[id_producto] = cantidad

    # Encontrar el producto más vendido
    if not ventas_por_producto:
        print("No se encontraron ventas en el período especificado")
        return

    id_mas_vendido = max(ventas_por_producto.keys(), 
                        key=lambda k: ventas_por_producto[k])
    
    # Buscar el nombre del producto
    nombre_producto = None
    for producto in productos:
        if int(producto['id_producto']) == id_mas_vendido:
            nombre_producto = producto['nombre']
            break

    mostrar_exito("consulta producto más vendido")
    print(f"\nProducto más vendido en el período {args.start_date} a {args.end_date}:")
    print(f"ID: {id_mas_vendido}")
    print(f"Nombre: {nombre_producto}")
    print(f"Unidades vendidas: {ventas_por_producto[id_mas_vendido]}")

def buscar_stock_bajo(args):
    if not args.threshold:
        mostrar_error("buscar_stock_bajo", "Se requiere especificar el límite de stock con --threshold")
        return
    
    if args.threshold < 0:
        mostrar_error("buscar_stock_bajo", "El límite de stock debe ser un número positivo")
        return
        
    productos = leer_productos()
    productos_bajo_stock = []
    
    for producto in productos:
        if int(producto['stock']) <= args.threshold:
            productos_bajo_stock.append(producto)
    
    mostrar_exito("búsqueda productos stock bajo")
    if productos_bajo_stock:
        print(f"\nProductos con stock menor o igual a {args.threshold}:")
        for producto in productos_bajo_stock:
            print(f"ID: {producto['id_producto']} | Nombre: {producto['nombre']}")
    else:
        print(f"\nNo se encontraron productos con stock menor o igual a {args.threshold}")


def consolidar_pedidos(args):
   if not args.id_pedidos:
       mostrar_error("consolidar_pedidos", "Se requiere especificar los IDs de pedidos")
       return
       
   # Convertir string de IDs a lista de enteros(idea del chat gpt)
   try:
       ids_pedidos = [int(id.strip()) for id in args.id_pedidos.split(',')]
   except ValueError:
       mostrar_error("consolidar_pedidos", "Formato de IDs incorrecto")
       return
       
   pedidos = leer_pedidos()
   pedidos_a_consolidar = []
   id_cliente = None
   
   # Verificar que todos los pedidos existen y cumplen las condiciones
   for id_pedido in ids_pedidos:
       pedido_encontrado = False
       for pedido in pedidos:
           if pedido['id_pedido'] == id_pedido:
               pedido_encontrado = True
               
               # Verificar que el pedido no está servido
               if pedido['estado'] != "en curso":
                   mostrar_error("consolidar_pedidos", f"El pedido {id_pedido} ya está servido")
                   return
                   
               # Verificar que todos los pedidos son del mismo cliente
               if id_cliente is None:
                   id_cliente = pedido['id_cliente']
               elif id_cliente != pedido['id_cliente']:
                   mostrar_error("consolidar_pedidos", "Los pedidos deben ser del mismo cliente")
                   return
                   
               pedidos_a_consolidar.append(pedido)
               break
               
       if not pedido_encontrado:
           mostrar_error("consolidar_pedidos", f"No existe el pedido {id_pedido}")
           return
   
   # Crear el nuevo pedido consolidado
   productos_consolidados = []
   for pedido in pedidos_a_consolidar:
       productos_consolidados.extend(pedido['productos'])
   
   # Combinar productos iguales sumando cantidades
   productos_combinados = {}
   for producto in productos_consolidados:
       id_prod = producto['id_producto']
       if id_prod in productos_combinados:
           productos_combinados[id_prod]['cantidad'] += producto['cantidad']
       else:
           productos_combinados[id_prod] = {'id_producto': id_prod,'cantidad': producto['cantidad'],'precio': producto['precio']}
   
   # Crear nuevo pedido
   nuevo_pedido = {
       'id_pedido': max([p['id_pedido'] for p in pedidos]) + 1,
       'id_cliente': id_cliente,
       'fecha_creacion': datetime.now().strftime("%Y-%m-%d"),
       'fecha_servicio': None,
       'productos': list(productos_combinados.values()),
       'estado': "en curso",
       'observaciones': "Pedido consolidado de: " + args.id_pedidos
   }
   
   # Eliminar pedidos antiguos y añadir el nuevo
   pedidos_actualizados = [p for p in pedidos if p['id_pedido'] not in ids_pedidos]
   pedidos_actualizados.append(nuevo_pedido)
   
   escribir_pedidos(pedidos_actualizados)
   mostrar_exito("consolidación pedidos")
   print(f"Nuevo pedido creado con ID: {nuevo_pedido['id_pedido']}")

def main():
    parser = configurar_parser()
    args = parser.parse_args()

    verificar_archivos()
    
    # Gestión de Clientes
    if args.add_customer:
        agregar_cliente(args)
    elif args.edit_customer:
        editar_cliente(args)
    elif args.delete_customer:
        eliminar_cliente(args)
    elif args.search_customer:
        buscar_clientes(args)

    # Funcionalidades ampliadas
    elif args.backup_data:
        crear_backup(args)
    elif args.set_order_priority:
        asignar_prioridad(args)
    elif args.most_sold_product:
        obtener_producto_mas_vendido(args)
    elif args.low_stock_products:
        buscar_stock_bajo(args)
    elif args.merge_orders:
       consolidar_pedidos(args)

    # Gestión de Productos
    elif args.add_product:
        agregar_producto(args)
    elif args.edit_product:
        modificar_precio(args)
    elif args.update_stock:
        actualizar_stock(args)
    elif args.delete_product:
        eliminar_producto(args)
    elif args.search_product:
        buscar_productos(args)            

    # Gestión de Pedidos
    elif args.add_observation:
        agregar_observacion(args)
    elif args.make_order:
        realizar_pedido(args)
    elif args.edit_order:
        actualizar_pedido(args)
    elif args.serve_order:
        servir_pedido(args)
    elif args.cancel_order:
        anular_pedido(args)
    elif args.search_order:
        buscar_pedidos(args)
    elif args.analyze_sales:
        analisis_ventas(args)
    else:
        mostrar_error("comando", "Comando no reconocido")

if __name__ == "__main__":
    main()
