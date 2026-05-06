# tools/roi_selector.py

import cv2
import json
import os
import numpy as np


# =========================================================
# PATHS
# =========================================================
ROI_FILE = "roi/roi_data.json"
HOMO_FILE = "homography/homography_data.json"

os.makedirs("roi", exist_ok=True)
os.makedirs("homography", exist_ok=True)


# =========================================================
# SCREEN SETTINGS
# =========================================================
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

MARGIN_X = 100
MARGIN_Y = 150

MAX_WIDTH = SCREEN_WIDTH - MARGIN_X
MAX_HEIGHT = SCREEN_HEIGHT - MARGIN_Y


# =========================================================
# GLOBAL STATE
# =========================================================
current_points = []
homography_points = []

all_rois = []
all_homographies = []

scale = 1.0
display_frame = None

mode = "roi"  # roi | homo


# =========================================================
# RESIZE FRAME
# =========================================================
def resize_to_screen(frame):

    h, w = frame.shape[:2]

    scale = min(
        MAX_WIDTH / w,
        MAX_HEIGHT / h
    )

    if scale >= 1:
        return frame.copy(), 1.0

    new_w = int(w * scale)
    new_h = int(h * scale)

    resized = cv2.resize(
        frame,
        (new_w, new_h)
    )

    return resized, scale


# =========================================================
# JSON HELPERS
# =========================================================
def load_json(path):

    if os.path.exists(path):

        with open(path, "r") as f:
            return json.load(f)

    return {}


def save_json(path, data):

    with open(path, "w") as f:
        json.dump(data, f, indent=4)


# =========================================================
# MOUSE CLICK
# =========================================================
def click_event(event, x, y, flags, param):

    global current_points
    global homography_points
    global scale
    global mode

    if event == cv2.EVENT_LBUTTONDOWN:

        orig_x = int(x / scale)
        orig_y = int(y / scale)

        # =================================================
        # ROI MODE
        # =================================================
        if mode == "roi":

            current_points.append(
                (orig_x, orig_y)
            )

        # =================================================
        # HOMOGRAPHY MODE
        # =================================================
        elif mode == "homo":

            if len(homography_points) < 4:

                homography_points.append(
                    (orig_x, orig_y)
                )

                print(
                    f"Homography point "
                    f"{len(homography_points)}: "
                    f"{(orig_x, orig_y)}"
                )


