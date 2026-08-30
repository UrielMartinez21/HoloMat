import math
import time

import cv2
import mediapipe as mp


class OneEuroFilter:
    """Filtro One Euro: suave cuando quieto, rápido cuando se mueve."""

    def __init__(self, min_cutoff=1.0, beta=0.007, d_cutoff=1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff

        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None

    def _smoothing_factor(self, t_e, cutoff):
        r = 2 * math.pi * cutoff * t_e
        return r / (r + 1)

    def __call__(self, x, t=None):
        if t is None:
            t = time.time()

        if self.t_prev is None:
            self.x_prev = x
            self.dx_prev = 0.0
            self.t_prev = t
            return x

        t_e = t - self.t_prev
        if t_e <= 0:
            t_e = 1e-6

        a_d = self._smoothing_factor(t_e, self.d_cutoff)
        dx = (x - self.x_prev) / t_e
        dx_hat = a_d * dx + (1 - a_d) * self.dx_prev

        cutoff = self.min_cutoff + self.beta * abs(dx_hat)

        a = self._smoothing_factor(t_e, cutoff)
        x_hat = a * x + (1 - a) * self.x_prev

        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t

        return x_hat


class HandTracker:
    def __init__(
        self,
        max_hands=1,
        detection_confidence=0.75,
        tracking_confidence=0.6,
    ):
        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

        # CLAHE para normalizar iluminación
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

        # One Euro Filter para el cursor
        self.filter_x = OneEuroFilter(min_cutoff=1.5, beta=0.01)
        self.filter_y = OneEuroFilter(min_cutoff=1.5, beta=0.01)

    def _preprocess(self, frame):
        """Normaliza iluminación."""
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l = self.clahe.apply(l)
        lab = cv2.merge([l, a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    def process(self, frame):
        """Procesa un frame y retorna los resultados de MediaPipe."""
        processed = self._preprocess(frame)
        rgb_frame = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
        return self.hands.process(rgb_frame)

    def get_index_pos(self, hand_landmarks, frame_shape):
        """Retorna la posición filtrada del índice en píxeles."""
        height, width, _ = frame_shape

        tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]

        t = time.time()
        x = self.filter_x(tip.x * width, t)
        y = self.filter_y(tip.y * height, t)

        return int(x), int(y)

    def close(self):
        self.hands.close()
