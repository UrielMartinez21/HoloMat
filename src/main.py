import cv2
import numpy as np

from core.hand_tracker import HandTracker
from core.gesture_detector import GestureDetector
from core.draggable_object import DraggableObject
from core.window_manager import WindowManager
from core.renderer import Renderer


def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        raise RuntimeError("No se pudo abrir la cámara.")

    # Obtener resolución real de la cámara
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    tracker = HandTracker()

    gesture_detector = GestureDetector(
        pinch_threshold=0.08,
        pinch_release_threshold=0.10,
        click_max_duration=0.30,
        drag_threshold=12,
        hold_duration=0.60
    )

    window_manager = WindowManager()
    renderer = Renderer()

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

    try:
        while True:
            success, frame = cap.read()

            if not success:
                break

            frame = cv2.flip(frame, 1)

            # Procesar mano sobre el frame de cámara
            results = tracker.process(frame, draw=False)

            # Reemplazar con fondo negro
            frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

            renderer.interaction_text = "Sin gesto"
            is_pinching = False

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]

                x, y = tracker.get_index_tip(
                    hand_landmarks,
                    (frame_height, frame_width, 3)
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

                # Feedback de pinch (solo cuando está cerca)
                renderer.draw_pinch_feedback(
                    frame,
                    hand_landmarks,
                    (frame_height, frame_width, 3),
                    gesture_detector.pinch_threshold,
                    gesture_detector.pinch_release_threshold
                )

                # Punto en el índice (estilo Concept Bytes)
                renderer.draw_finger_point(
                    frame,
                    x,
                    y,
                    is_pinching=is_pinching,
                    is_hovering=(hovered_window is not None)
                )

            else:
                window_manager.clear_hover()

            renderer.render(
                frame,
                window_manager.windows,
                window_manager.active_window
            )

            cv2.imshow("HoloMat", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

    finally:
        tracker.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
