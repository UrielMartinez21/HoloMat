import cv2
import mediapipe as mp


class HandTracker:
    def __init__(
        self,
        max_hands=2,
        detection_confidence=0.6,
        tracking_confidence=0.6,
    ):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

    def process(self, frame, draw=True):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if draw and results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                )

        return results

    def get_index_tip(self, hand_landmarks, frame_shape):
        height, width, _ = frame_shape

        index_tip = hand_landmarks.landmark[
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP
        ]

        x = int(index_tip.x * width)
        y = int(index_tip.y * height)

        return x, y

    def close(self):
        self.hands.close()