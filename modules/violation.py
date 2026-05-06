class ViolationDetector:

    def __init__(self, speed_threshold=50):
        self.speed_threshold = speed_threshold

        # to avoid repeated alerts
        self.triggered = set()

    def check(self, tracker_id, zone, speed):

        violations = []

        key = (tracker_id, zone)

        # 1. Sidewalk violation
        if zone == "sidewalk":
            if key not in self.triggered:
                violations.append("SIDEWALK")
                self.triggered.add(key)

        # 2. Speed violation
        if zone == "speed_zone" and speed is not None:
            if speed > self.speed_threshold:
                violations.append("OVERSPEED")

        return violations