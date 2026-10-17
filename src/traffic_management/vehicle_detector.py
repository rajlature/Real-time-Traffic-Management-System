
"""Vehicle detection using a pretrained YOLOv8 model."""

# from pathlib import Path

from ultralytics import YOLO


# COCO class IDs used by YOLO for common road vehicles.
VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}


class VehicleDetector:
    """Detect and count vehicles in an image or video frame."""

    def __init__(self, model_path: str = "yolov8s.pt"):
        self.model = YOLO(model_path)

    def detect(self, frame):
        """Return vehicle detections for a single image/frame."""
        results = self.model.predict(
            source=frame,
            classes=list(VEHICLE_CLASSES.keys()),
            conf=0.35,
            iou=0.45,
            imgsz=960,
            verbose=False,
        )

        detections = []

        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                class_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())
                x1, y1, x2, y2 = (
                    int(value) for value in box.xyxy[0].tolist()
                )

                detections.append({
                    "class_id": class_id,
                    "label": VEHICLE_CLASSES.get(class_id, "unknown"),
                    "confidence": confidence,
                    "bbox": (x1, y1, x2, y2),
                })

        return detections

    @staticmethod
    def count_by_type(detections):
        """Count detected vehicles by category."""
        counts = {name: 0 for name in VEHICLE_CLASSES.values()}

        for detection in detections:
            label = detection["label"]
            if label in counts:
                counts[label] += 1

        return counts
