class FrameSerializer:

    @staticmethod
    def serialize(frame_data):

        return {

            # =============================================
            # FRAME INFO
            # =============================================
            "frame_number":
                frame_data.frame_number,

            "timestamp":
                frame_data.timestamp,

            "fps":
                frame_data.fps,

            # =============================================
            # TRACKING
            # =============================================
            "tracked_objects":
                frame_data.tracked_objects,

            # =============================================
            # SPATIAL
            # =============================================
            "zones":
                frame_data.zones,

            "world_positions":
                frame_data.world_positions,

            # =============================================
            # ANALYTICS
            # =============================================
            "speeds":
                frame_data.speeds,

            "counts":
                frame_data.metadata.get(
                    "counts",
                    {}
                ),

            # =============================================
            # EVENTS / VIOLATIONS
            # =============================================
            "violations":
                frame_data.violations,

            "events":
                frame_data.events,

            # =============================================
            # ENGINES
            # =============================================
            "engines":
                frame_data.engines,

            # =============================================
            # EXTRA METADATA
            # =============================================
            "metadata":
                frame_data.metadata
        }