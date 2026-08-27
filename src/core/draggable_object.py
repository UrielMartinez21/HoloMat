class DraggableObject:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        name="WINDOW",
        smoothing=0.25
    ):
        self.x_float = float(x)
        self.y_float = float(y)
        self.width = width
        self.height = height

        self.name = name

        self.dragging = False
        self.hovering = False

        self.offset_x = 0
        self.offset_y = 0

        self.smoothing = smoothing

    @property
    def x(self):
        return int(self.x_float)

    @x.setter
    def x(self, value):
        self.x_float = float(value)

    @property
    def y(self):
        return int(self.y_float)

    @y.setter
    def y(self, value):
        self.y_float = float(value)

    def contains(self, px, py):
        return (
            self.x <= px <= self.x + self.width
            and
            self.y <= py <= self.y + self.height
        )

    def update_hover(self, px, py):
        self.hovering = self.contains(px, py)

    def start_drag(self, px, py):
        if self.contains(px, py):
            self.dragging = True

            self.offset_x = px - self.x
            self.offset_y = py - self.y

            return True

        return False

    def drag(self, px, py):
        if not self.dragging:
            return

        target_x = px - self.offset_x
        target_y = py - self.offset_y

        self.x_float += (target_x - self.x_float) * self.smoothing
        self.y_float += (target_y - self.y_float) * self.smoothing

    def stop_drag(self):
        self.dragging = False
