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
