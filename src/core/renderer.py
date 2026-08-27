import cv2
import numpy as np


class Renderer:
    def __init__(self):
        self.interaction_text = "Sin gesto"

        # Colores estilo Concept Bytes
        self.color_primary = (230, 216, 173)     # Azul claro (LIGHT_BLUE en BGR)
        self.color_hover = (255, 255, 200)       # Azul más brillante
        self.color_active = (0, 200, 255)        # Naranja para drag
        self.color_pinch = (0, 100, 255)         # Rojo-naranja para pinch activo
        self.color_text = (230, 216, 173)        # Mismo azul claro
        self.color_bg = (40, 20, 20)             # Fondo de ventana (navy oscuro)

    def draw_finger_point(self, frame, x, y, is_pinching=False, is_hovering=False):
        """
        Dibuja un punto/anillo en la punta del índice.
        Estilo Concept Bytes: anillo azul claro.
        """
        if is_pinching:
            color = self.color_pinch
            radius = 18
            thickness = 4
        elif is_hovering:
            color = self.color_hover
            radius = 16
            thickness = 3
        else:
            color = self.color_primary
            radius = 15
            thickness = 3

        # Anillo principal
        cv2.circle(frame, (x, y), radius, color, thickness)

        # Punto central sutil
        cv2.circle(frame, (x, y), 3, color, cv2.FILLED)

    def draw_pinch_feedback(self, frame, hand_landmarks, frame_shape, pinch_threshold, release_threshold):
        """
        Línea entre pulgar e índice. Solo visible cuando
        estás cerca del umbral de pinch (no siempre).
        """
        h, w, _ = frame_shape

        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]

        tx = int(thumb_tip.x * w)
        ty = int(thumb_tip.y * h)
        ix = int(index_tip.x * w)
        iy = int(index_tip.y * h)

        import math
        distance = math.sqrt(
            (thumb_tip.x - index_tip.x) ** 2 +
            (thumb_tip.y - index_tip.y) ** 2
        )

        # Solo mostrar feedback cuando estás cerca o en pinch
        if distance >= release_threshold * 1.8:
            return

        if distance < pinch_threshold:
            color = self.color_pinch
            thickness = 3
        elif distance < release_threshold:
            color = self.color_active
            thickness = 2
        else:
            # Cerca pero no activado → sutil
            color = self.color_primary
            thickness = 1

        cv2.line(frame, (tx, ty), (ix, iy), color, thickness)

        # Punto en el pulgar cuando está cerca
        cv2.circle(frame, (tx, ty), 8, color, 2)

    def draw_windows(self, frame, windows, active_window):
        for window in windows:

            x = window.x
            y = window.y
            w = window.width
            h = window.height

            # Determinar estado y color
            if window.dragging:
                color = self.color_active
                thickness = 4
                corner_len = 25
            elif window.hovering:
                color = self.color_hover
                thickness = 3
                corner_len = 22
            else:
                color = self.color_primary
                thickness = 2
                corner_len = 20

            # Fondo semi-transparente navy
            overlay = frame.copy()
            cv2.rectangle(
                overlay,
                (x, y),
                (x + w, y + h),
                self.color_bg,
                cv2.FILLED
            )
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

            # Esquinas estilo HUD
            self._draw_corner_brackets(
                frame, x, y, w, h,
                color, thickness, corner_len
            )

            # Borde superior completo (línea fina)
            cv2.line(
                frame,
                (x + corner_len, y),
                (x + w - corner_len, y),
                color,
                1
            )

            # Línea separadora debajo del título
            line_y = y + 50
            cv2.line(
                frame,
                (x + 10, line_y),
                (x + w - 10, line_y),
                color,
                1
            )

            # Nombre de la ventana
            cv2.putText(
                frame,
                window.name,
                (x + 15, y + 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                color,
                2
            )

    def _draw_corner_brackets(self, frame, x, y, w, h, color, thickness=2, corner_len=20):
        """Dibuja solo las esquinas del rectángulo, estilo HUD."""
        # Esquina superior izquierda
        cv2.line(frame, (x, y), (x + corner_len, y), color, thickness)
        cv2.line(frame, (x, y), (x, y + corner_len), color, thickness)

        # Esquina superior derecha
        cv2.line(frame, (x + w, y), (x + w - corner_len, y), color, thickness)
        cv2.line(frame, (x + w, y), (x + w, y + corner_len), color, thickness)

        # Esquina inferior izquierda
        cv2.line(frame, (x, y + h), (x + corner_len, y + h), color, thickness)
        cv2.line(frame, (x, y + h), (x, y + h - corner_len), color, thickness)

        # Esquina inferior derecha
        cv2.line(frame, (x + w, y + h), (x + w - corner_len, y + h), color, thickness)
        cv2.line(frame, (x + w, y + h), (x + w, y + h - corner_len), color, thickness)

    def draw_status(self, frame, frame_height):
        """Status en la esquina inferior izquierda, discreto."""
        cv2.putText(
            frame,
            self.interaction_text,
            (30, frame_height - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            self.color_primary,
            1
        )

    def render(self, frame, windows, active_window):
        self.draw_windows(frame, windows, active_window)
        self.draw_status(frame, frame.shape[0])
