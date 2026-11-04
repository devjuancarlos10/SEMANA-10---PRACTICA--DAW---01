"""
Módulo de utilidades de validación y sanitización de datos de entrada.
"""
from typing import Any, Optional, Type, TypeVar
from .exceptions import ValidationError

T = TypeVar("T", int, float)


def validar_numero(
    valor: str,
    tipo: Type[T] = float,
    min_val: Optional[float] = 0,
    max_val: Optional[float] = None,
) -> T:
    """
    Convierte y valida que un valor en cadena cumpla con el tipo numérico y rango esperado.

    :param valor: Cadena con el valor numérico ingresado.
    :param tipo: Tipo objetivo (int o float).
    :param min_val: Límite inferior permitido (inclusivo).
    :param max_val: Límite superior permitido (inclusivo).
    :return: El número convertido a su tipo correspondiente.
    :raises ValidationError: Si el formato es inválido o no respeta los límites.
    """
    if valor is None or not str(valor).strip():
        raise ValidationError("El valor numérico no puede estar vacío.")

    try:
        num = tipo(valor.strip())
    except (ValueError, TypeError):
        raise ValidationError(f"Formato numérico inválido: '{valor}'. Debe ser un número válido.")

    if min_val is not None and num < min_val:
        max_str = "inf" if max_val is None else str(max_val)
        raise ValidationError(f"Valor fuera de rango: {num} es menor al mínimo permitido ({min_val}). Rango: [{min_val} - {max_str}].")

    if max_val is not None and num > max_val:
        min_str = "-inf" if min_val is None else str(min_val)
        raise ValidationError(f"Valor fuera de rango: {num} es mayor al máximo permitido ({max_val}). Rango: [{min_str} - {max_val}].")

    return num


def validar_categoria(categoria: str) -> str:
    """
    Valida y normaliza la categoría de producto ingresada.

    :param categoria: Cadena ingresada por el usuario.
    :return: Categoría normalizada ('electronico' o 'libro').
    :raises ValidationError: Si la categoría no está soportada.
    """
    if not categoria or not categoria.strip():
        raise ValidationError("La categoría no puede estar vacía. Debe ser 'electronico' o 'libro'.")

    categoria_limpia = categoria.strip().lower()
    categorias_validas = {
        "electronico": "electronico",
        "electrónico": "electronico",
        "electronicos": "electronico",
        "electrónicos": "electronico",
        "libro": "libro",
        "libros": "libro",
    }

    if categoria_limpia not in categorias_validas:
        raise ValidationError(
            f"Categoría no válida: '{categoria}'. Opciones disponibles: 'electronico', 'libro'."
        )

    return categorias_validas[categoria_limpia]


def validar_texto(texto: str, campo: str = "campo") -> str:
    """
    Valida que un campo de texto no sea nulo ni contenga únicamente espacios en blanco.

    :param texto: Texto a validar.
    :param campo: Nombre descriptivo del campo para mensajes de error.
    :return: Cadena sin espacios periféricos.
    :raises ValidationError: Si el texto está vacío.
    """
    if texto is None or not texto.strip():
        raise ValidationError(f"El valor de '{campo}' no puede estar vacío.")
    return texto.strip()


def validar_booleano(valor: str, campo: str = "campo") -> bool:
    """
    Interpreta respuestas afirmativas o negativas de tipo sí/no (s/n, true/false).

    :param valor: Entrada ingresada.
    :param campo: Nombre del campo a reportar en errores.
    :return: Booleano representativo.
    :raises ValidationError: Si la opción no es reconocida.
    """
    if valor is None:
        raise ValidationError(f"Debe especificar una opción para '{campo}'.")

    limpio = valor.strip().lower()
    if limpio in {"s", "si", "sí", "true", "1", "y", "yes"}:
        return True
    if limpio in {"n", "no", "false", "0"}:
        return False

    raise ValidationError(f"Entrada inválida para '{campo}': '{valor}'. Ingrese 's' (Sí) o 'n' (No).")
