import pygame

from core.widgets.base_widget import BaseWidget
from core.widgets.hover_button import HoverButton
from core.widgets.spotify_controller import SpotifyController


class SpotifyWidget(BaseWidget):
    """Widget de Spotify — pantalla completa con botones hover."""

    def __init__(self):
        self.font_track = pygame.font.SysFont("Consolas", 28, bold=True)
        self.font_artist = pygame.font.SysFont("Consolas", 22)
        self.font_icon = pygame.font.SysFont("Consolas", 48, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 14)

        self.controller = SpotifyController()

        if not self.controller.auth.is_authenticated():
            self.controller.ensure_authenticated()

        self.controller.start_background_updates()

        # Botones (posiciones se calculan en draw)
        self.btn_prev = HoverButton(
            0, 0, 40, "<<",
            on_trigger=self.controller.previous_track,
            font_size=36,
        )
        self.btn_play = HoverButton(
            0, 0, 50, ">",
            on_trigger=self.controller.play_pause,
            font_size=36,
        )
        self.btn_next = HoverButton(
            0, 0, 40, ">>",
            on_trigger=self.controller.next_track,
            font_size=36,
        )

        self._buttons = [self.btn_prev, self.btn_play, self.btn_next]

        self.color_primary = (173, 216, 230)

    def update(self):
        pass

    def update_hover(self, finger_x, finger_y):
        """Actualiza hover sobre botones."""
        for btn in self._buttons:
            btn.update(finger_x, finger_y)

    def clear_hover(self):
        for btn in self._buttons:
            btn.clear()

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

        # Posicionar y dibujar botones
        btn_y = cy + 120
        btn_spacing = 140

        self.btn_prev.set_position(cx - btn_spacing, btn_y)
        self.btn_play.set_position(cx, btn_y)
        self.btn_next.set_position(cx + btn_spacing, btn_y)

        # Actualizar label del botón play según estado
        self.btn_play.label = icon

        for btn in self._buttons:
            btn.draw(screen)

    def stop(self):
        self.controller.stop()
