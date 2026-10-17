
from traffic_management.vehicle_detector import VehicleDetector


def test_count_by_type():
    detections = [
        {"label": "car"},
        {"label": "car"},
        {"label": "bus"},
        {"label": "motorcycle"},
    ]

    counts = VehicleDetector.count_by_type(detections)

    assert counts == {
        "car": 2,
        "motorcycle": 1,
        "bus": 1,
        "truck": 0,
    }


def test_empty_detections():
    counts = VehicleDetector.count_by_type([])

    assert counts == {
        "car": 0,
        "motorcycle": 0,
        "bus": 0,
        "truck": 0,
    }
