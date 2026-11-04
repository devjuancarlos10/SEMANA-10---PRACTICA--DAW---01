"""
Módulo de excepciones personalizadas para el dominio de inventario y catálogo.
"""


class InventoryAppError(Exception):
    """Clase base de excepciones del sistema de inventario."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message: str = message

    def __str__(self) -> str:
        return self.message


class ValidationError(InventoryAppError):
    """Lanzada cuando una entrada de usuario o regla de negocio no cumple los requisitos."""

    pass


class NotFoundError(InventoryAppError):
    """Lanzada cuando un producto o registro solicitado no existe en el catálogo."""

    pass

