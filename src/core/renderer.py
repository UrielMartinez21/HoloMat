import cv2


class Renderer:
    def __init__(self):
        self.interaction_text = "Sin gesto"

    def draw_cursor(self, frame, x, y, radius):
        cv2.circle(
            frame,
            (x, y),
            radius,
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

    def draw_pinch_feedback(self, frame, hand_landmarks, frame_shape, pinch_threshold, release_threshold):
        """
        Dibuja una línea entre pulgar e índice que cambia de color
        según qué tan cerca estás de activar el pinch.
        Verde = lejos, Amarillo = cerca, Rojo = pinch activo.
        """
        h, w, _ = frame_shape

        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]

        tx = int(thumb_tip.x * w)
        ty = int(thumb_tip.y * h)
        ix = int(index_tip.x * w)
        iy = int(index_tip.y * h)

        # Distancia normalizada (misma que usa is_pinching)
        import math
        distance = math.sqrt(
            (thumb_tip.x - index_tip.x) ** 2 +
            (thumb_tip.y - index_tip.y) ** 2
        )

        # Determinar color según proximidad al umbral
        if distance < pinch_threshold:
            # Pinch activo → rojo
            color = (0, 0, 255)
            thickness = 4
        elif distance < release_threshold:
            # Zona de histéresis → naranja
            color = (0, 140, 255)
            thickness = 3
        elif distance < release_threshold * 2:
            # Cerca → amarillo
            color = (0, 255, 255)
            thickness = 2
        else:
            # Lejos → verde
            color = (0, 255, 0)
            thickness = 1

        # Línea entre pulgar e índice
        cv2.line(frame, (tx, ty), (ix, iy), color, thickness)

        # Punto medio con indicador
        mx = (tx + ix) // 2
        my = (ty + iy) // 2

        cv2.circle(frame, (mx, my), 5, color, cv2.FILLED)

    def draw_windows(self, frame, windows, active_window):
        for window in windows:

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

    def draw_status(self, frame):
        cv2.putText(
            frame,
            self.interaction_text,
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2
        )

    def get_cursor_radius(self, hovered_window, active_window):
        if active_window:
            return 25
        if hovered_window:
            return 18
        return 10

    def render(self, frame, windows, active_window):
        self.draw_windows(frame, windows, active_window)
        self.draw_status(frame)
