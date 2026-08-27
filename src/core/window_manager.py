from core.draggable_object import DraggableObject


class WindowManager:
    def __init__(self):
        self.windows = []
        self.active_window = None

    def add_window(self, window):
        self.windows.append(window)

    def update_hover(self, px, py):
        hovered = None

        # Recorremos de atrás hacia adelante
        # para dar prioridad a la ventana superior
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

                # Llevar al frente
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