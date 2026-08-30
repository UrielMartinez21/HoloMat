"""Widget de monitoreo del sistema — pantalla completa."""

import math
import time
import threading
import pygame
import psutil


class SystemWidget:
    """Muestra CPU, RAM, disco y batería en tiempo real."""

    def __init__(self):
        self.font_label = pygame.font.SysFont("Consolas", 18)
        self.font_value = pygame.font.SysFont("Consolas", 36, bold=True)
        self.font_unit = pygame.font.SysFont("Consolas", 14)
        self.font_detail = pygame.font.SysFont("Consolas", 13)

        # Datos (se actualizan en background)
        self.cpu_percent = 0.0
        self.ram_percent = 0.0
        self.ram_used_gb = 0.0
        self.ram_total_gb = 0.0
        self.disk_percent = 0.0
        self.disk_used_gb = 0.0
        self.disk_total_gb = 0.0
        self.battery_percent = None
        self.battery_charging = False

        # Colores
        self.color_primary = (173, 216, 230)
        self.color_good = (100, 255, 150)
        self.color_warn = (255, 220, 80)
        self.color_bad = (255, 80, 80)
        self.color_dim = (100, 100, 120)
        self.color_bg = (20, 20, 40)

        # Update en background
        self._running = True
        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()

    def _update_loop(self):
        """Actualiza datos cada segundo."""
        while self._running:
            self.cpu_percent = psutil.cpu_percent(interval=1)

            mem = psutil.virtual_memory()
            self.ram_percent = mem.percent
            self.ram_used_gb = mem.used / (1024 ** 3)
            self.ram_total_gb = mem.total / (1024 ** 3)

            disk = psutil.disk_usage("/")
            self.disk_percent = disk.percent
            self.disk_used_gb = disk.used / (1024 ** 3)
            self.disk_total_gb = disk.total / (1024 ** 3)

            bat = psutil.sensors_battery()
            if bat:
                self.battery_percent = bat.percent
                self.battery_charging = bat.power_plugged
            else:
                self.battery_percent = None

    def update(self):
        pass

    def _get_color(self, percent):
        """Retorna color según el porcentaje (verde → amarillo → rojo)."""
        if percent < 50:
            return self.color_good
        elif percent < 80:
            return self.color_warn
        else:
            return self.color_bad

    def draw(self, screen, width, height, color):
        """Dibuja el monitor del sistema."""
        cx = width // 2

        # Layout: 2x2 grid de gauges
        has_battery = self.battery_percent is not None
        gauges = [
            ("CPU", self.cpu_percent, f"{self.cpu_percent:.0f}%", None),
            ("RAM", self.ram_percent, f"{self.ram_percent:.0f}%",
             f"{self.ram_used_gb:.1f} / {self.ram_total_gb:.1f} GB"),
            ("DISCO", self.disk_percent, f"{self.disk_percent:.0f}%",
             f"{self.disk_used_gb:.0f} / {self.disk_total_gb:.0f} GB"),
        ]

        if has_battery:
            charging = "⚡" if self.battery_charging else ""
            gauges.append(
                ("BATERÍA", self.battery_percent,
                 f"{self.battery_percent:.0f}%{charging}", None)
            )

        # Calcular posiciones
        cols = 2
        rows = math.ceil(len(gauges) / cols)
        spacing_x = 280
        spacing_y = 220
        start_x = cx - (spacing_x * (cols - 1)) // 2
        start_y = height // 2 - (spacing_y * (rows - 1)) // 2

        for i, (label, percent, value_text, detail) in enumerate(gauges):
            col = i % cols
            row = i // cols
            gx = start_x + col * spacing_x
            gy = start_y + row * spacing_y

            self._draw_gauge(screen, gx, gy, label, percent, value_text, detail, color)

    def _draw_gauge(self, screen, cx, cy, label, percent, value_text, detail, color):
        """Dibuja un gauge circular."""
        radius = 70
        thickness = 8
        gauge_color = self._get_color(percent)

        # Fondo del arco (gris oscuro)
        rect = pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)
        pygame.draw.arc(
            screen, (40, 40, 50), rect,
            -math.pi * 0.75, math.pi * 0.75,
            thickness
        )

        # Arco de progreso (270 grados máximo, de 225° a -45°)
        total_angle = math.pi * 1.5  # 270 grados
        progress_angle = total_angle * (percent / 100.0)

        start = math.pi * 0.75  # 135 grados (abajo-izquierda)
        end = start + progress_angle

        if progress_angle > 0.05:
            pygame.draw.arc(screen, gauge_color, rect, start, end, thickness)

        # Valor en el centro
        surface = self.font_value.render(value_text, True, gauge_color)
        text_rect = surface.get_rect(centerx=cx, centery=cy - 5)
        screen.blit(surface, text_rect)

        # Label arriba
        surface = self.font_label.render(label, True, color)
        text_rect = surface.get_rect(centerx=cx, centery=cy - radius - 20)
        screen.blit(surface, text_rect)

        # Detalle abajo
        if detail:
            surface = self.font_detail.render(detail, True, self.color_dim)
            text_rect = surface.get_rect(centerx=cx, centery=cy + radius + 15)
            screen.blit(surface, text_rect)

    def stop(self):
        self._running = False
