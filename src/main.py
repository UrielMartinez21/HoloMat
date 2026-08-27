import cv2

from core.hand_tracker import HandTracker
from core.gesture_detector import GestureDetector
from core.draggable_object import DraggableObject
from core.window_manager import WindowManager


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("No se pudo abrir la cámara.")

    tracker = HandTracker()

    gesture_detector = GestureDetector(
        pinch_threshold=0.06,
        click_max_duration=0.30,
        drag_threshold=20,
        hold_duration=0.60
    )

    window_manager = WindowManager()

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

    interaction_text = "Sin gesto"

    try:
        while True:
            success, frame = cap.read()

            if not success:
                break

            frame = cv2.flip(frame, 1)

            results = tracker.process(frame)

            interaction_text = "Sin gesto"

            if results.multi_hand_landmarks:

                hand_landmarks = results.multi_hand_landmarks[0]

                x, y = tracker.get_index_tip(
                    hand_landmarks,
                    frame.shape
                )

                hovered_window = window_manager.update_hover(
                    x,
                    y
                )

                event = gesture_detector.update_interaction(
                    hand_landmarks,
                    x,
                    y
                )

                # -------------------------
                # CLICK
                # -------------------------

                if event == "CLICK":

                    clicked_window = window_manager.get_window_at(
                        x,
                        y
                    )

                    if clicked_window:
                        interaction_text = (
                            f"CLICK: {clicked_window.name}"
                        )

                        print(
                            f"CLICK en {clicked_window.name}"
                        )
                    else:
                        interaction_text = "CLICK"

                # -------------------------
                # HOLD
                # -------------------------

                elif event == "HOLD":

                    held_window = window_manager.get_window_at(
                        x,
                        y
                    )

                    if held_window:
                        interaction_text = (
                            f"HOLD: {held_window.name}"
                        )
                    else:
                        interaction_text = "HOLD"

                # -------------------------
                # DRAG
                # -------------------------

                elif event == "DRAG":

                    if window_manager.active_window is None:

                        window_manager.start_drag(
                            x,
                            y
                        )

                    window_manager.drag(
                        x,
                        y
                    )

                    interaction_text = "DRAG"

                elif event == "DRAG_END":

                    window_manager.stop_drag()

                    interaction_text = "DRAG END"

                elif event == "PINCH_START":

                    interaction_text = "PINCH START"

                elif event == "PINCH_HOLD":

                    interaction_text = "PINCH HOLD"

                elif event == "PINCH_END":

                    interaction_text = "PINCH END"

                elif gesture_detector.is_fist(
                    hand_landmarks
                ):
                    interaction_text = "PUNO"

                elif gesture_detector.is_hand_open(
                    hand_landmarks
                ):
                    interaction_text = "MANO ABIERTA"

                # -------------------------
                # Cursor
                # -------------------------

                circle_radius = 10

                if hovered_window:
                    circle_radius = 18

                if window_manager.active_window:
                    circle_radius = 25

                cv2.circle(
                    frame,
                    (x, y),
                    circle_radius,
                    (0, 0, 255),
                    cv2.FILLED
                )

                cv2.putText(
                    frame,
                    f"Index: ({x}, {y})",
                    (x + 15, y - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

            else:

                for window in window_manager.windows:
                    window.hovering = False

            # -------------------------
            # Dibujar ventanas
            # -------------------------

            for window in window_manager.windows:

                if window.dragging:
                    thickness = 6

                elif window.hovering:
                    thickness = 4

                else:
                    thickness = 2

                cv2.rectangle(
                    frame,
                    (window.x, window.y),
                    (
                        window.x + window.width,
                        window.y + window.height
                    ),
                    (255, 255, 255),
                    thickness
                )

                cv2.putText(
                    frame,
                    window.name,
                    (
                        window.x + 20,
                        window.y + 40
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2
                )

            # -------------------------
            # Estado
            # -------------------------

            cv2.putText(
                frame,
                interaction_text,
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "HoloMat",
                frame
            )

            if cv2.waitKey(1) & 0xFF == 27:
                break

    finally:
        tracker.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()