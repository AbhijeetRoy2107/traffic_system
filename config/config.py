# =====================================================
# MODEL
# =====================================================

MODEL_PATH = "yolov8s.pt"

DEVICE = "cuda"

IMG_SIZE = 960


# =====================================================
# DETECTION
# =====================================================

CONFIDENCE_THRESHOLD = 0.3

IOU_THRESHOLD = 0.5

# COCO classes
# 0 = person
# 1 = bicycle
# 2 = car
# 3 = motorcycle
# 5 = bus
# 7 = truck
ALLOWED_CLASSES = [
    0,
    1,
    2,
    3,
    5,
    7
]


# =====================================================
# TRACKING
# =====================================================

TRACK_BUFFER = 30

TRACK_MATCH_THRESHOLD = 0.8


# =====================================================
# TRAJECTORY
# =====================================================

MAX_TRAJECTORY_POINTS = 30


# =====================================================
# SPEED ESTIMATION
# =====================================================

SPEED_ENABLED = True

DEFAULT_SPEED_LIMIT = 80

# larger window = smoother speed
SPEED_WINDOW_SIZE = 10

# EMA smoothing factor
SPEED_SMOOTHING_ALPHA = 0.3

# ignore tiny motion jitter
MIN_MOVEMENT_DISTANCE = 0.5

# clamp unrealistic spikes
MAX_REASONABLE_SPEED = 220


# =====================================================
# BIRD-EYE VIEW
# =====================================================

BIRD_EYE_ENABLED = True

BIRD_EYE_WIDTH = 1200

BIRD_EYE_HEIGHT = 900

BIRD_EYE_SCALE = 30

BIRD_EYE_OFFSET_X = 300

BIRD_EYE_OFFSET_Y = 100


# =====================================================
# ACCIDENT ENGINE
# =====================================================

ACCIDENT_DETECTION_ENABLED = True


# =====================================================
# EMERGENCY VEHICLES
# =====================================================

EMERGENCY_VEHICLE_ENABLED = False

EMERGENCY_CLASSES = [
    "ambulance",
    "police",
    "fire_truck"
]


# =====================================================
# ANPR
# =====================================================

ANPR_ENABLED = False

ANPR_OCR_ENGINE = "paddle"


# =====================================================
# OUTPUTS
# =====================================================

SAVE_OUTPUT_VIDEO = True

SAVE_BIRD_EYE_VIDEO = True


# =====================================================
# FASTAPI / STREAMING
# =====================================================

API_ENABLED = False

API_HOST = "0.0.0.0"

API_PORT = 8000


# =========================================================
# FEATURE TOGGLES
# =========================================================

ENABLE_DETECTION = True

ENABLE_TRACKING = True

ENABLE_SPATIAL = True

ENABLE_ANALYTICS = True

ENABLE_COUNTING = True

ENABLE_VIOLATIONS = True

ENABLE_EVENTS = True

ENABLE_VISUALIZATION = True

ENABLE_BIRDEYE = True

ENABLE_ACCIDENT_ENGINE = True

ENABLE_SPEED_ESTIMATION = True

# =========================================================
# FUTURE FEATURES
# =========================================================

ENABLE_ANPR = False

ENABLE_EMERGENCY_VEHICLE = False

ENABLE_DATABASE = False

ENABLE_WEBSOCKET = False