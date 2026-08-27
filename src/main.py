import cv2
import numpy as np

from core.hand_tracker import HandTracker
from core.gesture_detector import GestureDetector
from core.draggable_object import DraggableObject
from core.window_manager import WindowManager
from core.renderer import Renderer
from core.widgets.weather_widget import WeatherWidget


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
        pinch_threshold=0.08,
        pinch_release_threshold=0.10,
        pinch_drag_release_threshold=0.13,
        click_max_duration=0.30,
        drag_threshold=12,
        hold_duration=0.60
    )

    window_manager = WindowManager()
    renderer = Renderer(width, height)

    # Widgets
    weather_widget = WeatherWidget()
    renderer.register_widget("WEATHER", weather_widget)

    window_manager.add_window(
        DraggableObject(
            x=100,
            y=150,
            width=250,
            height=150,
            name="WEATHER",
            smoothing=0.25
        )
    )

    window_manager.add_window(
        DraggableObject(
            x=400,
            y=200,
            width=250,
            height=150,
            name="SPOTIFY",
            smoothing=0.25
        )
    )

    window_manager.add_window(
        DraggableObject(
            x=250,
            y=400,
            width=250,
            height=150,
            name="JARVIS",
            smoothing=0.25
        )
    )

    frame_shape = (height, width, 3)
    running = True

    try:
        while running:
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

            # Actualizar widgets
            weather_widget.update()

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]

                x, y = tracker.get_index_tip(
                    hand_landmarks,
                    frame_shape
                )

                hovered_window = window_manager.update_hover(x, y)

                event = gesture_detector.update_interaction(
                    hand_landmarks,
                    x,
                    y
                )

                is_pinching = gesture_detector.previous_pinch

                result_text = window_manager.handle_event(
                    event,
                    x,
                    y,
                    gesture_detector,
                    hand_landmarks
                )

                if result_text:
                    renderer.interaction_text = result_text

                # Puntos en índice y pulgar
                renderer.draw_finger_points(
                    hand_landmarks,
                    frame_shape,
                    is_pinching=is_pinching,
                    is_hovering=(hovered_window is not None)
                )

            else:
                window_manager.clear_hover()

            # Renderizar
            renderer.render(
                window_manager.windows,
                window_manager.active_window
            )

    finally:
        tracker.close()
        cap.release()
        renderer.quit()


if __name__ == "__main__":
    main()
