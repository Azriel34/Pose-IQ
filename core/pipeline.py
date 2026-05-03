import cv2
import time
import logging
from camera_stream import CameraStream
from pose_detector import PoseDetector
from angle_calculator import AngleCalculator  
from posture_rules import PostureRules        

# Setup basic logging to see outputs in the terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s' 
)

class PosePipeline:
    def __init__(self):
        logging.info("Initializing Real-Time Pipeline with YOLOv8...")
        self.camera = CameraStream()
        self.detector = PoseDetector()
        self.rules = PostureRules() 
        
        # Variables for state management and preventing terminal spam
        self.current_state = None  
        self.last_errors = []      
        self.ready_counter = 0     
        self.FRAMES_TO_READY = 10 

    def run(self):
        logging.info("Starting pipeline loop. Press 'q' to exit.")
        
        while True:
            start_time = time.time()

            # 1. Read frame from camera
            success, frame = self.camera.read_frame()
            if not success:
                logging.error("Failed to read from camera. Exiting pipeline...")
                break

            # 2. Process frame (Pose Detection)
            landmarks = self.detector.find_pose(frame)

            # 3. Calculate Angles
            angles = AngleCalculator.get_body_angles(landmarks)
            
            # Uncomment the next line if you want to see live angles printed
            # print(f"Live Angles: {angles}") 
            
            # 4. Apply Posture Rules
            if angles:
                posture_errors = self.rules.analyze_posture(angles)
                is_ready = self.rules.is_starting_pose(angles)
                
                # Requires a sequence of valid frames and ensures no active errors
                if is_ready and not posture_errors:
                    self.ready_counter += 1
                    if self.ready_counter >= self.FRAMES_TO_READY:
                        if self.current_state != 'READY':
                            logging.info("🟩 READY! Starting Pose Detected")
                            self.current_state = 'READY'
                            self.last_errors = []
                else:
                    self.ready_counter = 0 # Reset the counter as soon as there is movement or an error
                    
                    if posture_errors:
                        current_messages = [e['message'] for e in posture_errors]
                        last_messages = [e['message'] for e in self.last_errors]
                        
                        if self.current_state != 'ISSUES' or current_messages != last_messages:
                            logging.warning(f"🟥 ISSUES: {posture_errors}")
                            self.current_state = 'ISSUES'
                            self.last_errors = posture_errors
            
            # 5. Calculate metrics (Latency & FPS)
            process_time_ms = (time.time() - start_time) * 1000
            fps = self.camera.calculate_fps()

            # 6. Display Stats on Frame 
            cv2.putText(frame, f"FPS: {fps}", (10, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            
            # Color latency text based on performance
            latency_color = (0, 255, 0) if process_time_ms < 100 else (0, 0, 255)
            cv2.putText(frame, f"Latency: {process_time_ms:.1f}ms", (10, 80), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, latency_color, 2, cv2.LINE_AA)

            # 7. Display frame
            cv2.imshow('Pose-IQ Pipeline', frame)

            # Exit condition
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("Pipeline stopped by user.")
                break

        # Release resources
        self.camera.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        pipeline = PosePipeline()
        pipeline.run()
    except Exception as e:
        logging.critical(f"Pipeline crashed: {e}")