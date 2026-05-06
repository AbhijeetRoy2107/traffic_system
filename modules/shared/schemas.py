from dataclasses import (
    dataclass,
    field,
    asdict
)

from typing import (
    Dict,
    List,
    Any,
    Optional
)

import time
import uuid


# =========================================================
# EVENT SEVERITY
# =========================================================
class EventSeverity:

    INFO = "info"

    WARNING = "warning"

    CRITICAL = "critical"


# =========================================================
# EVENT TYPES
# =========================================================
class EventType:

    # =====================================================
    # ANALYTICS
    # =====================================================
    CONGESTION = "CONGESTION"

    # =====================================================
    # VIOLATIONS
    # =====================================================
    OVERSPEED = "OVERSPEED"

    WRONG_WAY = "WRONG_WAY"

    # =====================================================
    # ENGINES
    # =====================================================
    POSSIBLE_ACCIDENT = (
        "POSSIBLE_ACCIDENT"
    )

    EMERGENCY_VEHICLE = (
        "EMERGENCY_VEHICLE"
    )

    BLACKLISTED_PLATE = (
        "BLACKLISTED_PLATE"
    )


# =========================================================
# EVENT SEVERITY MAP
# =========================================================
EVENT_SEVERITY_MAP = {

    # =====================================================
    # ANALYTICS
    # =====================================================
    EventType.CONGESTION:
        EventSeverity.WARNING,

    # =====================================================
    # VIOLATIONS
    # =====================================================
    EventType.OVERSPEED:
        EventSeverity.WARNING,

    EventType.WRONG_WAY:
        EventSeverity.CRITICAL,

    # =====================================================
    # ENGINES
    # =====================================================
    EventType.POSSIBLE_ACCIDENT:
        EventSeverity.CRITICAL,

    EventType.EMERGENCY_VEHICLE:
        EventSeverity.CRITICAL,

    EventType.BLACKLISTED_PLATE:
        EventSeverity.CRITICAL
}


# =========================================================
# GET EVENT SEVERITY
# =========================================================
def get_event_severity(

    event_type: str
):

    return EVENT_SEVERITY_MAP.get(

        event_type,

        EventSeverity.INFO
    )


# =========================================================
# BASE EVENT SCHEMA
# =========================================================
@dataclass
class EventSchema:

    # =====================================================
    # CORE
    # =====================================================
    event_id: str

    event_type: str

    timestamp: float

    severity: str

    # =====================================================
    # TRACKING
    # =====================================================
    tracker_ids: List[int]

    # =====================================================
    # SPATIAL
    # =====================================================
    zone: Optional[str] = None

    camera_id: Optional[str] = None

    # =====================================================
    # ENGINE / ANALYTICS
    # =====================================================
    source: Optional[str] = None

    confidence: Optional[float] = None

    # =====================================================
    # MEDIA / EVIDENCE
    # =====================================================
    snapshot_path: Optional[str] = None

    crop_path: Optional[str] = None

    # =====================================================
    # EXTRA
    # =====================================================
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # SERIALIZATION
    # =====================================================
    def to_dict(self):

        return asdict(self)


# =========================================================
# EVENT FACTORY
# =========================================================
def create_event(

    event_type: str,

    tracker_ids: List[int],

    zone: Optional[str] = None,

    camera_id: Optional[str] = None,

    source: Optional[str] = None,

    confidence: Optional[float] = None,

    snapshot_path: Optional[str] = None,

    crop_path: Optional[str] = None,

    metadata: Optional[
        Dict[str, Any]
    ] = None
):

    return EventSchema(

        # =================================================
        # CORE
        # =================================================
        event_id=str(uuid.uuid4()),

        event_type=event_type,

        timestamp=time.time(),

        severity=get_event_severity(
            event_type
        ),

        # =================================================
        # TRACKING
        # =================================================
        tracker_ids=tracker_ids,

        # =================================================
        # SPATIAL
        # =================================================
        zone=zone,

        camera_id=camera_id,

        # =================================================
        # ENGINE / ANALYTICS
        # =================================================
        source=source,

        confidence=confidence,

        # =================================================
        # MEDIA
        # =================================================
        snapshot_path=snapshot_path,

        crop_path=crop_path,

        # =================================================
        # EXTRA
        # =================================================
        metadata=metadata or {}
    )