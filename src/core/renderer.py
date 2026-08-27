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
        self.color_text = (173, 216, 230)        # Azul claro
        self.color_bg = (20, 20, 40)             # Navy oscuro
        self.color_black = (0, 0, 0)

        # Fuentes
        self.font_title = pygame.font.SysFont("Consolas", 22, bold=True)
        self.font_status = pygame.font.SysFont("Consolas", 18)
        self.font_small = pygame.font.SysFont("Consolas", 14)

        # Widgets asociados a ventanas (por nombre)
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

    def draw_finger_points(self, hand_landmarks, frame_shape, is_pinching=False, is_hovering=False):
        """Dibuja un círculo en el índice y otro en el pulgar."""
        h, w, _ = frame_shape

        index_tip = hand_landmarks.landmark[8]
        thumb_tip = hand_landmarks.landmark[4]

        ix = int(index_tip.x * w)
        iy = int(index_tip.y * h)
        tx = int(thumb_tip.x * w)
        ty = int(thumb_tip.y * h)

        if is_pinching:
            color = self.color_pinch
            index_radius = 16
            thumb_radius = 12
            thickness = 3
        elif is_hovering:
            color = self.color_hover
            index_radius = 15
            thumb_radius = 10
            thickness = 3
        else:
            color = self.color_primary
            index_radius = 15
            thumb_radius = 10
            thickness = 3

        # Anillo en el índice
        pygame.draw.circle(self.screen, color, (ix, iy), index_radius, thickness)
        pygame.draw.circle(self.screen, color, (ix, iy), 3)

        # Anillo en el pulgar
        pygame.draw.circle(self.screen, color, (tx, ty), thumb_radius, 2)
        pygame.draw.circle(self.screen, color, (tx, ty), 2)

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

            # Borde superior (línea fina entre esquinas)
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

            # Dibujar widget si existe para esta ventana
            if window.name in self.widgets:
                self.widgets[window.name].draw(
                    self.screen, x, y, w, h, color
                )

    def _draw_corner_brackets(self, x, y, w, h, color, thickness=2, corner_len=20):
        """Esquinas estilo HUD."""
        # Superior izquierda
        pygame.draw.line(self.screen, color, (x, y), (x + corner_len, y), thickness)
        pygame.draw.line(self.screen, color, (x, y), (x, y + corner_len), thickness)

        # Superior derecha
        pygame.draw.line(self.screen, color, (x + w, y), (x + w - corner_len, y), thickness)
        pygame.draw.line(self.screen, color, (x + w, y), (x + w, y + corner_len), thickness)

        # Inferior izquierda
        pygame.draw.line(self.screen, color, (x, y + h), (x + corner_len, y + h), thickness)
        pygame.draw.line(self.screen, color, (x, y + h), (x, y + h - corner_len), thickness)

        # Inferior derecha
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
