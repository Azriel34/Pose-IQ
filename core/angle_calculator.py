import math

class AngleCalculator:
    # All 17 keypoints in COCO (YOLOv8) format
    KP = {
        'nose': 0, 'l_eye': 1, 'r_eye': 2, 'l_ear': 3, 'r_ear': 4,
        'l_shoulder': 5, 'r_shoulder': 6, 'l_elbow': 7, 'r_elbow': 8,
        'l_wrist': 9, 'r_wrist': 10, 'l_hip': 11, 'r_hip': 12,
        'l_knee': 13, 'r_knee': 14, 'l_ankle': 15, 'r_ankle': 16
    }

    @staticmethod
    def calculate_2d_angle(a, b, c):
        """Calculates the 2D angle between three points with B as the vertex."""
        if not a or not b or not c:
            return 0.0

        radians = math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x)
        angle = abs(radians * 180.0 / math.pi)
        
        if angle > 180.0:
            angle = 360.0 - angle
            
        return round(angle, 1)

    @classmethod
    def get_body_angles(cls, landmarks):
        """
        Extracts specific joints and calculates vital angles for posture analysis.
        """
        angles = {}
        if not landmarks:
            return angles

        # Helper function to safely calculate angle only if all 3 points exist
        def calc_if_exists(p1_idx, p2_idx, p3_idx):
            if p1_idx in landmarks and p2_idx in landmarks and p3_idx in landmarks:
                return cls.calculate_2d_angle(landmarks[p1_idx], landmarks[p2_idx], landmarks[p3_idx])
            return None

        # --- Knees ---
        r_knee = calc_if_exists(cls.KP['r_hip'], cls.KP['r_knee'], cls.KP['r_ankle'])
        if r_knee is not None: angles['right_knee'] = r_knee
            
        l_knee = calc_if_exists(cls.KP['l_hip'], cls.KP['l_knee'], cls.KP['l_ankle'])
        if l_knee is not None: angles['left_knee'] = l_knee

        # --- Elbows ---
        r_elbow = calc_if_exists(cls.KP['r_shoulder'], cls.KP['r_elbow'], cls.KP['r_wrist'])
        if r_elbow is not None: angles['right_elbow'] = r_elbow

        l_elbow = calc_if_exists(cls.KP['l_shoulder'], cls.KP['l_elbow'], cls.KP['l_wrist'])
        if l_elbow is not None: angles['left_elbow'] = l_elbow

        # --- Arm to Body Alignment (Are hands close to the body?) ---
        r_arm_body = calc_if_exists(cls.KP['r_hip'], cls.KP['r_shoulder'], cls.KP['r_elbow'])
        if r_arm_body is not None: angles['right_arm_body'] = r_arm_body

        l_arm_body = calc_if_exists(cls.KP['l_hip'], cls.KP['l_shoulder'], cls.KP['l_elbow'])
        if l_arm_body is not None: angles['left_arm_body'] = l_arm_body

        # --- Spine (Relative to virtual vertical line) ---
        # Try right side first
        if cls.KP['r_shoulder'] in landmarks and cls.KP['r_hip'] in landmarks:
            shoulder = landmarks[cls.KP['r_shoulder']]
            hip = landmarks[cls.KP['r_hip']]
            vertical_ref = type('Point', (), {'x': hip.x, 'y': hip.y - 50.0})()
            angles['spine'] = cls.calculate_2d_angle(shoulder, hip, vertical_ref)
        # Fallback to left side if right side is hidden
        elif cls.KP['l_shoulder'] in landmarks and cls.KP['l_hip'] in landmarks:
            shoulder = landmarks[cls.KP['l_shoulder']]
            hip = landmarks[cls.KP['l_hip']]
            vertical_ref = type('Point', (), {'x': hip.x, 'y': hip.y - 50.0})()
            angles['spine'] = cls.calculate_2d_angle(shoulder, hip, vertical_ref)

        return angles