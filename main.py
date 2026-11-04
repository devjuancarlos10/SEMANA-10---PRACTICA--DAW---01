#!/usr/bin/env python3
"""
Orquestador CLI del Sistema de Gestión de Productos.
Controla el flujo de interacción, captura y canalización de excepciones,
y delegación a los modelos de dominio.
"""
from __future__ import annotations
import sys
from typing import Dict

# Asegurar codificación utf-8 tolerante en consolas de cualquier plataforma (Windows/Linux/macOS)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from models.producto import DescuentoMixin, Electronico, Libro, Producto
from utils.exceptions import NotFoundError, ValidationError
from utils.validators import (
    validar_booleano,
    validar_categoria,
    validar_numero,
    validar_texto,
)


def menu() -> str:
    """Muestra el menú principal de la consola y obtiene la opción del usuario."""
    print("\n" + "=" * 42)
    print("=== GESTIÓN DE PRODUCTOS (CLI) ===")
    print("=" * 42)
    print("1. Agregar Producto")
    print("2. Listar Productos")
    print("3. Calcular Precio Final")
    print("4. Salir")
    print("-" * 42)
    return input("Opción > ").strip()


def solicitar_datos_producto() -> Producto:
    """
    Solicita, sanitiza y valida por consola los datos requeridos para instanciar
    un producto de tipo Electrónico o Libro.
    """
    categoria_raw = input("Ingrese categoría (electronico / libro): ")
    categoria = validar_categoria(categoria_raw)

    nombre_raw = input("Nombre del producto: ")
    nombre = validar_texto(nombre_raw, campo="Nombre")

    precio_raw = input("Precio base (S/): ")
    precio_base = validar_numero(precio_raw, tipo=float, min_val=0.01)

    stock_raw = input("Cantidad en stock: ")
    stock = validar_numero(stock_raw, tipo=int, min_val=0)

    if categoria == "electronico":
        garantia_raw = input("Meses de garantía: ")
        garantia_meses = validar_numero(garantia_raw, tipo=int, min_val=0)
        return Electronico(
            nombre=nombre,
            precio_base=precio_base,
            stock=stock,
            garantia_meses=garantia_meses,
        )

    # Caso: libro
    autor_raw = input("Autor del libro: ")
    autor = validar_texto(autor_raw, campo="Autor")

    es_educativo_raw = input("¿Es libro educativo / texto técnico? (s/n): ")
    es_educativo = validar_booleano(es_educativo_raw, campo="Es educativo")

    return Libro(
        nombre=nombre,
        precio_base=precio_base,
        stock=stock,
        autor=autor,
        es_educativo=es_educativo,
    )


def listar_inventario(inventario: Dict[int, Producto]) -> None:
    """Imprime el listado tabular de todos los productos registrados."""
    if not inventario:
        print("\n📦 El catálogo se encuentra vacío. No hay productos registrados.")
        return

    print("\n" + "-" * 75)
    print(f"{'ID':<6} | {'DETALLE Y ESPECIFICACIONES':<65}")
    print("-" * 75)
    for prod_id, prod in inventario.items():
        print(f"#{prod_id:<5} | {prod}")
    print("-" * 75)
    print(f"Total de registros: {len(inventario)}")


def calcular_precio_producto(inventario: Dict[int, Producto]) -> None:
    """Busca un producto por ID y muestra el desglose de su precio final."""
    id_raw = input("Ingrese el ID del producto a cotizar: ")
    prod_id = validar_numero(id_raw, tipo=int, min_val=1)

    if prod_id not in inventario:
        raise NotFoundError(f"No existe ningún producto registrado con el ID #{prod_id}.")

    producto = inventario[prod_id]
    precio_final = producto.calcular_precio_final()

    print("\n" + "-" * 50)
    print(f"💰 COTIZACIÓN DE PRECIO FINAL: ID #{prod_id}")
    print("-" * 50)
    print(f"• Producto       : {producto.nombre}")
    print(f"• Categoría      : {producto.__class__.__name__}")
    print(f"• Precio Base    : S/ {producto.precio_base:.2f}")
    print(f"• Stock Actual   : {producto.stock} unidades")

    if isinstance(producto, Electronico):
        if producto.stock > Electronico.UMBRAL_STOCK_DESCUENTO:
            print(f"• Descuento Vol. : -{Electronico.DESCUENTO_ALTO_STOCK}% (Stock > 50)")
        print(f"• Tasa Impuesto  : IGV ({int(Electronico.TASA_IGV * 100)}%)")
        print(f"• Garantía       : {producto.garantia_meses} meses")
    elif isinstance(producto, Libro):
        tipo = "Educativo / Técnico (-10%)" if producto.es_educativo else "General (0% desc.)"
        print(f"• Autor          : {producto.autor}")
        print(f"• Régimen Libro  : {tipo} | Exonerado de IGV (0%)")

    print("-" * 50)
    print(f"➡️  PRECIO FINAL DE VENTA: S/ {precio_final:.2f}")
    print("-" * 50)


def main() -> None:
    """Bucle principal de ejecución del sistema con manejo exhaustivo de excepciones."""
    inventario: Dict[int, Producto] = {}
    contador_id = 1

    print("Iniciando Sistema de Gestión de Productos...")

    while True:
        hubo_error = False
        try:
            opcion = menu()

            if opcion == "1":
                nuevo_producto = solicitar_datos_producto()
                inventario[contador_id] = nuevo_producto
                print(f"\n✅ Producto agregado con éxito. Asignado con ID #{contador_id}.")
                contador_id += 1

            elif opcion == "2":
                listar_inventario(inventario)

            elif opcion == "3":
                calcular_precio_producto(inventario)

            elif opcion == "4":
                print("\nCerrando sistema... ¡Hasta luego!")
                break

            else:
                raise ValidationError("Opción inválida. Por favor, seleccione un número entre 1 y 4.")

        except ValidationError as e:
            hubo_error = True
            print(f"\n⚠️  Error de validación: {e}")

        except NotFoundError as e:
            hubo_error = True
            print(f"\n🔍 No encontrado: {e}")

        except Exception as e:
            hubo_error = True
            print(f"\n❌ Error inesperado: {e}")

        else:
            # Se ejecuta cuando el bloque try termina sin lanzar excepciones
            pass

        finally:
            # Se ejecuta en cada ciclo para garantizar consistencia y delimitación
            if hubo_error:
                print("ℹ️  Revise los datos ingresados e intente nuevamente.")


if __name__ == "__main__":
    main()
