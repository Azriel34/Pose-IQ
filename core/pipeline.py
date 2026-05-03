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
        logging.info("Initializing Real-Time Pipeline with Targeted Visual Feedback...")
        self.camera = CameraStream()
        self.detector = PoseDetector()
        self.rules = PostureRules() 
        
        self.current_state = None  
        self.last_errors = []      
        self.ready_counter = 0     
        self.FRAMES_TO_READY = 10 

        # הגדרת חיבורי השלד (לפי אינדקסים של COCO שמוגדרים ב-AngleCalculator)
        self.SKELETON_CONNECTIONS = [
            (5, 6), (5, 7), (7, 9), (6, 8), (8, 10), # כתפיים וידיים
            (5, 11), (6, 12), (11, 12),              # פלג גוף עליון
            (11, 13), (13, 15), (12, 14), (14, 16)   # רגליים
        ]

        # מיפוי: איזו שגיאה מדליקה אילו קווים באדום?
        self.ERROR_TO_LINES = {
            'spine': [(5, 11), (6, 12), (11, 12)],       # קווי הגו (כתף למותן)
            'right_knee': [(12, 14), (14, 16)],          # רגל ימין (מותן לברך לקרסול)
            'left_knee': [(11, 13), (13, 15)],           # רגל שמאל
            'right_arm_body': [(6, 8), (8, 10)],         # יד ימין (כתף למרפק לשורש כף היד)
            'left_arm_body': [(5, 7), (7, 9)]            # יד שמאל
        }

    def draw_skeleton(self, frame, landmarks, posture_errors):
        """Draws points and highlights specifically the problematic lines in red."""
        
        # 1. איסוף כל הקווים שצריכים להיות אדומים בפריים הנוכחי
        red_lines = set()
        if posture_errors:
            for error in posture_errors:
                joint_name = error['joint']
                if joint_name in self.ERROR_TO_LINES:
                    for line in self.ERROR_TO_LINES[joint_name]:
                        red_lines.add(line)

        # 2. ציור הקווים
        for start_idx, end_idx in self.SKELETON_CONNECTIONS:
            if start_idx in landmarks and end_idx in landmarks:
                p1 = (int(landmarks[start_idx].x), int(landmarks[start_idx].y))
                p2 = (int(landmarks[end_idx].x), int(landmarks[end_idx].y))
                
                # אם הקו נמצא ברשימת השגיאות הוא ייצבע באדום, אחרת ירוק
                color = (0, 0, 255) if (start_idx, end_idx) in red_lines else (0, 255, 0)
                cv2.line(frame, p1, p2, color, 3) # עובי 3 לקו בולט יותר

        # 3. ציור נקודות המפרקים בלבן
        for idx, pt in landmarks.items():
            cv2.circle(frame, (int(pt.x), int(pt.y)), 4, (255, 255, 255), -1)

    def run(self):
        logging.info("Starting pipeline loop. Press 'q' to exit.")
        
        while True:
            start_time = time.time()
            success, frame = self.camera.read_frame()
            if not success: break

            landmarks = self.detector.find_pose(frame)
            angles = AngleCalculator.get_body_angles(landmarks)
            
            is_ready = False
            posture_errors = [] # אתחול רשימה ריקה כדי להעביר לציור גם אם אין שגיאות
            
            if landmarks and angles:
                posture_errors = self.rules.analyze_posture(angles)
                is_ready = self.rules.is_starting_pose(angles)
                
                # מעבירים את רשימת השגיאות העדכנית לפונקציית הציור
                self.draw_skeleton(frame, landmarks, posture_errors)

                # State Management Logic
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

            # UI Overlays
            fps = self.camera.calculate_fps()
            cv2.putText(frame, f"Status: {'READY' if is_ready else 'ADJUSTING'}", (10, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if is_ready else (0, 165, 255), 2) # צהוב-כתום למצב התאמה

            cv2.imshow('Pose-IQ Visual Feedback', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

        self.camera.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    PosePipeline().run()