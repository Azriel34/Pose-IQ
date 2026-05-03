class PostureRules:
    def __init__(self):
        # Define sensitivity thresholds for posture alerts
        self.thresholds = {
            'spine_max_lean': 45.0,  
            'spine_warning': 20.0,   
            'knee_min_angle': 70.0,
            'arm_max_away': 45.0     
        }
        
        # State management (Debouncing) - counts consecutive frames with errors
        self.violation_counters = {
            'spine_high': 0,
            'spine_low': 0,
            'right_knee': 0,
            'left_knee': 0,
            'right_arm_body': 0,
            'left_arm_body': 0
        }
        self.FRAMES_TO_ALERT = 10 

    def is_starting_pose(self, angles):
        if not angles:
            return False

        # Check only the angles that the camera actually sees in the current frame
        spine = angles.get('spine')
        if spine is not None and spine > 15.0:
            return False

        # If any arm is visible and far from the body, it's not a starting pose
        for side in ['right_arm_body', 'left_arm_body']:
            arm_angle = angles.get(side)
            if arm_angle is not None and arm_angle > 20.0:
                return False

        # Same logic for knees - if a knee is visible, it must be straight
        for side in ['right_knee', 'left_knee']:
            knee_angle = angles.get(side)
            if knee_angle is not None and knee_angle < 160.0:
                return False

        # Safety check: Must see at least some body parts to confirm "ready" state
        if spine is None and 'right_knee' not in angles and 'left_knee' not in angles:
            return False

        return True

    def analyze_posture(self, angles):
        issues = []
        if not angles:
            return issues

        # --- Rule 1: Spine Check (with debouncing) ---
        spine_angle = angles.get('spine')
        if spine_angle is not None:
            if spine_angle > self.thresholds['spine_max_lean']:
                self.violation_counters['spine_high'] += 1
                self.violation_counters['spine_low'] = 0 
                
                if self.violation_counters['spine_high'] >= self.FRAMES_TO_ALERT:
                    issues.append({'joint': 'spine', 'severity': 'high', 'message': 'Keep back straight!'})
            
            elif spine_angle > self.thresholds['spine_warning']:
                self.violation_counters['spine_low'] += 1
                self.violation_counters['spine_high'] = 0 
                
                if self.violation_counters['spine_low'] >= self.FRAMES_TO_ALERT:
                    issues.append({'joint': 'spine', 'severity': 'low', 'message': 'Careful with your back'})
            else:
                self.violation_counters['spine_high'] = 0
                self.violation_counters['spine_low'] = 0

        # --- Rule 2: Knees Check ---
        for side in ['right_knee', 'left_knee']:
            knee_angle = angles.get(side)
            if knee_angle is not None:
                if knee_angle < self.thresholds['knee_min_angle']:
                    self.violation_counters[side] += 1
                    if self.violation_counters[side] >= self.FRAMES_TO_ALERT:
                        issues.append({'joint': side, 'severity': 'medium', 'message': f"Don't bend {side.replace('_', ' ')} too deep"})
                else:
                    self.violation_counters[side] = 0

        # --- Rule 3: Arms Check ---
        for side in ['right_arm_body', 'left_arm_body']:
            arm_angle = angles.get(side)
            if arm_angle is not None:
                if arm_angle > self.thresholds['arm_max_away']:
                    self.violation_counters[side] += 1
                    if self.violation_counters[side] >= self.FRAMES_TO_ALERT:
                        side_name = 'Right' if 'right' in side else 'Left'
                        issues.append({'joint': side, 'severity': 'low', 'message': f"Keep {side_name} arm closer to body"})
                else:
                    self.violation_counters[side] = 0

        return issues