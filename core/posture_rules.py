class PostureRules:
    def __init__(self):
        # ריכוך מסיבי של כל הזוויות כדי לאפשר עמידה טבעית ונוחה מול המצלמה
        self.thresholds = {
            'spine_max_lean': 45.0,  
            'spine_warning': 30.0,   
            # ברכיים מאפשרות כיפוף משמעותי מאוד
            'knee_min_angle': 120.0, 
            # הידיים יכולות להיות רחוקות מהגוף עד 65 מעלות
            'arm_max_away': 65.0,
            # מרפקים מקבלים אישור להיות מכופפים מאוד (עד זווית של 110)
            'elbow_min_angle': 110.0,
            # פיסוק רחב במיוחד
            'legs_max_spread': 90.0
        }
        
        self.violation_counters = {
            'spine_high': 0, 'spine_low': 0,
            'right_knee': 0, 'left_knee': 0,
            'right_arm_body': 0, 'left_arm_body': 0,
            'right_elbow': 0, 'left_elbow': 0,
            'legs_spread': 0
        }
        self.FRAMES_TO_ALERT = 10 

    def is_starting_pose(self, angles):
        if not angles: return False

        # שימוש בספים הסלחניים שהגדרנו למעלה גם עבור תנוחת המוצא
        spine = angles.get('spine')
        if spine is not None and spine > self.thresholds['spine_warning']: return False

        for side in ['right_arm_body', 'left_arm_body']:
            arm_angle = angles.get(side)
            if arm_angle is not None and arm_angle > self.thresholds['arm_max_away']: return False

        for side in ['right_elbow', 'left_elbow']:
            elbow_angle = angles.get(side)
            if elbow_angle is not None and elbow_angle < self.thresholds['elbow_min_angle']: return False

        for side in ['right_knee', 'left_knee']:
            knee_angle = angles.get(side)
            if knee_angle is not None and knee_angle < self.thresholds['knee_min_angle']: return False

        legs_spread = angles.get('legs_spread')
        if legs_spread is not None and legs_spread > self.thresholds['legs_max_spread']: return False

        # וידוא שקיימים נתונים בסיסיים
        if spine is None and 'right_knee' not in angles and 'left_knee' not in angles: return False

        return True

    def analyze_posture(self, angles):
        issues = []
        if not angles: return issues

        # --- Rule 1: Spine Check ---
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

        # --- Rule 4: Elbows Check ---
        for side in ['right_elbow', 'left_elbow']:
            elbow_angle = angles.get(side)
            if elbow_angle is not None:
                if elbow_angle < self.thresholds['elbow_min_angle']:
                    self.violation_counters[side] += 1
                    if self.violation_counters[side] >= self.FRAMES_TO_ALERT:
                        side_name = 'Right' if 'right' in side else 'Left'
                        issues.append({'joint': side, 'severity': 'medium', 'message': f"Straighten {side_name} elbow!"})
                else:
                    self.violation_counters[side] = 0

        # --- Rule 5: Legs Spread Check ---
        legs_spread = angles.get('legs_spread')
        if legs_spread is not None:
            if legs_spread > self.thresholds['legs_max_spread']:
                self.violation_counters['legs_spread'] += 1
                if self.violation_counters['legs_spread'] >= self.FRAMES_TO_ALERT:
                    issues.append({'joint': 'legs_spread', 'severity': 'medium', 'message': "Bring legs closer together!"})
            else:
                self.violation_counters['legs_spread'] = 0

        return issues