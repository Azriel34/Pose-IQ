class PostureRules:
    def __init__(self):
        # Define sensitivity thresholds for posture alerts
        self.thresholds = {
            'spine_max_lean': 45.0,  
            'spine_warning': 30.0,   
            'knee_min_angle': 70.0,
            # סף חדש: אם היד מתרחקת יותר מ-45 מעלות מהגוף בזמן תנועה
            'arm_max_away': 45.0     
        }

    def is_starting_pose(self, angles):
        """
        Checks if the user is in a 'Ready' state:
        Straight back, straight legs, and arms close to the body.
        """
        if not angles:
            return False

        spine = angles.get('spine', 90.0)
        is_spine_straight = spine < 15.0

        r_arm = angles.get('right_arm_body', 90.0)
        l_arm = angles.get('left_arm_body', 90.0)
        are_arms_close = min(r_arm, l_arm) < 20.0 

        r_knee = angles.get('right_knee', 0.0)
        l_knee = angles.get('left_knee', 0.0)
        is_knee_straight = max(r_knee, l_knee) > 160.0

        return is_spine_straight and are_arms_close and is_knee_straight

    def analyze_posture(self, angles):
        issues = []
        if not angles:
            return issues

        # --- חוק 0: בדיקת עמידת מוצא (חדש!) ---
        # אם המשתמש לא בעמידת מוצא, זה כשלעצמו נושא לתיקון
        if not self.is_starting_pose(angles):
            issues.append({
                'joint': 'general', 
                'severity': 'medium', 
                'message': 'Return to starting position'
            })

        # --- Rule 1: Spine Check ---
        spine_angle = angles.get('spine')
        # ... (שאר הלוגיקה של הגב נשארת כאן) ...
        if spine_angle is not None:
            if spine_angle > self.thresholds['spine_max_lean']:
                issues.append({'joint': 'spine', 'severity': 'high', 'message': 'Keep back straight!'})
            elif spine_angle > self.thresholds['spine_warning']:
                issues.append({'joint': 'spine', 'severity': 'low', 'message': 'Careful with your back'})

        # --- Rule 2: Knees Check ---
        # ... (שאר הלוגיקה של הברכיים) ...
        for side in ['right_knee', 'left_knee']:
            knee_angle = angles.get(side)
            if knee_angle is not None and knee_angle < self.thresholds['knee_min_angle']:
                issues.append({'joint': side, 'severity': 'medium', 'message': f"Don't bend {side.replace('_', ' ')} too deep"})

        # --- Rule 3: Arms Check ---
        # ... (שאר הלוגיקה של הידיים) ...
        for side in ['right_arm_body', 'left_arm_body']:
            arm_angle = angles.get(side)
            if arm_angle is not None and arm_angle > self.thresholds['arm_max_away']:
                side_name = 'Right' if 'right' in side else 'Left'
                issues.append({'joint': side, 'severity': 'low', 'message': f"Keep {side_name} arm closer to body"})

        return issues