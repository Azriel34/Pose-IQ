from ultralytics import YOLO
from dataclasses import dataclass
from typing import Dict, Optional

# Structured object for a body landmark
@dataclass
class Point:
    x: float
    y: float
    z: float
    visibility: float

class PoseDetector:
    def __init__(self):
        # Load the lightweight YOLOv8 pose model
        # It will automatically download 'yolov8n-pose.pt' on the first run
        self.model = YOLO('yolov8n-pose.pt')

    def find_pose(self, frame) -> Optional[Dict[int, Point]]:
        """
        Receives a frame, detects a pose using YOLOv8, 
        and returns a dictionary of structured points with high confidence.
        """
        # Run YOLOv8 inference on the frame (verbose=False hides console spam)
        results = self.model(frame, verbose=False)

        # Check if a person or keypoints were detected
        if not results or not results[0].keypoints or len(results[0].keypoints.xy[0]) == 0:
            return None 

        # Extract coordinates and confidence scores for the first detected person
        keypoints = results[0].keypoints
        xy = keypoints.xy[0].cpu().numpy()       # [X, Y] coordinates
        conf = keypoints.conf[0].cpu().numpy()   # Visibility / Confidence score

        landmarks = {}
        
        # YOLO returns 17 keypoints in COCO format
        for id, (point, visibility) in enumerate(zip(xy, conf)):
            # Filter out guesses: Only keep points the model is at least 50% sure about
            if float(visibility) > 0.5:
                # YOLO doesn't provide native depth (Z), so we set it to 0.0
                landmarks[id] = Point(x=float(point[0]), y=float(point[1]), z=0.0, visibility=float(visibility))

        return landmarks