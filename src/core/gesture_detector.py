import math
import time
from collections import deque


class GestureDetector:
    def __init__(
        self,
        pinch_threshold=0.09,
        pinch_release_threshold=0.11,
        pinch_drag_release_threshold=0.14,
        drag_threshold=12,
        hold_duration=0.60,
        pinch_buffer_size=3,
        distance_smoothing_frames=5
    ):
        self.pinch_threshold = pinch_threshold
        self.pinch_release_threshold = pinch_release_threshold
        self.pinch_drag_release_threshold = pinch_drag_release_threshold
        self.drag_threshold = drag_threshold
        self.hold_duration = hold_duration

        self.previous_pinch = False

        self.pinch_start_time = None
        self.pinch_start_position = None

        self.drag_started = False
        self.hold_triggered = False

        # Buffer para pinch (drag)
        self.pinch_buffer_size = pinch_buffer_size
        self.pinch_buffer = deque(maxlen=pinch_buffer_size)
        self.distance_history = deque(maxlen=distance_smoothing_frames)

        # Protección contra soltar durante drag
        self.release_buffer_size = 4
        self.release_buffer = deque(maxlen=self.release_buffer_size)

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

    def _get_smoothed_distance(self, hand_landmarks):
        """Distancia pulgar-índice con mediana."""
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]

        raw_distance = self._distance(thumb_tip, index_tip)
        self.distance_history.append(raw_distance)

        sorted_distances = sorted(self.distance_history)
        mid = len(sorted_distances) // 2

        if len(sorted_distances) % 2 == 0:
            return (sorted_distances[mid - 1] + sorted_distances[mid]) / 2
        else:
            return sorted_distances[mid]

    def _confirm_pinch_state(self, raw_pinch):
        """Confirma cambio si se mantiene por N frames."""
        self.pinch_buffer.append(raw_pinch)

        if len(self.pinch_buffer) < self.pinch_buffer_size:
            return self.previous_pinch

        if all(self.pinch_buffer):
            return True
        elif not any(self.pinch_buffer):
            return False

        return self.previous_pinch

    def is_pinching(self, hand_landmarks):
        """Detecta pinch (pulgar + índice) para drag."""
        distance = self._get_smoothed_distance(hand_landmarks)

        if self.drag_started:
            release_threshold = self.pinch_drag_release_threshold
        else:
            release_threshold = self.pinch_release_threshold

        if self.previous_pinch:
            raw_pinch = distance < release_threshold
        else:
            raw_pinch = distance < self.pinch_threshold

        # Protección contra soltar durante drag
        if self.drag_started and not raw_pinch:
            self.release_buffer.append(False)
            if not all(not x for x in self.release_buffer):
                raw_pinch = True
        elif self.drag_started:
            self.release_buffer.clear()

        return self._confirm_pinch_state(raw_pinch)

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
        # Drag (pulgar + índice)
        # -------------------------

        if current_pinch and not self.previous_pinch:
            self.pinch_start_time = current_time
            self.pinch_start_position = (x, y)

            self.drag_started = False
            self.hold_triggered = False
            self.release_buffer.clear()

            event = "PINCH_START"

        elif current_pinch and self.previous_pinch:

            elapsed = current_time - self.pinch_start_time

            movement = self._pixel_distance(
                (x, y),
                self.pinch_start_position
            )

            if movement >= self.drag_threshold:
                self.drag_started = True
                self.pinch_start_position = (x, y)
                event = "DRAG"

            elif (
                elapsed >= self.hold_duration
                and not self.hold_triggered
            ):
                self.hold_triggered = True
                event = "HOLD"

            else:
                event = "PINCH_HOLD"

        elif not current_pinch and self.previous_pinch:

            if self.drag_started:
                event = "DRAG_END"
            else:
                event = "PINCH_END"

            self.pinch_start_time = None
            self.pinch_start_position = None

            self.drag_started = False
            self.hold_triggered = False
            self.release_buffer.clear()

        self.previous_pinch = current_pinch

        return event
