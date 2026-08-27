from core.draggable_object import DraggableObject


class WindowManager:
    def __init__(self):
        self.windows = []
        self.active_window = None
        self.click_actions = {}

    def add_window(self, window):
        self.windows.append(window)

    def register_click_action(self, window_name, callback):
        """Registra una función a ejecutar cuando se hace click en una ventana."""
        self.click_actions[window_name] = callback

    def update_hover(self, px, py):
        hovered = None

        for window in reversed(self.windows):
            window.update_hover(px, py)

            if window.hovering and hovered is None:
                hovered = window
            else:
                window.hovering = False

        return hovered

    def start_drag(self, px, py):
        for window in reversed(self.windows):
            if window.start_drag(px, py):
                self.active_window = window

                self.windows.remove(window)
                self.windows.append(window)

                return window

        return None

    def drag(self, px, py):
        if self.active_window:
            self.active_window.drag(px, py)

    def stop_drag(self):
        if self.active_window:
            self.active_window.stop_drag()

        self.active_window = None

    def get_window_at(self, px, py):
        for window in reversed(self.windows):
            if window.contains(px, py):
                return window

        return None

    def clear_hover(self):
        for window in self.windows:
            window.hovering = False

    def handle_event(self, event, x, y, gesture_detector, hand_landmarks):
        """Procesa un evento de gesto y retorna el texto de interacción."""

        if event == "CLICK":
            clicked_window = self.get_window_at(x, y)

            if clicked_window:
                # Ejecutar acción de click si existe
                if clicked_window.name in self.click_actions:
                    self.click_actions[clicked_window.name]()

                print(f"CLICK en {clicked_window.name}")
                return f"CLICK: {clicked_window.name}"

            return "CLICK"

        elif event == "HOLD":
            held_window = self.get_window_at(x, y)

            if held_window:
                return f"HOLD: {held_window.name}"

            return "HOLD"

        elif event == "DRAG":
            if self.active_window is None:
                self.start_drag(x, y)

            self.drag(x, y)
            return "DRAG"

        elif event == "DRAG_END":
            self.stop_drag()
            return "DRAG END"

        elif event == "PINCH_START":
            return "PINCH START"

        elif event == "PINCH_HOLD":
            return "PINCH HOLD"

        elif event == "PINCH_END":
            return "PINCH END"

        elif gesture_detector.is_fist(hand_landmarks):
            return "PUNO"

        elif gesture_detector.is_hand_open(hand_landmarks):
            return "MANO ABIERTA"

        return None
