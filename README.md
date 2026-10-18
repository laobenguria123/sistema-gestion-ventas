# Sistema de gestión de ventas (CLI en Python)

Aplicación de línea de comandos para gestionar los **clientes, productos y pedidos** de una tienda. Valida los datos, controla el stock, analiza las ventas y hace copias de seguridad. Usa solo la biblioteca estándar de Python.

Trabajo final de la asignatura Fundamentos de Programación del Grado en Ciencia de Datos e Inteligencia Artificial (Universidad Miguel Hernández), curso 2024–25.

## Funcionalidades

| Área | Comandos | Qué hace |
|---|---|---|
| Clientes | `--add-customer`, `--edit-customer`, `--delete-customer`, `--search-customer` | Alta, modificación, baja y búsqueda. Valida el email, el teléfono y el código postal, y no deja borrar clientes con pedidos en curso |
| Productos | `--add-product`, `--edit-product`, `--update-stock`, `--delete-product`, `--search-product` | Catálogo con precio y stock. No permite stock negativo ni borrar productos que estén en pedidos activos |
| Pedidos | `--make-order`, `--edit-order`, `--serve-order`, `--cancel-order`, `--search-order`, `--add-observation` | Ciclo de vida completo del pedido (en curso → servido). Al servirlo comprueba y descuenta el stock |
| Análisis | `--analyze-sales`, `--most-sold-product`, `--low-stock-products` | Resumen de ventas mensual por producto, producto más vendido en un periodo y productos con stock bajo |
| Utilidades | `--set-order-priority`, `--merge-orders`, `--backup-data` | Prioridad de pedidos, consolidación de varios pedidos en uno y copia de seguridad en `.zip` |

Los datos se guardan en `clientes.csv` y `productos.csv` (separados por `;`) y en `pedidos.json`. El repositorio incluye datos de ejemplo ficticios.

## Uso

Requiere Python 3.8 o superior. No necesita instalar dependencias.

```bash
# Alta de un cliente
python app.py --add-customer --id_cliente 3 --name "Ana López" --email ana@ejemplo.com \
  --phone 600555666 --address "Calle Sol 4" --city Elche --province Alicante --postal_code 03202

# Pedido con varios productos (formato id:cantidad)
python app.py --make-order --id_pedido 5 --id_cliente 3 --products "101:1,102:2"

# Servir el pedido (descuenta el stock)
python app.py --serve-order --id_pedido 5

# Análisis de ventas de un mes (nombre del mes en inglés)
python app.py --analyze-sales --month October --year 2026
```

Ejemplo de salida del análisis de ventas:

```
ANALISIS DE VENTAS
Productos        Unidades        Total Precio
--------------------------------------------
101              1               799.90
103              3               687.00
102              7               174.93
--------------------------------------------
PRECIO TOTAL MES: 1661.83
```

Otros ejemplos:

```bash
python app.py --most-sold-product --start-date 2026-01-01 --end-date 2026-12-31
python app.py --low-stock-products --threshold 5
python app.py --merge-orders --id_pedidos 2,3
mkdir backups && python app.py --backup-data --destination backups
python app.py --help   # lista completa de opciones
```

## Autor

Marcos Samuel Lao Benguria — [LinkedIn](https://www.linkedin.com/in/marcos-samuel-lao-benguria-a17791255/) · [GitHub](https://github.com/laobenguria123)
