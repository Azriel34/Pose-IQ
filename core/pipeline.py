import cv2
import time
import logging
from camera_stream import CameraStream
from pose_detector import PoseDetector
from angle_calculator import AngleCalculator  
from posture_rules import PostureRules        

logging.basicConfig(level=logging.INFO, format='%(message)s')

class PosePipeline:
    def __init__(self):
        logging.info("Initializing Real-Time 3D Pipeline with Debug Angles...")
        self.camera = CameraStream()
        self.detector = PoseDetector()
        self.rules = PostureRules() 
        
        self.current_state = None  
        self.last_errors = []      
        self.ready_counter = 0     
        self.FRAMES_TO_READY = 10 

        self.SKELETON_CONNECTIONS = [
            (11, 12), (11, 13), (13, 15), (12, 14), (14, 16), 
            (11, 23), (12, 24), (23, 24),                     
            (23, 25), (25, 27), (24, 26), (26, 28)            
        ]

        self.ERROR_TO_LINES = {
            'spine': [(11, 23), (12, 24), (23, 24)],       
            'right_knee': [(24, 26), (26, 28)],          
            'left_knee': [(23, 25), (25, 27)],           
            'right_arm_body': [(12, 14), (14, 16)],         
            'left_arm_body': [(11, 13), (13, 15)],
            'right_elbow': [(12, 14), (14, 16)],             
            'left_elbow': [(11, 13), (13, 15)],               
            'legs_spread': [(23, 25), (24, 26), (23, 24)] 
        }

    def draw_skeleton(self, frame, landmarks, posture_errors):
        red_lines = set()
        if posture_errors:
            for error in posture_errors:
                joint_name = error['joint']
                if joint_name in self.ERROR_TO_LINES:
                    for line in self.ERROR_TO_LINES[joint_name]:
                        red_lines.add(line)

        for start_idx, end_idx in self.SKELETON_CONNECTIONS:
            if start_idx in landmarks and end_idx in landmarks:
                p1 = (int(landmarks[start_idx].x), int(landmarks[start_idx].y))
                p2 = (int(landmarks[end_idx].x), int(landmarks[end_idx].y))
                
                color = (0, 0, 255) if (start_idx, end_idx) in red_lines else (0, 255, 0)
                cv2.line(frame, p1, p2, color, 3) 

        for idx, pt in landmarks.items():
            if idx > 10: 
                cv2.circle(frame, (int(pt.x), int(pt.y)), 4, (255, 255, 255), -1)

    # הפונקציה החדשה שמציירת את המספרים על המסך
    def draw_debug_angles(self, frame, landmarks, angles):
        mapping = {
            'right_knee': 26, 'left_knee': 25,
            'right_elbow': 14, 'left_elbow': 13,
            'right_arm_body': 12, 'left_arm_body': 11,
            'spine': 24,
            'legs_spread': 23
        }
        for joint, angle in angles.items():
            if joint in mapping and mapping[joint] in landmarks:
                pt = landmarks[mapping[joint]]
                # מצייר את הזווית בטקסט צהוב ליד המפרק
                cv2.putText(frame, f"{joint}: {int(angle)}", (int(pt.x) + 10, int(pt.y) - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    def run(self):
        logging.info("Starting pipeline loop. Press 'q' to exit.")
        
        while True:
            start_time = time.time()
            success, frame = self.camera.read_frame()
            if not success: break

            landmarks = self.detector.find_pose(frame)
            angles = AngleCalculator.get_body_angles(landmarks)
            
            is_ready = False
            posture_errors = [] 
            
            if landmarks and angles:
                posture_errors = self.rules.analyze_posture(angles)
                is_ready = self.rules.is_starting_pose(angles)
                
                self.draw_skeleton(frame, landmarks, posture_errors)
                # קריאה לפונקציית הדיבאג החדשה
                self.draw_debug_angles(frame, landmarks, angles)

                if is_ready and not posture_errors:
                    self.ready_counter += 1
                    if self.ready_counter >= self.FRAMES_TO_READY:
                        if self.current_state != 'READY':
                            logging.info("🟩 READY!")
                            self.current_state = 'READY'
                            self.last_errors = []
                else:
                    self.ready_counter = 0
                    if posture_errors:
                        current_messages = [e['message'] for e in posture_errors]
                        if self.current_state != 'ISSUES' or current_messages != [e['message'] for e in self.last_errors]:
                            logging.warning(f"🟥 ISSUES: {posture_errors}")
                            self.current_state = 'ISSUES'
                            self.last_errors = posture_errors

            cv2.putText(frame, f"Status: {'READY' if is_ready else 'ADJUSTING'}", (10, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if is_ready else (0, 165, 255), 2) 

            cv2.imshow('Pose-IQ 3D Feedback', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

        self.camera.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    PosePipeline().run()