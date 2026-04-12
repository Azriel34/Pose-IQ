import math

class AngleCalculator:
    
    @staticmethod
    def calculate_2d_angle(a, b, c):
        """
        Task: implement angle formula
        Calculates the angle between three points.
        B is the vertex (the joint we are measuring).
        a, b, c are 'Point' objects (from our dataclass) with x and y coordinates.
        """
        if not a or not b or not c:
            return 0.0

        # Calculate angle in radians using arctangent
        radians = math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x)
        
        # Convert to degrees
        angle = abs(radians * 180.0 / math.pi)
        
        # Task: normalize coordinates (ensure angle is between 0 and 180)
        # Joints don't usually bend past 180 degrees in a standard 2D projection
        if angle > 180.0:
            angle = 360.0 - angle
            
        return round(angle, 1)

    @classmethod
    def get_body_angles(cls, landmarks):
        """
        Task: build AngleCalculator & extract specific joints
        Expects the landmarks dictionary from PoseDetector.
        Returns a dictionary of calculated angles.
        """
        angles = {}
        
        if not landmarks:
            return angles

        # MediaPipe Landmark Mapping (Right side for example, can be extended to Left)
        # 12: Right Shoulder, 24: Right Hip, 26: Right Knee, 28: Right Ankle

        # 1. Hip Angle (Shoulder -> Hip -> Knee)
        if 12 in landmarks and 24 in landmarks and 26 in landmarks:
            angles['hip'] = cls.calculate_2d_angle(
                landmarks[12], landmarks[24], landmarks[26]
            )

        # 2. Knee Angle (Hip -> Knee -> Ankle)
        if 24 in landmarks and 26 in landmarks and 28 in landmarks:
            angles['knee'] = cls.calculate_2d_angle(
                landmarks[24], landmarks[26], landmarks[28]
            )

        # 3. Spine/Torso Angle (Angle of the back relative to vertical)
        # We create a virtual point directly above the hip to represent a perfectly straight vertical back
        if 12 in landmarks and 24 in landmarks:
            shoulder = landmarks[12]
            hip = landmarks[24]
            # Virtual point directly above the hip
            vertical_ref = type('Point', (), {'x': hip.x, 'y': hip.y - 0.5})() 
            angles['spine'] = cls.calculate_2d_angle(
                shoulder, hip, vertical_ref
            )

        return angles