from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class FrameData:

    # =====================================================
    # FRAME INFO
    # =====================================================
    frame_number: int = 0

    timestamp: float = 0.0

    fps: float = 0.0

    # =====================================================
    # RAW DETECTIONS
    # =====================================================
    detections: List[Any] = field(
        default_factory=list
    )

    # =====================================================
    # TRACKED OBJECTS
    # =====================================================
    tracked_objects: List[dict] = field(
        default_factory=list
    )

    # =====================================================
    # SPATIAL
    # =====================================================
    zones: Dict[int, str] = field(
        default_factory=dict
    )

    world_positions: Dict[int, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # ANALYTICS
    # =====================================================
    speeds: Dict[int, float] = field(
        default_factory=dict
    )

    counts: Dict[str, int] = field(
        default_factory=dict
    )

    lane_statistics: Dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # EVENTS / VIOLATIONS
    # =====================================================
    violations: List[dict] = field(
        default_factory=list
    )

    events: List[dict] = field(
        default_factory=list
    )

    # =====================================================
    # OPTIONAL ENGINES
    # =====================================================
    emergency_vehicles: List[dict] = field(
        default_factory=list
    )

    anpr_results: List[dict] = field(
        default_factory=list
    )

    accidents: List[dict] = field(
        default_factory=list
    )

    # =====================================================
    # ENGINE OUTPUTS
    # =====================================================
    engines: Dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # VISUALIZATION
    # =====================================================
    bird_eye_objects: List[dict] = field(
        default_factory=list
    )

    # =====================================================
    # EXTRA
    # =====================================================
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )
    
    # =====================================================
    # ENGINE OUTPUTS
    # =====================================================
    engines: Dict[str, Any] = field(
        default_factory=dict
    )