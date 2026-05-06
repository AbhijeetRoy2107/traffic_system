from dataclasses import dataclass, field

from typing import Dict, List, Any

import time
import uuid


# =========================================================
# EVENT SCHEMA
# =========================================================
@dataclass
class EventSchema:

    event_id: str

    event_type: str

    timestamp: float

    tracker_ids: List[int]

    zone: str | None = None

    severity: str = "info"

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# =========================================================
# EVENT FACTORY
# =========================================================
def create_event(

    event_type: str,

    tracker_ids: List[int],

    zone: str | None = None,

    severity: str = "info",

    metadata: Dict[str, Any] | None = None
):

    return EventSchema(

        event_id=str(uuid.uuid4()),

        event_type=event_type,

        timestamp=time.time(),

        tracker_ids=tracker_ids,

        zone=zone,

        severity=severity,

        metadata=metadata or {}
    )