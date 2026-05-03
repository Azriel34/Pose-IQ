import cv2
import mediapipe as mp

from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class Point:
    x: float
    y: float
    z: float
    visibility: float

class PoseDetector:
    def __init__(self):
        # שימוש סטנדרטי במודול, עכשיו שזה פייתון 3.10 זה אמור לעבוד חלק
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    def find_pose(self, frame) -> Optional[Dict[int, Point]]:
        # MediaPipe דורש תמונות בפורמט RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)

        if not results.pose_landmarks:
            return None

        landmarks = {}
        h, w, c = frame.shape
        
        # חילוץ 33 הנקודות בתלת-מימד
        for id, lm in enumerate(results.pose_landmarks.landmark):
            landmarks[id] = Point(x=lm.x * w, y=lm.y * h, z=lm.z * w, visibility=lm.visibility)

        return landmarks