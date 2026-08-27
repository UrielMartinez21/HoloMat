import pygame
from core.widgets.spotify_controller import SpotifyController


class SpotifyWidget:
    """
    Widget de Spotify para la ventana SPOTIFY.
    Muestra canción actual y permite play/pause con click.
    """

    def __init__(self):
        self.font_track = pygame.font.SysFont("Consolas", 16, bold=True)
        self.font_artist = pygame.font.SysFont("Consolas", 14)
        self.font_status = pygame.font.SysFont("Consolas", 12)
        self.font_icon = pygame.font.SysFont("Consolas", 28, bold=True)

        self.controller = SpotifyController()

        # Autenticar si es necesario
        if not self.controller.auth.is_authenticated():
            self.controller.ensure_authenticated()

        # Iniciar actualizaciones en background
        self.controller.start_background_updates()

    def update(self):
        """No-op: el controller se actualiza solo en background."""
        pass

    def on_click(self):
        """Al hacer click en la ventana → play/pause."""
        self.controller.play_pause()

    def draw(self, screen, x, y, w, h, color):
        """Dibuja el contenido del widget."""
        content_y = y + 60
        center_x = x + w // 2

        # Estado de reproducción (icono play/pause)
        if self.controller.is_playing:
            icon = "||"
        else:
            icon = ">"

        icon_surface = self.font_icon.render(icon, True, color)
        icon_rect = icon_surface.get_rect(centerx=center_x, top=content_y)
        screen.blit(icon_surface, icon_rect)

        # Nombre de la canción
        track = self.controller.track_name or "---"
        if len(track) > 22:
            track = track[:20] + ".."

        track_surface = self.font_track.render(track, True, color)
        track_rect = track_surface.get_rect(centerx=center_x, top=content_y + 38)
        screen.blit(track_surface, track_rect)

        # Artista
        artist = self.controller.artist_name or ""
        if len(artist) > 25:
            artist = artist[:23] + ".."

        if artist:
            artist_surface = self.font_artist.render(artist, True, color)
            artist_rect = artist_surface.get_rect(centerx=center_x, top=content_y + 60)
            screen.blit(artist_surface, artist_rect)

        # Barra de progreso
        if self.controller.duration_ms > 0:
            bar_w = w - 40
            bar_x = x + 20
            bar_y = content_y + 82

            progress = self.controller.progress_ms / self.controller.duration_ms
            filled_w = int(bar_w * progress)

            # Fondo de la barra
            pygame.draw.line(screen, (60, 60, 80), (bar_x, bar_y), (bar_x + bar_w, bar_y), 2)
            # Progreso
            if filled_w > 0:
                pygame.draw.line(screen, color, (bar_x, bar_y), (bar_x + filled_w, bar_y), 2)

    def stop(self):
        """Detiene el controller."""
        self.controller.stop()
