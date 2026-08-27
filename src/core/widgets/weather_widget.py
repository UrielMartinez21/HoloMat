import time
import pygame


class WeatherWidget:
    """
    Widget de clima para la ventana WEATHER.
    Muestra hora, fecha y estructura lista para
    conectar OpenWeatherMap cuando tengas API key.
    """

    def __init__(self):
        self.font_time = pygame.font.SysFont("Consolas", 36, bold=True)
        self.font_date = pygame.font.SysFont("Consolas", 16)
        self.font_temp = pygame.font.SysFont("Consolas", 28, bold=True)
        self.font_desc = pygame.font.SysFont("Consolas", 14)

        # Datos del clima (placeholder hasta tener API)
        self.temperature = None
        self.description = None
        self.humidity = None
        self.city = None

    def update(self):
        """Actualizar datos. Aquí se conectará la API."""
        pass

    def draw(self, screen, x, y, w, h, color):
        """Dibuja el contenido del widget dentro de la ventana."""
        content_y = y + 60
        center_x = x + w // 2

        # Hora actual
        current_time = time.strftime("%H:%M:%S")
        time_surface = self.font_time.render(current_time, True, color)
        time_rect = time_surface.get_rect(centerx=center_x, top=content_y + 5)
        screen.blit(time_surface, time_rect)

        # Fecha
        current_date = time.strftime("%a %d %b %Y")
        date_surface = self.font_date.render(current_date, True, color)
        date_rect = date_surface.get_rect(centerx=center_x, top=content_y + 50)
        screen.blit(date_surface, date_rect)

        # Si hay datos de clima, mostrarlos debajo
        if self.temperature is not None:
            temp_text = f"{self.temperature}°C"
            temp_surface = self.font_temp.render(temp_text, True, color)
            temp_rect = temp_surface.get_rect(centerx=center_x, top=content_y + 75)
            screen.blit(temp_surface, temp_rect)

            if self.description:
                desc_surface = self.font_desc.render(
                    self.description.capitalize(), True, color
                )
                desc_rect = desc_surface.get_rect(centerx=center_x, top=content_y + 110)
                screen.blit(desc_surface, desc_rect)
