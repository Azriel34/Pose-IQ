class PostureRules:
    def __init__(self):
        # Task: define rule thresholds
        # Define sensitivity thresholds for posture alerts
        self.thresholds = {
            'spine_max_lean': 45.0,  # Maximum forward lean angle before a severe warning
            'spine_warning': 35.0,   # Warning zone (early signs of bad posture or bending)
            'knee_min_angle': 70.0   # Too sharp of a knee bend, indicating potential strain
        }

    def analyze_posture(self, angles):
        """
        Task: implement PostureRules & detect violations
        Receives angles from the calculator and returns a list of detected posture issues (if any).
        """
        issues = []
        
        if not angles:
            return issues

        # --- Rule 1: Spine Posture Check ---
        # In our calculation (Shoulder -> Hip -> Vertical reference), 0 degrees is perfectly upright.
        # As the angle increases, the person is leaning further forward.
        spine_angle = angles.get('spine')
        if spine_angle is not None:
            if spine_angle > self.thresholds['spine_max_lean']:
                issues.append({
                    'joint': 'spine',
                    'severity': 'high',
                    'message': 'Keep back straight!'
                })
            elif spine_angle > self.thresholds['spine_warning']:
                # Task: add severity levels
                issues.append({
                    'joint': 'spine',
                    'severity': 'low',
                    'message': 'Careful with your back'
                })

        # --- Rule 2: Knee Posture Check ---
        knee_angle = angles.get('knee')
        if knee_angle is not None:
            if knee_angle < self.thresholds['knee_min_angle']:
                issues.append({
                    'joint': 'knee',
                    'severity': 'medium',
                    'message': 'Don\'t bend knee too deep'
                })

        return issues