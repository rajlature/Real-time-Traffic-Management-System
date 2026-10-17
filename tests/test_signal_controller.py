
import pytest

from traffic_management.signal_controller import SignalController, SignalConfig


@pytest.fixture
def controller():
    return SignalController()


def test_zero_traffic_returns_balanced_plan(controller):
    plan = controller.calculate(0, 0)

    assert plan["north_south_green"] == plan["east_west_green"]
    assert plan["cycle_length"] == 90


def test_heavier_traffic_gets_more_green_time(controller):
    plan = controller.calculate(100, 10)

    assert plan["north_south_green"] > plan["east_west_green"]


def test_green_times_respect_limits(controller):
    for ns, ew in [(0, 100), (100, 0), (50, 50), (1000, 1)]:
        plan = controller.calculate(ns, ew)

        assert 10 <= plan["north_south_green"] <= 60
        assert 10 <= plan["east_west_green"] <= 60


def test_cycle_length_includes_clearance_times(controller):
    plan = controller.calculate(80, 20)

    expected = (
        plan["north_south_green"]
        + plan["east_west_green"]
        + 2 * (plan["yellow_time"] + plan["red_clearance"])
    )

    assert plan["cycle_length"] == expected


def test_invalid_demands_do_not_crash(controller):
    plan = controller.calculate(float("nan"), -5)

    assert plan["north_south_green"] >= 10
    assert plan["east_west_green"] >= 10


def test_invalid_configuration_is_rejected():
    with pytest.raises(ValueError):
        SignalController(SignalConfig(min_green=70, max_green=60))
