import time

from core.draggable_object import DraggableObject


class WindowManager:
    def __init__(self):
        self.windows = []
        self.active_window = None
        self.click_actions = {}

        # Hover-to-click (dwell)
        self.hover_target = None
        self.hover_start_time = 0
        self.hover_click_delay = 0.8
        self.hover_click_triggered = False

    def add_window(self, window):
        self.windows.append(window)

    def register_click_action(self, window_name, callback):
        """Registra una función a ejecutar cuando se hace click en una ventana."""
        self.click_actions[window_name] = callback

    def update_hover(self, px, py, is_pinching=False):
        """
        Actualiza hover de ventanas.
        is_pinching: si True, suspende hover-to-click (el usuario está arrastrando).
        """
        hovered = None

        for window in reversed(self.windows):
            window.update_hover(px, py)

            if window.hovering and hovered is None:
                hovered = window
            else:
                window.hovering = False

        # Hover-to-click solo cuando NO hay pinch activo
        if is_pinching:
            self._cancel_hover_click()
        else:
            self._update_hover_click(hovered)

        return hovered

    def _update_hover_click(self, hovered_window):
        """Actualiza el sistema de hover-to-click."""
        if hovered_window is None:
            self._cancel_hover_click()
            return

        # Solo contar hover si la ventana tiene click_action
        if hovered_window.name not in self.click_actions:
            self._cancel_hover_click()
            return

        # Si cambió la ventana, resetear
        if hovered_window != self.hover_target:
            self.hover_target = hovered_window
            self.hover_start_time = time.time()
            self.hover_click_triggered = False
            return

        # Ya se disparó, no repetir
        if self.hover_click_triggered:
            return

        elapsed = time.time() - self.hover_start_time

        if elapsed >= self.hover_click_delay:
            self.hover_click_triggered = True
            self.click_actions[hovered_window.name]()
            print(f"HOVER CLICK en {hovered_window.name}")

    def _cancel_hover_click(self):
        """Cancela cualquier hover-to-click en progreso."""
        self.hover_target = None
        self.hover_start_time = 0
        self.hover_click_triggered = False

    def get_hover_click_progress(self):
        """Retorna (ventana, progreso 0.0-1.0) del hover-to-click actual."""
        if self.hover_target is None or self.hover_click_triggered:
            return None, 0.0

        elapsed = time.time() - self.hover_start_time
        progress = min(elapsed / self.hover_click_delay, 1.0)
        return self.hover_target, progress

    def start_drag(self, px, py):
        for window in reversed(self.windows):
            if window.start_drag(px, py):
                self.active_window = window

                self.windows.remove(window)
                self.windows.append(window)

                self._cancel_hover_click()

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

        self._cancel_hover_click()

    def handle_event(self, event, x, y, gesture_detector, hand_landmarks):
        """Procesa un evento de gesto y retorna el texto de interacción."""

        if event == "HOLD":
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
