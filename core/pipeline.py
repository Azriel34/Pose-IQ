import cv2
import time
import logging
from camera_stream import CameraStream
from pose_detector import PoseDetector

# Task: add basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PosePipeline:
    def __init__(self):
        logging.info("Initializing Real-Time Pipeline...")
        # Task: connect camera -> pose detector
        self.camera = CameraStream()
        self.detector = PoseDetector()

    def run(self):
        logging.info("Starting pipeline loop. Press 'q' to exit.")
        
        # Task: implement main loop
        while True:
            start_time = time.time() # For latency measurement

            # 1. Read frame from camera
            success, frame = self.camera.read_frame()
            if not success:
                logging.error("Failed to read from camera. Exiting pipeline...")
                break

            # 2. Process frame (Pose Detection)
            # The writeable=False optimization in your pose_detector helps latency here
            landmarks = self.detector.find_pose(frame)

            # 3. Calculate metrics (Latency < 100ms & FPS)
            process_time_ms = (time.time() - start_time) * 1000
            fps = self.camera.calculate_fps()

            # Optional: Log occasionally to avoid spamming the console
            if landmarks and int(time.time() * 2) % 2 == 0: 
                logging.debug(f"Detected {len(landmarks)} landmarks. Latency: {process_time_ms:.1f}ms")

            # 4. Display Stats on Frame (so we can verify Acceptance Criteria)
            cv2.putText(frame, f"FPS: {fps}", (10, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            
            # Color latency text based on performance (Warning if > 100ms)
            latency_color = (0, 255, 0) if process_time_ms < 100 else (0, 0, 255)
            cv2.putText(frame, f"Latency: {process_time_ms:.1f}ms", (10, 80), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, latency_color, 2, cv2.LINE_AA)

            # 5. Display frame
            cv2.imshow('Pose-IQ Pipeline (Story 3)', frame)

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