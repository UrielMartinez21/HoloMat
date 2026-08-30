import math
import pygame


class Renderer:
    """Renderizado estilo HoloMat: fondo negro, HUD azul claro."""

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

        # Colores
        self.color_primary = (173, 216, 230)
        self.color_hover = (200, 255, 255)
        self.color_bg = (20, 20, 40)
        self.color_black = (0, 0, 0)

        # Fuentes
        self.font_title = pygame.font.SysFont("Consolas", 22, bold=True)
        self.font_status = pygame.font.SysFont("Consolas", 18)
        self.font_small = pygame.font.SysFont("Consolas", 14)

        self.status_text = ""

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
        self.screen.fill(self.color_black)

    def draw_cursor(self, x, y):
        """Dibuja el cursor del dedo índice."""
        pygame.draw.circle(self.screen, self.color_primary, (x, y), 15, 3)
        pygame.draw.circle(self.screen, self.color_primary, (x, y), 3)

    def draw_status(self):
        """Status en la esquina inferior izquierda."""
        if self.status_text:
            surface = self.font_status.render(
                self.status_text, True, self.color_primary
            )
            self.screen.blit(surface, (30, self.height - 40))

    def draw_home_button(self, rect, is_hovered=False):
        """Botón circular Home para regresar."""
        center = rect.center
        radius = rect.width // 2
        color = self.color_hover if is_hovered else self.color_primary

        bg = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(bg, (20, 20, 40, 180), (radius, radius), radius)
        self.screen.blit(bg, (center[0] - radius, center[1] - radius))

        pygame.draw.circle(self.screen, color, center, radius, 3)

        text = self.font_small.render("Home", True, color)
        text_rect = text.get_rect(center=center)
        self.screen.blit(text, text_rect)

    def draw_home_button_progress(self, rect, progress):
        """Dibuja arco de progreso alrededor del botón Home."""
        if progress <= 0.05:
            return

        center = rect.center
        radius = rect.width // 2 + 6

        arc_rect = pygame.Rect(
            center[0] - radius, center[1] - radius,
            radius * 2, radius * 2
        )

        start = math.pi / 2
        end = start + (2 * math.pi * progress)
        color = (100, 255, 100) if progress >= 0.9 else self.color_hover

        pygame.draw.arc(self.screen, color, arc_rect, start, end, 3)

    def flip(self):
        """Actualiza pantalla."""
        self.draw_status()
        pygame.display.flip()
        self.clock.tick(self.fps)

    def quit(self):
        pygame.quit()