# =========================================================
# DRAW UI
# =========================================================
def draw(frame):

    temp = frame.copy()

    # =====================================================
    # DRAW SAVED ROIS
    # =====================================================
    for roi in all_rois:

        pts = np.array([
            (
                int(x * scale),
                int(y * scale)
            )
            for x, y in roi["points"]
        ])

        cv2.polylines(
            temp,
            [pts],
            True,
            (255, 0, 0),
            2
        )

        x, y = pts[0]

        cv2.putText(
            temp,
            roi["label"],
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

    # =====================================================
    # DRAW CURRENT ROI
    # =====================================================
    scaled_current = [
        (
            int(x * scale),
            int(y * scale)
        )
        for x, y in current_points
    ]

    for p in scaled_current:

        cv2.circle(
            temp,
            p,
            5,
            (0, 0, 255),
            -1
        )

    # =====================================================
    # CLOSED ROI POLYGON
    # =====================================================
    if len(scaled_current) > 1:

        cv2.polylines(
            temp,
            [np.array(scaled_current)],
            True,
            (0, 255, 0),
            2
        )

    # =====================================================
    # DRAW HOMOGRAPHY POINTS
    # =====================================================
    for i, (x, y) in enumerate(
        homography_points
    ):

        px = int(x * scale)
        py = int(y * scale)

        cv2.circle(
            temp,
            (px, py),
            6,
            (0, 255, 255),
            -1
        )

        cv2.putText(
            temp,
            str(i + 1),
            (px + 5, py - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            2
        )

    # =====================================================
    # DRAW HOMOGRAPHY SHAPE
    # =====================================================
    if len(homography_points) > 1:

        homo_pts = np.array([
            (
                int(x * scale),
                int(y * scale)
            )
            for x, y in homography_points
        ])

        cv2.polylines(
            temp,
            [homo_pts],
            len(homography_points) == 4,
            (0, 255, 255),
            2
        )

    # =====================================================
    # INFO
    # =====================================================
    cv2.putText(
        temp,
        f"MODE: {mode.upper()}",
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )

    cv2.putText(
        temp,
        f"ROIs: {len(all_rois)}",
        (10, 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 0),
        2
    )

    cv2.putText(
        temp,
        f"Homographies: {len(all_homographies)}",
        (10, 85),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 0),
        2
    )

    cv2.putText(
        temp,
        f"HomoPts: {len(homography_points)}/4",
        (10, 115),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 0),
        2
    )

    # =====================================================
    # CONTROLS
    # =====================================================
    controls = [
        "Click = add point",
        "u = undo",
        "r = reset current",
        "n = finalize ROI",
        "m = finalize homography",
        "h = switch ROI/HOMO",
        "s = save all",
        "q = quit"
    ]

    y = 160

    for text in controls:

        cv2.putText(
            temp,
            text,
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        y += 30

    return temp


# =========================================================
# MAIN
# =========================================================
def main():

    global current_points
    global homography_points
    global all_rois
    global all_homographies
    global scale
    global display_frame
    global mode

    # =====================================================
    # VIDEO
    # =====================================================
    video_path = input(
        "Enter video path: "
    ).strip()

    filename = os.path.basename(
        video_path
    )

    cap = cv2.VideoCapture(
        video_path
    )

    ret, frame = cap.read()

    cap.release()

    if not ret:

        print("Error reading video")
        return

    display_frame, scale = resize_to_screen(
        frame
    )

    # =====================================================
    # WINDOW
    # =====================================================
    cv2.namedWindow(
        "ROI + Homography Tool"
    )

    cv2.setMouseCallback(
        "ROI + Homography Tool",
        click_event
    )

    # =====================================================
    # LOOP
    # =====================================================
    while True:

        display = draw(display_frame)

        cv2.imshow(
            "ROI + Homography Tool",
            display
        )

        key = cv2.waitKey(1)

        # =================================================
        # UNDO
        # =================================================
        if key == ord("u"):

            if mode == "roi":

                if current_points:
                    current_points.pop()

            elif mode == "homo":

                if homography_points:
                    homography_points.pop()

        # =================================================
        # RESET CURRENT
        # =================================================
        elif key == ord("r"):

            if mode == "roi":
                current_points = []

            elif mode == "homo":
                homography_points = []

        # =================================================
        # FINALIZE ROI
        # =================================================
        elif key == ord("n"):

            if len(current_points) >= 3:

                label = input(
                    "Enter ROI label: "
                ).strip()

                all_rois.append({

                    "label": label,

                    "points": current_points.copy()
                })

                current_points = []

                print(
                    f"ROI '{label}' added"
                )

            else:

                print(
                    "Need at least 3 points"
                )

        # =================================================
        # FINALIZE HOMOGRAPHY
        # =================================================
        elif key == ord("m"):

            if len(homography_points) != 4:

                print(
                    "Need exactly 4 points"
                )

                continue

            print("\nPoint order must be:")
            print("1 = top-left")
            print("2 = top-right")
            print("3 = bottom-left")
            print("4 = bottom-right\n")

            label = input(
                "Enter homography label: "
            ).strip()

            width = float(
                input(
                    "Enter real width (meters): "
                )
            )

            height = float(
                input(
                    "Enter real length (meters): "
                )
            )

            all_homographies.append({

                "label": label,

                "src": homography_points.copy(),

                "dst": [
                    [0, 0],
                    [width, 0],
                    [0, height],
                    [width, height]
                ]
            })

            print(
                f"Homography '{label}' added"
            )

            # reset for next homography
            homography_points = []

        # =================================================
        # SWITCH MODE
        # =================================================
        elif key == ord("h"):

            mode = (
                "homo"
                if mode == "roi"
                else "roi"
            )

            print(
                "Switched to:",
                mode
            )

        # =================================================
        # SAVE
        # =================================================
        elif key == ord("s"):

            # =============================================
            # SAVE ROIS
            # =============================================
            roi_data = load_json(
                ROI_FILE
            )

            roi_data[filename] = all_rois

            save_json(
                ROI_FILE,
                roi_data
            )

            # =============================================
            # SAVE HOMOGRAPHIES
            # =============================================
            homo_data = load_json(
                HOMO_FILE
            )

            homo_data[filename] = (
                all_homographies
            )

            save_json(
                HOMO_FILE,
                homo_data
            )

            print(
                "All ROI + homography data saved"
            )

        # =================================================
        # EXIT
        # =================================================
        elif key == ord("q"):

            print("Exiting tool")
            break

    cv2.destroyAllWindows()


# =========================================================
# ENTRY
# =========================================================
if __name__ == "__main__":
    main()