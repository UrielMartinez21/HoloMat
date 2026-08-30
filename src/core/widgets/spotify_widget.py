import math
import time
import pygame
from core.widgets.spotify_controller import SpotifyController


class SpotifyWidget:
    """Widget de Spotify — pantalla completa con botones hover."""

    def __init__(self):
        self.font_track = pygame.font.SysFont("Consolas", 28, bold=True)
        self.font_artist = pygame.font.SysFont("Consolas", 22)
        self.font_icon = pygame.font.SysFont("Consolas", 48, bold=True)
        self.font_btn = pygame.font.SysFont("Consolas", 36, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 14)

        self.controller = SpotifyController()

        if not self.controller.auth.is_authenticated():
            self.controller.ensure_authenticated()

        self.controller.start_background_updates()

        # Botones (se calculan en draw)
        self.btn_prev = pygame.Rect(0, 0, 80, 80)
        self.btn_play = pygame.Rect(0, 0, 100, 100)
        self.btn_next = pygame.Rect(0, 0, 80, 80)

        # Hover-to-click por botón
        self.hovered_btn = None
        self.hover_start = 0
        self.hover_delay = 0.8
        self.hover_triggered = False

        self.color_primary = (173, 216, 230)
        self.color_hover = (200, 255, 255)
        self.color_selected = (100, 255, 100)

    def update(self):
        pass

    def update_hover(self, finger_x, finger_y):
        """Actualiza hover sobre botones. Retorna True si se activó una acción."""
        current_btn = None

        if self.btn_play.collidepoint(finger_x, finger_y):
            current_btn = "play"
        elif self.btn_prev.collidepoint(finger_x, finger_y):
            current_btn = "prev"
        elif self.btn_next.collidepoint(finger_x, finger_y):
            current_btn = "next"

        if current_btn != self.hovered_btn:
            self.hovered_btn = current_btn
            self.hover_start = time.time() if current_btn else 0
            self.hover_triggered = False
            return False

        if current_btn is None or self.hover_triggered:
            return False

        elapsed = time.time() - self.hover_start

        if elapsed >= self.hover_delay:
            self.hover_triggered = True

            if current_btn == "play":
                self.controller.play_pause()
            elif current_btn == "prev":
                self.controller.previous_track()
            elif current_btn == "next":
                self.controller.next_track()

            return True

        return False

    def clear_hover(self):
        self.hovered_btn = None
        self.hover_start = 0
        self.hover_triggered = False

    def _get_hover_progress(self, btn_name):
        """Progreso del hover para un botón específico."""
        if self.hovered_btn != btn_name or self.hover_triggered:
            return 0.0
        if self.hover_start == 0:
            return 0.0
        elapsed = time.time() - self.hover_start
        return min(elapsed / self.hover_delay, 1.0)

    def draw(self, screen, width, height, color):
        """Dibuja el widget de Spotify centrado."""
        cx = width // 2
        cy = height // 2

        # Icono play/pause
        if self.controller.is_playing:
            icon = "||"
        else:
            icon = ">"

        icon_surface = self.font_icon.render(icon, True, color)
        icon_rect = icon_surface.get_rect(centerx=cx, centery=cy - 60)
        screen.blit(icon_surface, icon_rect)

        # Track
        track = self.controller.track_name or "---"
        if len(track) > 35:
            track = track[:33] + ".."

        surface = self.font_track.render(track, True, color)
        rect = surface.get_rect(centerx=cx, centery=cy)
        screen.blit(surface, rect)

        # Artista
        artist = self.controller.artist_name or ""
        if len(artist) > 40:
            artist = artist[:38] + ".."

        if artist:
            surface = self.font_artist.render(artist, True, color)
            rect = surface.get_rect(centerx=cx, centery=cy + 35)
            screen.blit(surface, rect)

        # Barra de progreso
        if self.controller.duration_ms > 0:
            bar_w = 400
            bar_x = cx - bar_w // 2
            bar_y = cy + 70

            progress = self.controller.progress_ms / self.controller.duration_ms
            filled_w = int(bar_w * progress)

            pygame.draw.line(screen, (60, 60, 80), (bar_x, bar_y), (bar_x + bar_w, bar_y), 3)
            if filled_w > 0:
                pygame.draw.line(screen, color, (bar_x, bar_y), (bar_x + filled_w, bar_y), 3)

        # Botones de control
        btn_y = cy + 120
        btn_spacing = 140

        self.btn_prev = pygame.Rect(cx - btn_spacing - 40, btn_y - 40, 80, 80)
        self.btn_play = pygame.Rect(cx - 50, btn_y - 50, 100, 100)
        self.btn_next = pygame.Rect(cx + btn_spacing - 40, btn_y - 40, 80, 80)

        self._draw_btn(screen, self.btn_prev, "<<", "prev")
        self._draw_btn(screen, self.btn_play, icon, "play")
        self._draw_btn(screen, self.btn_next, ">>", "next")

    def _draw_btn(self, screen, rect, text, btn_name):
        """Dibuja un botón circular con progreso de hover."""
        center = rect.center
        radius = rect.width // 2

        is_hovered = (self.hovered_btn == btn_name)
        color = self.color_hover if is_hovered else self.color_primary

        # Fondo
        bg = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(bg, (20, 20, 40, 160), (radius, radius), radius)
        screen.blit(bg, (center[0] - radius, center[1] - radius))

        # Borde
        pygame.draw.circle(screen, color, center, radius, 3)

        # Texto
        surface = self.font_btn.render(text, True, color)
        text_rect = surface.get_rect(center=center)
        screen.blit(surface, text_rect)

        # Arco de progreso
        progress = self._get_hover_progress(btn_name)
        if progress > 0.05:
            arc_radius = radius + 6
            arc_rect = pygame.Rect(
                center[0] - arc_radius, center[1] - arc_radius,
                arc_radius * 2, arc_radius * 2
            )
            start = math.pi / 2
            end = start + (2 * math.pi * progress)
            arc_color = self.color_selected if progress >= 0.9 else self.color_hover
            pygame.draw.arc(screen, arc_color, arc_rect, start, end, 3)

    def stop(self):
        self.controller.stop()
