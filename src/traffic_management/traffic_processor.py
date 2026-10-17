
"""Connect vehicle detection to adaptive traffic signal timing."""

from traffic_management.signal_controller import SignalController
from traffic_management.vehicle_detector import VehicleDetector


class TrafficProcessor:
    """Process vehicle detections and calculate signal timings."""

    def __init__(self):
        self.detector = VehicleDetector()
        self.signal_controller = SignalController()

    def process_image(self, image):
        """Detect vehicles and return counts and signal timings."""
        detections = self.detector.detect(image)
        counts = self.detector.count_by_type(detections)

        # Simple demonstration: total detected vehicles are treated
        # as demand for the north-south direction.
        north_south_demand = sum(counts.values())
        east_west_demand = 0

        timings = self.signal_controller.calculate(
            north_south=north_south_demand,
            east_west=east_west_demand,
        )

        return {
            "detections": detections,
            "vehicle_counts": counts,
            "signal_timings": timings,
        }
