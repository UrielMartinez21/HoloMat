import math
import time

import cv2
import pygame

from core.hand_tracker import HandTracker
from core.renderer import Renderer
from core.home_menu import HomeMenu
from core.widgets.weather_widget import WeatherWidget
from core.widgets.spotify_widget import SpotifyWidget
from core.widgets.system_widget import SystemWidget


# Estados
STATE_HOME = "HOME"
STATE_APP = "APP"

# Color global
COLOR = (173, 216, 230)


def main():
    width = 1280
    height = 720

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    if not cap.isOpened():
        raise RuntimeError("No se pudo abrir la cámara.")

    tracker = HandTracker()
    renderer = Renderer(width, height)

    # Widgets
    weather_widget = WeatherWidget()
    spotify_widget = SpotifyWidget()
    system_widget = SystemWidget()

    widgets = {
        "WEATHER": weather_widget,
        "SPOTIFY": spotify_widget,
        "SYSTEM": system_widget,
    }

    # Menú Home
    home_menu = HomeMenu(width, height)
    home_menu.setup(["WEATHER", "SPOTIFY", "SYSTEM"])

    # Estado
    state = STATE_HOME
    current_app = None

    # Botón Home dentro de las apps (esquina inferior izquierda)
    home_btn_radius = 40
    home_btn_rect = pygame.Rect(
        30, height - 30 - home_btn_radius * 2,
        home_btn_radius * 2, home_btn_radius * 2
    )
    home_hover_start = 0
    home_hover_delay = 0.8

    frame_shape = (height, width, 3)

    try:
        while True:
            if not renderer.handle_events():
                break

            success, frame = cap.read()
            if not success:
                break

            frame = cv2.flip(frame, 1)
            results = tracker.process(frame)

            renderer.clear()
            renderer.status_text = ""

            # Obtener posición del dedo
            finger_pos = None

            if results.multi_hand_landmarks:
                hand = results.multi_hand_landmarks[0]
                finger_pos = tracker.get_index_pos(hand, frame_shape)

            # --- HOME ---
            if state == STATE_HOME:
                if finger_pos:
                    fx, fy = finger_pos
                    selected = home_menu.update(fx, fy)

                    if selected:
                        state = STATE_APP
                        current_app = selected
                        home_hover_start = 0

                        # Reset hover del widget al entrar
                        w = widgets.get(selected)
                        if w and hasattr(w, 'clear_hover'):
                            w.clear_hover()
                    else:
                        renderer.status_text = "Menú Home"
                else:
                    home_menu.update_no_hand()

                home_menu.draw(renderer.screen)

                if finger_pos:
                    renderer.draw_cursor(*finger_pos)

                renderer.flip()

            # --- APP ---
            elif state == STATE_APP:
                widget = widgets.get(current_app)

                # Actualizar widget
                if widget:
                    widget.update()

                # Hover sobre botón Home
                home_hovered = False
                home_progress = 0.0

                if finger_pos:
                    fx, fy = finger_pos

                    # Distancia al centro del botón Home
                    hx, hy = home_btn_rect.center
                    dist = math.sqrt((fx - hx) ** 2 + (fy - hy) ** 2)
                    home_hovered = dist <= home_btn_radius

                    if home_hovered:
                        if home_hover_start == 0:
                            home_hover_start = time.time()
                        else:
                            elapsed = time.time() - home_hover_start
                            home_progress = min(elapsed / home_hover_delay, 1.0)

                            if elapsed >= home_hover_delay:
                                # Regresar al Home
                                state = STATE_HOME
                                current_app = None
                                home_hover_start = 0

                                # Resetear menú
                                home_menu.apps_visible = False
                                home_menu.last_toggle_time = 0
                                for circle in home_menu.circles[1:]:
                                    circle.visible = False
                                    circle.is_animating = False
                                    circle.animation_start_time = None
                                    circle.cx = float(circle.center_pos[0])
                                    circle.cy = float(circle.center_pos[1])

                                renderer.flip()
                                continue
                    else:
                        home_hover_start = 0

                    # Hover sobre botones del widget (si no está sobre Home)
                    if not home_hovered and widget and hasattr(widget, 'update_hover'):
                        widget.update_hover(fx, fy)
                    elif widget and hasattr(widget, 'clear_hover'):
                        widget.clear_hover()

                else:
                    home_hover_start = 0
                    if widget and hasattr(widget, 'clear_hover'):
                        widget.clear_hover()

                # Dibujar widget
                if widget:
                    widget.draw(renderer.screen, width, height, COLOR)

                # Dibujar botón Home
                renderer.draw_home_button(home_btn_rect, home_hovered)
                if home_progress > 0:
                    renderer.draw_home_button_progress(home_btn_rect, home_progress)

                # Cursor
                if finger_pos:
                    renderer.draw_cursor(*finger_pos)

                renderer.flip()

    finally:
        spotify_widget.stop()
        system_widget.stop()
        tracker.close()
        cap.release()
        renderer.quit()


if __name__ == "__main__":
    main()
