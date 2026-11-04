"""
Módulo de modelos de dominio para el catálogo de productos.
Implementa principios de POO: herencia, polimorfismo, encapsulamiento y herencia múltiple con Mixin.
"""
from __future__ import annotations
from typing import override
from utils.exceptions import ValidationError


class DescuentoMixin:
    """
    Mixin reutilizable que dota a las clases de catálogo de lógica para aplicar
    descuentos porcentuales promocionales sobre cálculos comerciales.
    Demuestra herencia múltiple y resolución cooperativa de métodos (MRO).
    """

    def aplicar_descuento_porcentual(self, monto: float, porcentaje: float) -> float:
        """
        Calcula el valor resultante tras deducir un porcentaje de descuento.

        :param monto: Importe base a descontar.
        :param porcentaje: Porcentaje de rebaja (0 a 100).
        :return: Monto final tras el descuento.
        :raises ValidationError: Si el porcentaje está fuera del rango [0, 100].
        """
        if not (0.0 <= porcentaje <= 100.0):
            raise ValidationError(
                f"El porcentaje de descuento debe estar entre 0 y 100. Valor recibido: {porcentaje}%."
            )
        rebaja = monto * (porcentaje / 100.0)
        return max(0.0, monto - rebaja)


class Producto:
    """
    Clase base abstracta/conceptual que define el contrato general de los productos
    en el catálogo comercial. Encapsula nombre, precio base y stock disponible.
    """

    def __init__(self, nombre: str, precio_base: float, stock: int) -> None:
        """
        Inicializa un producto validando todos sus campos mediante sus respectivos setters.
        """
        self._nombre: str = ""
        self._precio_base: float = 0.0
        self._stock: int = 0

        # Asignación controlada a través de propiedades con validación
        self.nombre = nombre
        self.precio_base = precio_base
        self.stock = stock

    # --- Propiedad: nombre ---
    @property
    def nombre(self) -> str:
        """Obtiene el nombre comercial del producto."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValidationError("El nombre del producto no puede estar vacío ni contener solo espacios.")
        self._nombre = valor.strip()

    # --- Propiedad: precio_base ---
    @property
    def precio_base(self) -> float:
        """Obtiene el precio base de lista del producto."""
        return self._precio_base

    @precio_base.setter
    def precio_base(self, valor: float) -> None:
        try:
            num = float(valor)
        except (ValueError, TypeError):
            raise ValidationError("El precio base debe ser un valor numérico.")

        if num <= 0.0:
            raise ValidationError(f"El precio base debe ser estrictamente mayor a 0. Recibido: {num}.")
        self._precio_base = round(num, 2)

    # --- Propiedad: stock ---
    @property
    def stock(self) -> int:
        """Obtiene la cantidad física en existencia."""
        return self._stock

    @stock.setter
    def stock(self, valor: int) -> None:
        try:
            cantidad = int(valor)
        except (ValueError, TypeError):
            raise ValidationError("El stock debe ser un número entero.")

        if cantidad < 0:
            raise ValidationError(f"El stock no puede ser un valor negativo. Recibido: {cantidad}.")
        self._stock = cantidad

    def calcular_precio_final(self) -> float:
        """
        Calcula el precio final de venta. Las subclases deben proveer su propia
        implementación según su régimen tributario y políticas de descuento.
        """
        raise NotImplementedError("Subclases deben implementar este método de cálculo.")

    def __str__(self) -> str:
        """Representación uniforme y legible del producto."""
        return (
            f"[{self.__class__.__name__}] {self.nombre} | "
            f"S/ {self.precio_base:.2f} | Stock: {self.stock}"
        )

    def __del__(self) -> None:
        """Destructor de instancia para trazas de limpieza de memoria."""
        try:
            print(f"🗑️  Destruyendo instancia: {self.nombre}")
        except Exception:
            pass


class Electronico(Producto, DescuentoMixin):
    """
    Representa un dispositivo o accesorio tecnológico.
    Políticas comerciales:
      - Aplica IGV estándar del 18%.
      - Si el stock supera las 50 unidades, se otorga un 10% de descuento por volumen sobre el subtotal.
      - Incluye período de garantía en meses.
    """

    TASA_IGV: float = 0.18
    DESCUENTO_ALTO_STOCK: float = 10.0  # 10% si stock > 50
    UMBRAL_STOCK_DESCUENTO: int = 50

    def __init__(
        self,
        nombre: str,
        precio_base: float,
        stock: int,
        garantia_meses: int,
    ) -> None:
        # Llamada al constructor de la clase base mediante super()
        super().__init__(nombre=nombre, precio_base=precio_base, stock=stock)
        self._garantia_meses: int = 0
        self.garantia_meses = garantia_meses

    @property
    def garantia_meses(self) -> int:
        """Meses de garantía técnica ofrecida."""
        return self._garantia_meses

    @garantia_meses.setter
    def garantia_meses(self, valor: int) -> None:
        try:
            meses = int(valor)
        except (ValueError, TypeError):
            raise ValidationError("La garantía en meses debe ser un valor entero.")

        if meses < 0:
            raise ValidationError(f"La garantía no puede ser negativa. Recibido: {meses} meses.")
        self._garantia_meses = meses

    @override
    def calcular_precio_final(self) -> float:
        """
        Calcula el precio final para electrónicos:
        1. Si stock > 50, se deduce el 10% de descuento comercial utilizando el Mixin.
        2. Se aplica el 18% de IGV sobre el monto resultante.
        """
        subtotal = self.precio_base

        if self.stock > self.UMBRAL_STOCK_DESCUENTO:
            subtotal = self.aplicar_descuento_porcentual(subtotal, self.DESCUENTO_ALTO_STOCK)

        total_con_igv = subtotal * (1.0 + self.TASA_IGV)
        return round(total_con_igv, 2)

    @override
    def __str__(self) -> str:
        base_repr = super().__str__()
        descuento_badge = " (Descuento por stock > 50 aplicable)" if self.stock > self.UMBRAL_STOCK_DESCUENTO else ""
        return f"{base_repr} | Garantía: {self.garantia_meses} meses{descuento_badge}"


class Libro(Producto, DescuentoMixin):
    """
    Representa un libro físico o digital (literatura técnica, académica o de ficción).
    Políticas comerciales:
      - Exonerado de IGV (fomento cultural a la lectura).
      - Si es clasificado como libro educativo o de texto, recibe un 10% de descuento directo.
      - Almacena el autor de la obra como atributo protegido.
    """

    DESCUENTO_EDUCATIVO: float = 10.0  # 10% si es libro de texto/educativo

    def __init__(
        self,
        nombre: str,
        precio_base: float,
        stock: int,
        autor: str,
        es_educativo: bool = False,
    ) -> None:
        super().__init__(nombre=nombre, precio_base=precio_base, stock=stock)
        self._autor: str = ""
        self._es_educativo: bool = bool(es_educativo)
        self.autor = autor

    @property
    def autor(self) -> str:
        """Nombre o seudónimo del autor de la publicación."""
        return self._autor

    @autor.setter
    def autor(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValidationError("El autor del libro no puede estar vacío.")
        self._autor = valor.strip()

    @property
    def es_educativo(self) -> bool:
        """Indica si el libro califica como obra educativa o de texto."""
        return self._es_educativo

    @es_educativo.setter
    def es_educativo(self, valor: bool) -> None:
        self._es_educativo = bool(valor)

    @override
    def calcular_precio_final(self) -> float:
        """
        Calcula el precio final para libros:
        1. Si es educativo, descuenta 10% mediante DescuentoMixin.
        2. Tasa de IGV 0% (exoneración fiscal legal).
        """
        monto = self.precio_base
        if self.es_educativo:
            monto = self.aplicar_descuento_porcentual(monto, self.DESCUENTO_EDUCATIVO)

        return round(monto, 2)

    @override
    def __str__(self) -> str:
        base_repr = super().__str__()
        tipo_libro = "Educativo / Técnico" if self.es_educativo else "General"
        return f"{base_repr} | Autor: {self.autor} | Tipo: {tipo_libro} (Exento IGV)"

