"""Clase base para todos los widgets de HoloMat."""

from abc import ABC, abstractmethod


class BaseWidget(ABC):
    """Interfaz común para todos los widgets.

    Métodos requeridos:
        update  — lógica por frame (puede ser no-op)
        draw    — renderizar en pantalla

    Métodos opcionales (tienen implementación no-op por defecto):
        update_hover — procesar posición del dedo sobre botones
        clear_hover  — resetear estado de hover
        stop         — cleanup al cerrar la app
    """

    @abstractmethod
    def update(self):
        """Actualiza lógica del widget (llamado cada frame)."""
        ...

    @abstractmethod
    def draw(self, screen, width, height, color):
        """Renderiza el widget en pantalla."""
        ...

    def update_hover(self, finger_x, finger_y):
        """Actualiza hover con la posición del dedo. No-op por defecto."""
        pass

    def clear_hover(self):
        """Resetea todo estado de hover. No-op por defecto."""
        pass

    def stop(self):
        """Cleanup al cerrar. No-op por defecto."""
        pass
