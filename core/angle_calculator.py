import math

class AngleCalculator:
    
    @staticmethod
    def calculate_2d_angle(a, b, c):
        """
        Calculates the angle between three points.
        'b' is the vertex (the joint being measured).
        """
        if not a or not b or not c:
            return 0.0

        # Calculate angle in radians using arctangent
        radians = math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x)
        
        # Convert radians to degrees
        angle = abs(radians * 180.0 / math.pi)
        
        # Normalize the angle to a 0-180 range
        # (Since human joints generally don't bend past 180 degrees in a 2D projection)
        if angle > 180.0:
            angle = 360.0 - angle
            
        return round(angle, 1)

    @classmethod
    def get_body_angles(cls, landmarks):
        """
        Expects a dictionary of MediaPipe landmarks.
        Returns a dictionary of calculated body angles.
        """
        angles = {}
        
        if not landmarks:
            return angles

        # ====================
        # Right Side
        # ====================
        
        # Right Hip (Shoulder -> Hip -> Knee)
        if 12 in landmarks and 24 in landmarks and 26 in landmarks:
            angles['right_hip'] = cls.calculate_2d_angle(landmarks[12], landmarks[24], landmarks[26])

        # Right Knee (Hip -> Knee -> Ankle)
        if 24 in landmarks and 26 in landmarks and 28 in landmarks:
            angles['right_knee'] = cls.calculate_2d_angle(landmarks[24], landmarks[26], landmarks[28])

        # Right Ankle (Knee -> Ankle -> Foot Index)
        if 26 in landmarks and 28 in landmarks and 32 in landmarks:
            angles['right_ankle'] = cls.calculate_2d_angle(landmarks[26], landmarks[28], landmarks[32])

        # Right Elbow (Shoulder -> Elbow -> Wrist)
        if 12 in landmarks and 14 in landmarks and 16 in landmarks:
            angles['right_elbow'] = cls.calculate_2d_angle(landmarks[12], landmarks[14], landmarks[16])

        # Right Shoulder (Hip -> Shoulder -> Elbow) - Measures arm elevation
        if 24 in landmarks and 12 in landmarks and 14 in landmarks:
            angles['right_shoulder'] = cls.calculate_2d_angle(landmarks[24], landmarks[12], landmarks[14])


        # ====================
        # Left Side
        # ====================
        
        # Left Hip (Shoulder -> Hip -> Knee)
        if 11 in landmarks and 23 in landmarks and 25 in landmarks:
            angles['left_hip'] = cls.calculate_2d_angle(landmarks[11], landmarks[23], landmarks[25])

        # Left Knee (Hip -> Knee -> Ankle)
        if 23 in landmarks and 25 in landmarks and 27 in landmarks:
            angles['left_knee'] = cls.calculate_2d_angle(landmarks[23], landmarks[25], landmarks[27])

        # Left Ankle (Knee -> Ankle -> Foot Index)
        if 25 in landmarks and 27 in landmarks and 31 in landmarks:
            angles['left_ankle'] = cls.calculate_2d_angle(landmarks[25], landmarks[27], landmarks[31])

        # Left Elbow (Shoulder -> Elbow -> Wrist)
        if 11 in landmarks and 13 in landmarks and 15 in landmarks:
            angles['left_elbow'] = cls.calculate_2d_angle(landmarks[11], landmarks[13], landmarks[15])

        # Left Shoulder (Hip -> Shoulder -> Elbow)
        if 23 in landmarks and 11 in landmarks and 13 in landmarks:
            angles['left_shoulder'] = cls.calculate_2d_angle(landmarks[23], landmarks[11], landmarks[13])


        # ====================
        # Posture Metrics
        # ====================
        
        # Spine Angle (Torso forward/backward tilt)
        if 12 in landmarks and 24 in landmarks:
            shoulder = landmarks[12]
            hip = landmarks[24]
            # Create a virtual point directly above the hip to represent a perfectly vertical reference line
            vertical_ref_spine = type('Point', (), {'x': hip.x, 'y': hip.y - 0.5})() 
            angles['spine'] = cls.calculate_2d_angle(shoulder, hip, vertical_ref_spine)

        # Neck Angle (Text Neck - Forward head posture)
        # Calculates the angle between the right ear, right shoulder, and a vertical reference line
        if 8 in landmarks and 12 in landmarks:
            ear = landmarks[8]
            shoulder = landmarks[12]
            # Virtual point directly above the shoulder
            vertical_ref_neck = type('Point', (), {'x': shoulder.x, 'y': shoulder.y - 0.5})()
            angles['neck'] = cls.calculate_2d_angle(ear, shoulder, vertical_ref_neck)

        return angles