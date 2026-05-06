class LabelBuilder:

    def __init__(self, mode="clean"):
        self.mode = mode  # "clean", "debug", "minimal"

    def build(self, tracker_id, zone=None, speed=None, violations=None):

        label = f"#{tracker_id}"

        # show speed cleanly
        if speed is not None:
            label += f" | {int(speed)} km/h"

        return label