# === File: modules/vision.py ===

import cv2
import mediapipe as mp
import numpy as np
from scipy.spatial import distance

class FaceEyeDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier('haar/haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier('haar/haarcascade_eye.xml')
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

        # Left and right eye landmark indices (for EAR calculation)
        self.LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]

    def eye_aspect_ratio(self, eye_landmarks):
        A = distance.euclidean(eye_landmarks[1], eye_landmarks[5])
        B = distance.euclidean(eye_landmarks[2], eye_landmarks[4])
        C = distance.euclidean(eye_landmarks[0], eye_landmarks[3])
        ear = (A + B) / (2.0 * C)
        return ear

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        eyes_detected = 0
        blink_ratio = None

        # OpenCV eye detection (basic fallback)
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            eyes_detected = len(eyes)
            break

        # MediaPipe face mesh detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            h, w, _ = frame.shape
            face_landmarks = results.multi_face_landmarks[0]

            def extract_points(indexes):
                return [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in indexes]

            left_eye_pts = extract_points(self.LEFT_EYE_IDX)
            right_eye_pts = extract_points(self.RIGHT_EYE_IDX)

            left_ear = self.eye_aspect_ratio(left_eye_pts)
            right_ear = self.eye_aspect_ratio(right_eye_pts)
            blink_ratio = (left_ear + right_ear) / 2.0

        return len(faces), eyes_detected, blink_ratio
