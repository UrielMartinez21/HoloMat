import math
import time


class GestureDetector:
    def __init__(
        self,
        pinch_threshold=0.08,
        pinch_release_threshold=0.10,
        click_max_duration=0.30,
        drag_threshold=12,
        hold_duration=0.60
    ):
        self.pinch_threshold = pinch_threshold
        self.pinch_release_threshold = pinch_release_threshold
        self.click_max_duration = click_max_duration
        self.drag_threshold = drag_threshold
        self.hold_duration = hold_duration

        self.previous_pinch = False

        self.pinch_start_time = None
        self.pinch_start_position = None

        self.drag_started = False
        self.hold_triggered = False

    def _distance(self, p1, p2):
        return math.sqrt(
            (p1.x - p2.x) ** 2 +
            (p1.y - p2.y) ** 2
        )

    def _landmark_distance(self, lm1, lm2):
        return math.sqrt(
            (lm1.x - lm2.x) ** 2 +
            (lm1.y - lm2.y) ** 2 +
            (lm1.z - lm2.z) ** 2
        )

    def _pixel_distance(self, p1, p2):
        return math.sqrt(
            (p1[0] - p2[0]) ** 2 +
            (p1[1] - p2[1]) ** 2
        )

    def is_pinching(self, hand_landmarks):
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]

        distance = self._distance(thumb_tip, index_tip)

        # Histéresis: umbral diferente para iniciar vs soltar
        if self.previous_pinch:
            return distance < self.pinch_release_threshold
        else:
            return distance < self.pinch_threshold

    def _is_finger_extended(self, landmarks, tip_idx, pip_idx, mcp_idx):
        tip = landmarks[tip_idx]
        pip = landmarks[pip_idx]
        mcp = landmarks[mcp_idx]

        tip_to_mcp = self._landmark_distance(tip, mcp)
        pip_to_mcp = self._landmark_distance(pip, mcp)

        return tip_to_mcp > pip_to_mcp

    def _is_thumb_extended(self, landmarks):
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        index_mcp = landmarks[5]

        tip_dist = self._landmark_distance(thumb_tip, index_mcp)
        ip_dist = self._landmark_distance(thumb_ip, index_mcp)

        return tip_dist > ip_dist

    def _count_extended_fingers(self, hand_landmarks):
        landmarks = hand_landmarks.landmark

        fingers = [
            (8, 6, 5),
            (12, 10, 9),
            (16, 14, 13),
            (20, 18, 17),
        ]

        extended = 0

        for tip, pip, mcp in fingers:
            if self._is_finger_extended(landmarks, tip, pip, mcp):
                extended += 1

        if self._is_thumb_extended(landmarks):
            extended += 1

        return extended

    def is_hand_open(self, hand_landmarks):
        return self._count_extended_fingers(hand_landmarks) >= 5

    def is_fist(self, hand_landmarks):
        return self._count_extended_fingers(hand_landmarks) <= 1

    def update_interaction(self, hand_landmarks, x, y):
        current_pinch = self.is_pinching(hand_landmarks)
        current_time = time.time()

        event = None

        # -------------------------
        # Inicio del pinch
        # -------------------------

        if current_pinch and not self.previous_pinch:
            self.pinch_start_time = current_time
            self.pinch_start_position = (x, y)

            self.drag_started = False
            self.hold_triggered = False

            event = "PINCH_START"

        # -------------------------
        # Pinch mantenido
        # -------------------------

        elif current_pinch and self.previous_pinch:

            elapsed = current_time - self.pinch_start_time

            movement = self._pixel_distance(
                (x, y),
                self.pinch_start_position
            )

            # Movimiento suficiente → DRAG
            if movement >= self.drag_threshold:

                self.drag_started = True
                self.pinch_start_position = (x, y)
                event = "DRAG"

            # Sin movimiento pero tiempo suficiente → HOLD
            elif (
                elapsed >= self.hold_duration
                and not self.hold_triggered
            ):
                self.hold_triggered = True
                event = "HOLD"

            else:
                event = "PINCH_HOLD"

        # -------------------------
        # Fin del pinch
        # -------------------------

        elif not current_pinch and self.previous_pinch:

            elapsed = current_time - self.pinch_start_time

            movement = self._pixel_distance(
                (x, y),
                self.pinch_start_position
            )

            if (
                not self.drag_started
                and not self.hold_triggered
                and elapsed <= self.click_max_duration
                and movement < self.drag_threshold
            ):
                event = "CLICK"

            elif self.drag_started:
                event = "DRAG_END"

            else:
                event = "PINCH_END"

            self.pinch_start_time = None
            self.pinch_start_position = None

            self.drag_started = False
            self.hold_triggered = False

        self.previous_pinch = current_pinch

        return event
