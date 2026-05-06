class FrameSerializer:

    @staticmethod
    def serialize(frame_data):

        return {

            "frame_number":
                frame_data.frame_number,

            "timestamp":
                frame_data.timestamp,

            "zones":
                frame_data.zones,

            "speeds":
                frame_data.speeds,

            "violations":
                frame_data.violations,

            "events":
                frame_data.events,

            "engines":
                frame_data.engines,

            "counts":
                frame_data.metadata.get(
                    "counts",
                    {}
                )
        }