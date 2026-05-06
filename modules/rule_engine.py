import json
import os

# Map YOLO class IDs → names (COCO)
CLASS_ID_TO_NAME = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}


class RuleEngine:
    def __init__(self, rules_path="config/rules.json"):
        self.rules = self._load_rules(rules_path)

    def _load_rules(self, path):
        if not os.path.exists(path):
            return {"zones": {}}
        with open(path, "r") as f:
            return json.load(f)

    def get_class_name(self, class_id):
        return CLASS_ID_TO_NAME.get(int(class_id), "unknown")

    def check(self, tracker_id, class_id, zone, speed):
        """
        Returns list of violations for this object
        """
        violations = []
        class_name = self.get_class_name(class_id)

        zone_rules = self.rules.get("zones", {}).get(zone, {})

        # --- Zone class rules ---
        allowed = zone_rules.get("allowed_classes", [])
        disallowed = zone_rules.get("violation_classes", [])

        if disallowed and class_name in disallowed:
            violations.append(f"{class_name.upper()}_IN_{zone.upper()}")

        if allowed and class_name not in allowed:
            violations.append(f"{class_name.upper()}_NOT_ALLOWED_IN_{zone.upper()}")

        # --- Speed rules ---
        max_speed = zone_rules.get("max_speed", None)
        if max_speed is not None and speed is not None:
            if speed > max_speed:
                violations.append("OVERSPEED")

        return violations