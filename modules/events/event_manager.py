import time

from modules.shared.schemas import (
    create_event
)


class EventManager:

    def __init__(self, cooldown=2.0):
        """
        cooldown: seconds before same event
        can trigger again
        """

        self.cooldown = cooldown

        # =================================================
        # EVENT MEMORY
        # =================================================
        # (tracker_id, event_type) -> last_trigger_time
        self.last_events = {}

        # =================================================
        # STORED EVENTS
        # =================================================
        self.events = []

    # =====================================================
    # UPDATE
    # =====================================================
    def update(

        self,

        tracker_id,

        violations,

        zone
    ):
        """
        Process violations and generate events
        """

        current_time = time.time()

        new_events = []

        for v in violations:

            key = (tracker_id, v)

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

                event_type=v,

                tracker_ids=[tracker_id],

                zone=zone,

                severity="warning"
            )

            # =============================================
            # STORE
            # =============================================
            self.events.append(
                event.__dict__
            )

            self.last_events[
                key
            ] = current_time

            new_events.append(
                event.__dict__
            )

        return new_events

    # =====================================================
    # GET EVENTS
    # =====================================================
    def get_events(self):

        return self.events

    # =====================================================
    # CLEAR
    # =====================================================
    def clear(self):

        self.events = []