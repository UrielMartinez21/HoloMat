import pygame
import numpy as np


class Renderer:
    def __init__(self, width=1280, height=720):
        pygame.init()
        self.width = width
        self.height = height

        self.screen = pygame.display.set_mode(
            (width, height),
            pygame.NOFRAME
        )
        pygame.display.set_caption("HoloMat")

        self.clock = pygame.time.Clock()
        self.fps = 30

        self.interaction_text = "Sin gesto"

        # Colores estilo HoloMat
        self.color_primary = (173, 216, 230)     # Azul claro
        self.color_hover = (200, 255, 255)       # Azul más brillante
        self.color_active = (255, 200, 0)        # Naranja/dorado para drag
        self.color_pinch = (255, 100, 0)         # Rojo-naranja para pinch activo
        self.color_click = (100, 255, 100)       # Verde para click
        self.color_text = (173, 216, 230)        # Azul claro
        self.color_bg = (20, 20, 40)             # Navy oscuro
        self.color_black = (0, 0, 0)

        # Fuentes
        self.font_title = pygame.font.SysFont("Consolas", 22, bold=True)
        self.font_status = pygame.font.SysFont("Consolas", 18)
        self.font_small = pygame.font.SysFont("Consolas", 14)

        # Widgets asociados a ventanas
        self.widgets = {}

    def register_widget(self, window_name, widget):
        """Registra un widget para que se dibuje dentro de una ventana."""
        self.widgets[window_name] = widget

    def handle_events(self):
        """Procesa eventos de Pygame. Retorna False si hay que cerrar."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

    def clear(self):
        """Limpia la pantalla con fondo negro."""
        self.screen.fill(self.color_black)

    def draw_finger_points(self, hand_landmarks, frame_shape, is_pinching=False, is_clicking=False, is_hovering=False):
        """Dibuja círculos en índice, pulgar y dedo medio."""
        h, w, _ = frame_shape

        index_tip = hand_landmarks.landmark[8]
        thumb_tip = hand_landmarks.landmark[4]
        middle_tip = hand_landmarks.landmark[12]

        ix = int(index_tip.x * w)
        iy = int(index_tip.y * h)
        tx = int(thumb_tip.x * w)
        ty = int(thumb_tip.y * h)
        mx = int(middle_tip.x * w)
        my = int(middle_tip.y * h)

        # Color del índice (cursor)
        if is_hovering:
            index_color = self.color_hover
        else:
            index_color = self.color_primary

        # Anillo en el índice (siempre como cursor)
        pygame.draw.circle(self.screen, index_color, (ix, iy), 15, 3)
        pygame.draw.circle(self.screen, index_color, (ix, iy), 3)

        # Pulgar: cambia si está en pinch/drag
        if is_pinching:
            thumb_color = self.color_pinch
            thumb_radius = 12
        else:
            thumb_color = self.color_primary
            thumb_radius = 10

        pygame.draw.circle(self.screen, thumb_color, (tx, ty), thumb_radius, 2)
        pygame.draw.circle(self.screen, thumb_color, (tx, ty), 2)

        # Dedo medio: cambia si está en click
        if is_clicking:
            mid_color = self.color_click
            mid_radius = 12
        else:
            mid_color = self.color_primary
            mid_radius = 8

        pygame.draw.circle(self.screen, mid_color, (mx, my), mid_radius, 2)
        pygame.draw.circle(self.screen, mid_color, (mx, my), 2)

    def draw_windows(self, windows, active_window):
        for window in windows:

            x = window.x
            y = window.y
            w = window.width
            h = window.height

            # Determinar estado y color
            if window.dragging:
                color = self.color_active
                thickness = 4
                corner_len = 25
            elif window.hovering:
                color = self.color_hover
                thickness = 3
                corner_len = 22
            else:
                color = self.color_primary
                thickness = 2
                corner_len = 20

            # Fondo semi-transparente
            bg_surface = pygame.Surface((w, h), pygame.SRCALPHA)
            bg_surface.fill((20, 20, 40, 150))
            self.screen.blit(bg_surface, (x, y))

            # Esquinas estilo HUD
            self._draw_corner_brackets(x, y, w, h, color, thickness, corner_len)

            # Borde superior
            pygame.draw.line(
                self.screen, color,
                (x + corner_len, y),
                (x + w - corner_len, y),
                1
            )

            # Línea separadora debajo del título
            line_y = y + 50
            pygame.draw.line(
                self.screen, color,
                (x + 10, line_y),
                (x + w - 10, line_y),
                1
            )

            # Nombre de la ventana
            text_surface = self.font_title.render(window.name, True, color)
            self.screen.blit(text_surface, (x + 15, y + 15))

            # Dibujar widget si existe
            if window.name in self.widgets:
                self.widgets[window.name].draw(
                    self.screen, x, y, w, h, color
                )

    def _draw_corner_brackets(self, x, y, w, h, color, thickness=2, corner_len=20):
        """Esquinas estilo HUD."""
        pygame.draw.line(self.screen, color, (x, y), (x + corner_len, y), thickness)
        pygame.draw.line(self.screen, color, (x, y), (x, y + corner_len), thickness)

        pygame.draw.line(self.screen, color, (x + w, y), (x + w - corner_len, y), thickness)
        pygame.draw.line(self.screen, color, (x + w, y), (x + w, y + corner_len), thickness)

        pygame.draw.line(self.screen, color, (x, y + h), (x + corner_len, y + h), thickness)
        pygame.draw.line(self.screen, color, (x, y + h), (x, y + h - corner_len), thickness)

        pygame.draw.line(self.screen, color, (x + w, y + h), (x + w - corner_len, y + h), thickness)
        pygame.draw.line(self.screen, color, (x + w, y + h), (x + w, y + h - corner_len), thickness)

    def draw_status(self):
        """Status discreto en la esquina inferior izquierda."""
        text_surface = self.font_status.render(
            self.interaction_text, True, self.color_primary
        )
        self.screen.blit(text_surface, (30, self.height - 40))

    def render(self, windows, active_window):
        """Dibuja ventanas y status, luego actualiza pantalla."""
        self.draw_windows(windows, active_window)
        self.draw_status()
        pygame.display.flip()
        self.clock.tick(self.fps)

    def quit(self):
        pygame.quit()
