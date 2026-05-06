import time

from modules.shared.schemas import (

    create_event
)


# =========================================================
# EVENT MANAGER
# =========================================================
class EventManager:

    def __init__(

        self,

        cooldown=2.0
    ):

        """
        cooldown:
        seconds before same event
        can trigger again
        """

        self.cooldown = cooldown

        # =================================================
        # EVENT MEMORY
        # =================================================
        # (tracker_id, event_type)
        # -> last trigger time
        self.last_events = {}

        # =================================================
        # EVENT STORAGE
        # =================================================
        self.events = []

    # =====================================================
    # UPDATE
    # =====================================================
    def update(

        self,

        tracker_id,

        violations,

        zone,

        source="rule_engine",

        confidence=None,

        metadata=None
    ):

        current_time = time.time()

        new_events = []

        for event_type in violations:

            key = (

                tracker_id,

                event_type
            )

            last_time = self.last_events.get(

                key,

                0
            )

            # =============================================
            # COOLDOWN CHECK
            # =============================================
            if (

                current_time - last_time
                < self.cooldown
            ):

                continue

            # =============================================
            # CREATE EVENT
            # =============================================
            event = create_event(

                event_type=event_type,

                tracker_ids=[tracker_id],

                zone=zone,

                source=source,

                confidence=confidence,

                metadata=metadata
            )

            event_dict = event.to_dict()

            # =============================================
            # STORE
            # =============================================
            self.events.append(
                event_dict
            )

            self.last_events[
                key
            ] = current_time

            new_events.append(
                event_dict
            )

        return new_events

    # =====================================================
    # GET EVENTS
    # =====================================================
    def get_events(self):

        return self.events

    # =====================================================
    # CLEAR EVENTS
    # =====================================================
    def clear(self):

        self.events = []