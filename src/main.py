import time

import cv2
import pygame

from core.hand_tracker import HandTracker
from core.gesture_detector import GestureDetector
from core.draggable_object import DraggableObject
from core.window_manager import WindowManager
from core.renderer import Renderer
from core.home_menu import HomeMenu
from core.widgets.weather_widget import WeatherWidget
from core.widgets.spotify_widget import SpotifyWidget


# Estados de la aplicación
STATE_HOME = "HOME"
STATE_APP = "APP"


class AppState:
    """Estado global de la aplicación."""

    def __init__(self, width, height):
        self.state = STATE_HOME
        self.current_app = None
        self.window_manager = None

        # Botón de regreso
        self.back_button_rect = pygame.Rect(20, 15, 90, 35)
        self.back_hovered = False
        self.back_hover_start = 0
        self.back_hover_delay = 0.8

    def enter_app(self, app_name, widgets):
        """Transición al modo app."""
        self.state = STATE_APP
        self.current_app = app_name

        self.window_manager = WindowManager()

        # Registrar acciones de click
        if "SPOTIFY" in widgets and app_name == "SPOTIFY":
            self.window_manager.register_click_action(
                "SPOTIFY", widgets["SPOTIFY"].on_click
            )

        # Crear ventanas de la app
        for win in self._create_windows(app_name):
            self.window_manager.add_window(win)

    def enter_home(self, home_menu):
        """Transición al menú Home."""
        self.state = STATE_HOME
        self.current_app = None
        self.window_manager = None
        self.back_hovered = False
        self.back_hover_start = 0

        # Resetear menú
        home_menu.apps_visible = False
        home_menu.last_toggle_time = 0

        for circle in home_menu.circles[1:]:
            circle.visible = False
            circle.is_animating = False
            circle.animation_start_time = None
            circle.cx = float(circle.center_pos[0])
            circle.cy = float(circle.center_pos[1])

    def _create_windows(self, app_name):
        """Crea las ventanas para una app específica."""
        return [
            DraggableObject(
                x=515, y=200,
                width=250, height=150,
                name=app_name, smoothing=0.25
            )
        ]


def main():
    # Resolución de la interfaz
    width = 1280
    height = 720

    # Cámara (solo para detección)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    if not cap.isOpened():
        raise RuntimeError("No se pudo abrir la cámara.")

    tracker = HandTracker()

    gesture_detector = GestureDetector(
        pinch_threshold=0.09,
        pinch_release_threshold=0.11,
        pinch_drag_release_threshold=0.14,
        click_threshold=0.06,
        click_release_threshold=0.08,
        click_max_duration=0.40,
        drag_threshold=12,
        hold_duration=0.60
    )

    renderer = Renderer(width, height)

    # Widgets
    weather_widget = WeatherWidget()
    spotify_widget = SpotifyWidget()

    widgets = {
        "WEATHER": weather_widget,
        "SPOTIFY": spotify_widget,
    }

    renderer.register_widget("WEATHER", weather_widget)
    renderer.register_widget("SPOTIFY", spotify_widget)

    # Menú Home
    home_menu = HomeMenu(width, height)
    app_names = ["WEATHER", "SPOTIFY", "JARVIS"]
    home_menu.setup(app_names)

    # Estado
    app_state = AppState(width, height)

    frame_shape = (height, width, 3)

    try:
        while True:
            # Eventos de Pygame
            if not renderer.handle_events():
                break

            # Capturar frame para detección
            success, frame = cap.read()
            if not success:
                break

            frame = cv2.flip(frame, 1)

            # Detectar mano
            results = tracker.process(frame, draw=False)

            # Limpiar pantalla
            renderer.clear()
            renderer.interaction_text = "Sin gesto"

            # Actualizar widgets siempre
            weather_widget.update()
            spotify_widget.update()

            if app_state.state == STATE_HOME:
                run_home(
                    results, tracker, frame_shape,
                    renderer, home_menu, app_state, widgets
                )

            elif app_state.state == STATE_APP:
                run_app(
                    results, tracker, frame_shape,
                    renderer, gesture_detector,
                    app_state, home_menu
                )

    finally:
        spotify_widget.stop()
        tracker.close()
        cap.release()
        renderer.quit()


def run_home(results, tracker, frame_shape, renderer, home_menu, app_state, widgets):
    """Ejecuta un frame del menú Home."""
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        x, y = tracker.get_index_tip(hand_landmarks, frame_shape)

        # Actualizar menú (hover con timer → selecciona)
        selected = home_menu.update(x, y)

        if selected:
            app_state.enter_app(selected, widgets)
            return

        renderer.draw_cursor_only(hand_landmarks, frame_shape)
        renderer.interaction_text = "Menú Home"
    else:
        home_menu.update_no_hand()

    renderer.render_home(home_menu)


def run_app(results, tracker, frame_shape, renderer, gesture_detector, app_state, home_menu):
    """Ejecuta un frame de una app con ventanas arrastrables."""
    wm = app_state.window_manager

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        x, y = tracker.get_index_tip(hand_landmarks, frame_shape)

        # Hover sobre botón de regreso (mismo patrón: mantener dedo → volver)
        if app_state.back_button_rect.collidepoint(x, y):
            if not app_state.back_hovered:
                app_state.back_hovered = True
                app_state.back_hover_start = time.time()
            else:
                elapsed = time.time() - app_state.back_hover_start
                if elapsed >= app_state.back_hover_delay:
                    app_state.enter_home(home_menu)
                    return
        else:
            app_state.back_hovered = False
            app_state.back_hover_start = 0

        hovered_window = wm.update_hover(x, y)

        event = gesture_detector.update_interaction(
            hand_landmarks, x, y
        )

        is_pinching = gesture_detector.previous_pinch
        is_clicking = gesture_detector.previous_click_gesture

        result_text = wm.handle_event(
            event, x, y, gesture_detector, hand_landmarks
        )

        if result_text:
            renderer.interaction_text = result_text

        renderer.draw_finger_points(
            hand_landmarks, frame_shape,
            is_pinching=is_pinching,
            is_clicking=is_clicking,
            is_hovering=(hovered_window is not None)
        )

    else:
        wm.clear_hover()
        app_state.back_hovered = False
        app_state.back_hover_start = 0

    renderer.render_app(
        wm.windows,
        wm.active_window,
        app_state.current_app,
        app_state.back_button_rect,
        app_state.back_hovered
    )


if __name__ == "__main__":
    main()
