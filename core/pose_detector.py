import cv2
import mediapipe as mp
from dataclasses import dataclass
from typing import Dict, Optional

# Task: Map landmarks to structured object
@dataclass
class Point:
    x: float
    y: float
    z: float
    visibility: float

class PoseDetector:
    def __init__(self, 
                 static_mode: bool = False, 
                 model_complexity: int = 1, 
                 min_detection_confidence: float = 0.5, 
                 min_tracking_confidence: float = 0.5):
        
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_mode,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def find_pose(self, frame) -> Optional[Dict[int, Point]]:
        """
           Receives a frame (from OpenCV), detects a pose, and returns a dictionary of structured points.        """
        # MediaPipe expects RGB, but OpenCV reads in BGR
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # -improve latency
        image_rgb.flags.writeable = False
        results = self.pose.process(image_rgb)
        image_rgb.flags.writeable = True

        # Task: Handle missing detections
        if not results.pose_landmarks:
            return None 

        # Task: Map landmarks to structured object
        landmarks = {}
        for id, lm in enumerate(results.pose_landmarks.landmark):
            landmarks[id] = Point(x=lm.x, y=lm.y, z=lm.z, visibility=lm.visibility)

        return landmarks