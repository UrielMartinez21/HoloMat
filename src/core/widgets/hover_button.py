"""Botón circular reutilizable con hover-to-activate."""

import math
import time

import pygame


class HoverButton:
    """Botón circular que se activa manteniendo el dedo sobre él.

    Uso:
        btn = HoverButton(cx, cy, radius, "PLAY", on_trigger=my_callback)
        btn.update(finger_x, finger_y)  # cada frame con dedo
        btn.draw(screen)                # renderizar
        btn.clear()                     # cuando no hay dedo

    El botón maneja internamente:
        - Detección de hover (circular)
        - Timer con delay configurable
        - Arco de progreso visual
        - Cambio de color al hover
        - Callback al activarse
    """

    # Colores compartidos (estilo HoloMat)
    COLOR_PRIMARY = (173, 216, 230)
    COLOR_HOVER = (200, 255, 255)
    COLOR_SELECTED = (100, 255, 100)
    COLOR_BG = (20, 20, 40, 160)

    def __init__(
        self,
        cx,
        cy,
        radius,
        label,
        on_trigger=None,
        delay=0.8,
        font_size=24,
    ):
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.label = label
        self.on_trigger = on_trigger
        self.delay = delay

        self._font = pygame.font.SysFont("Consolas", font_size, bold=True)

        # Estado interno
        self._hovered = False
        self._hover_start = 0
        self._triggered = False

    @property
    def rect(self):
        """Rect del botón (para compatibilidad)."""
        return pygame.Rect(
            self.cx - self.radius, self.cy - self.radius,
            self.radius * 2, self.radius * 2,
        )

    @property
    def hovered(self):
        return self._hovered

    @property
    def triggered(self):
        return self._triggered

    @property
    def progress(self):
        """Progreso del hover (0.0 a 1.0)."""
        if not self._hovered or self._triggered or self._hover_start == 0:
            return 0.0
        elapsed = time.time() - self._hover_start
        return min(elapsed / self.delay, 1.0)

    def set_position(self, cx, cy):
        """Actualiza posición del botón (para layouts dinámicos)."""
        self.cx = cx
        self.cy = cy

    def contains(self, px, py):
        """Verifica si un punto está dentro del círculo."""
        dx = px - self.cx
        dy = py - self.cy
        return math.sqrt(dx * dx + dy * dy) <= self.radius

    def update(self, finger_x, finger_y):
        """Actualiza hover con la posición del dedo.

        Retorna True si se activó el botón en este frame.
        """
        was_hovered = self._hovered
        self._hovered = self.contains(finger_x, finger_y)

        # Empezó a hacer hover
        if self._hovered and not was_hovered:
            self._hover_start = time.time()
            self._triggered = False
            return False

        # Dejó de hacer hover
        if not self._hovered:
            self._hover_start = 0
            self._triggered = False
            return False

        # Ya se activó, no repetir
        if self._triggered:
            return False

        # Verificar si completó el delay
        elapsed = time.time() - self._hover_start

        if elapsed >= self.delay:
            self._triggered = True

            if self.on_trigger:
                self.on_trigger()

            return True

        return False

    def clear(self):
        """Resetea estado de hover."""
        self._hovered = False
        self._hover_start = 0
        self._triggered = False

    def draw(self, screen, color_override=None):
        """Dibuja el botón con fondo, borde, texto y arco de progreso."""
        center = (self.cx, self.cy)
        color = color_override or (self.COLOR_HOVER if self._hovered else self.COLOR_PRIMARY)

        # Fondo semitransparente
        bg = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(bg, self.COLOR_BG, (self.radius, self.radius), self.radius)
        screen.blit(bg, (self.cx - self.radius, self.cy - self.radius))

        # Borde
        pygame.draw.circle(screen, color, center, self.radius, 3)

        # Texto
        surface = self._font.render(self.label, True, color)
        text_rect = surface.get_rect(center=center)
        screen.blit(surface, text_rect)

        # Arco de progreso
        p = self.progress
        if p > 0.05:
            arc_radius = self.radius + 6
            arc_rect = pygame.Rect(
                self.cx - arc_radius, self.cy - arc_radius,
                arc_radius * 2, arc_radius * 2,
            )
            start = math.pi / 2
            end = start + (2 * math.pi * p)
            arc_color = self.COLOR_SELECTED if p >= 0.9 else self.COLOR_HOVER
            pygame.draw.arc(screen, arc_color, arc_rect, start, end, 3)
