"""
Paquete de modelos de dominio.
Expone las clases principales para importaciones limpias.
"""
from .producto import DescuentoMixin, Electronico, Libro, Producto

__all__ = [
    "Producto",
    "Electronico",
    "Libro",
    "DescuentoMixin",
]

