class BaseAccidentEngine:

    def detect(self, detections, trajectories, zone_logic):
        """
        Should return list of accident events
        """
        raise NotImplementedError