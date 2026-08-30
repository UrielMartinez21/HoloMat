import time
import pygame


class WeatherWidget:
    """Widget de clima / reloj — pantalla completa."""

    def __init__(self):
        self.font_time = pygame.font.SysFont("Consolas", 72, bold=True)
        self.font_date = pygame.font.SysFont("Consolas", 28)
        self.font_temp = pygame.font.SysFont("Consolas", 48, bold=True)
        self.font_desc = pygame.font.SysFont("Consolas", 22)

        self.temperature = None
        self.description = None

    def update(self):
        pass

    def draw(self, screen, width, height, color):
        """Dibuja el widget centrado en la pantalla."""
        cx = width // 2
        cy = height // 2

        # Hora
        current_time = time.strftime("%H:%M:%S")
        surface = self.font_time.render(current_time, True, color)
        rect = surface.get_rect(centerx=cx, centery=cy - 30)
        screen.blit(surface, rect)

        # Fecha
        current_date = time.strftime("%A %d %B %Y")
        surface = self.font_date.render(current_date, True, color)
        rect = surface.get_rect(centerx=cx, centery=cy + 40)
        screen.blit(surface, rect)

        # Clima si hay datos
        if self.temperature is not None:
            temp_text = f"{self.temperature}°C"
            surface = self.font_temp.render(temp_text, True, color)
            rect = surface.get_rect(centerx=cx, centery=cy + 100)
            screen.blit(surface, rect)

            if self.description:
                surface = self.font_desc.render(
                    self.description.capitalize(), True, color
                )
                rect = surface.get_rect(centerx=cx, centery=cy + 150)
                screen.blit(surface, rect)

    def stop(self):
        pass
