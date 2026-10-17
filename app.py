
"""Streamlit dashboard for the Real-time Traffic Management System."""

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from traffic_management.traffic_processor import TrafficProcessor


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Real-time Traffic Management System",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚦 Real-time Traffic Management System")
st.caption(
    "YOLOv8 Vehicle Detection | Adaptive Traffic Signal Simulation"
)

st.write(
    "Upload a traffic image to detect vehicles, view detection details, "
    "and calculate demonstration signal timings."
)


# --------------------------------------------------
# Detection settings
# --------------------------------------------------

st.sidebar.header("Detection Settings")

confidence_threshold = st.sidebar.slider(
    "Minimum confidence",
    min_value=0.25,
    max_value=0.80,
    value=0.25,
    step=0.05,
    help=(
        "Higher values show fewer, more confident detections. "
        "The detector's base confidence is currently 0.25."
    ),
)

st.sidebar.caption(
    "This slider filters detections after YOLO inference. "
    "Lowering it below the detector's base threshold requires "
    "changing vehicle_detector.py as well."
)


# --------------------------------------------------
# Image upload
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload a traffic image",
    type=["jpg", "jpeg", "png"],
)

if uploaded_file is None:
    st.info("Upload a JPG, JPEG, or PNG image to get started.")
    st.stop()

try:
    image = Image.open(uploaded_file).convert("RGB")
except Exception as error:
    st.error(f"Could not open the uploaded image: {error}")
    st.stop()

st.subheader("Uploaded Traffic Image")
st.image(image, caption="Original image", use_container_width=True)


# --------------------------------------------------
# Run detection
# --------------------------------------------------

if st.button("Detect Vehicles and Calculate Signals", type="primary"):
    try:
        with st.spinner("Detecting vehicles and calculating signal timings..."):
            # Convert RGB image to OpenCV BGR format.
            frame = cv2.cvtColor(
                np.array(image),
                cv2.COLOR_RGB2BGR,
            )

            processor = TrafficProcessor()
            result = processor.process_image(frame)

            # Apply the selected display threshold.
            detections = [
                detection
                for detection in result["detections"]
                if detection["confidence"] >= confidence_threshold
            ]

            # Use the counts and timings returned by TrafficProcessor.
            # Recalculate vehicle counts using only detections above the slider threshold.
            counts = processor.detector.count_by_type(detections)
            timings = processor.signal_controller.calculate(
                north_south=sum(counts.values()),
                east_west=0,
            )

            # --------------------------------------------------
            # Draw clearer bounding boxes and labels
            # --------------------------------------------------

            annotated_frame = frame.copy()
            image_height, image_width = frame.shape[:2]

            for detection in detections:
                x1, y1, x2, y2 = detection["bbox"]
                label = detection["label"]
                confidence = detection["confidence"]

                # Clamp bounding-box coordinates to image dimensions.
                x1 = max(0, min(int(x1), image_width - 1))
                y1 = max(0, min(int(y1), image_height - 1))
                x2 = max(0, min(int(x2), image_width - 1))
                y2 = max(0, min(int(y2), image_height - 1))

                if x2 <= x1 or y2 <= y1:
                    continue

                # Draw a thin green bounding box.
                cv2.rectangle(
                    annotated_frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 200, 0),
                    2,
                )

                text = f"{label} {confidence:.2f}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.45
                thickness = 1

                (text_width, text_height), baseline = cv2.getTextSize(
                    text,
                    font,
                    font_scale,
                    thickness,
                )

                # Put labels above boxes where possible.
                label_x = max(
                    0,
                    min(x1, image_width - text_width - 4),
                )

                label_y = y1 - 6
                if label_y - text_height - baseline < 0:
                    label_y = min(
                        y1 + text_height + 8,
                        image_height - baseline - 1,
                    )

                background_top = max(
                    0,
                    label_y - text_height - 4,
                )
                background_bottom = min(
                    image_height - 1,
                    label_y + baseline,
                )
                background_right = min(
                    image_width - 1,
                    label_x + text_width + 4,
                )

                # Dark background improves label readability.
                cv2.rectangle(
                    annotated_frame,
                    (label_x, background_top),
                    (background_right, background_bottom),
                    (0, 120, 0),
                    -1,
                )

                cv2.putText(
                    annotated_frame,
                    text,
                    (label_x + 2, label_y),
                    font,
                    font_scale,
                    (255, 255, 255),
                    thickness,
                    cv2.LINE_AA,
                )

            annotated_image = cv2.cvtColor(
                annotated_frame,
                cv2.COLOR_BGR2RGB,
            )

        # --------------------------------------------------
        # Display detections
        # --------------------------------------------------

        st.subheader("Detected Vehicles")
        st.image(
            annotated_image,
            caption="YOLOv8 vehicle detections",
            use_container_width=True,
        )

        # --------------------------------------------------
        # Vehicle counts
        # --------------------------------------------------

        st.subheader("Vehicle Counts")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("🚗 Cars", counts["car"])
        col2.metric("🏍️ Motorcycles", counts["motorcycle"])
        col3.metric("🚌 Buses", counts["bus"])
        col4.metric("🚚 Trucks", counts["truck"])

        total_vehicles = sum(counts.values())
        st.metric("Total Vehicles", total_vehicles)

        # --------------------------------------------------
        # Adaptive signal timings
        # --------------------------------------------------

        st.subheader("Adaptive Signal Timings")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "North-South Green",
            f'{timings["north_south_green"]} sec',
        )
        col2.metric(
            "East-West Green",
            f'{timings["east_west_green"]} sec',
        )
        col3.metric(
            "Cycle Length",
            f'{timings["cycle_length"]} sec',
        )

        # --------------------------------------------------
        # Detection details
        # --------------------------------------------------

        with st.expander("View Detection Details"):
            if detections:
                st.dataframe(
                    [
                        {
                            "Vehicle": detection["label"],
                            "Confidence": round(
                                detection["confidence"], 3
                            ),
                            "Bounding Box": str(detection["bbox"]),
                        }
                        for detection in sorted(
                            detections,
                            key=lambda item: item["confidence"],
                            reverse=True,
                        )
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info(
                    "No vehicles met the selected confidence threshold."
                )

        # --------------------------------------------------
        # Limitations
        # --------------------------------------------------

        st.info(
            "Demonstration only: this application counts vehicles in "
            "a single image. It does not yet identify individual lanes, "
            "estimate real-time traffic flow, or determine actual "
            "traffic directions. The displayed signal timings are "
            "simulated and must not be used to control real traffic lights."
        )

    except Exception as error:
        st.error(f"Could not process the image: {error}")
        st.exception(error)
