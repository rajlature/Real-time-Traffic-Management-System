
"""Adaptive traffic signal timing logic."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class SignalConfig:
    base_cycle: int = 90
    yellow_time: int = 3
    red_clearance: int = 1
    min_green: int = 10
    max_green: int = 60


class SignalController:
    """Allocate green time according to measured traffic demand."""

    def __init__(self, config: SignalConfig | None = None):
        self.config = config or SignalConfig()

        if self.config.min_green <= 0:
            raise ValueError("min_green must be positive")
        if self.config.max_green < self.config.min_green:
            raise ValueError("max_green must be >= min_green")
        if self.config.yellow_time < 0 or self.config.red_clearance < 0:
            raise ValueError("Clearance times cannot be negative")

        clearance = 2 * (
            self.config.yellow_time + self.config.red_clearance
        )
        available = self.config.base_cycle - clearance

        if available < 2 * self.config.min_green:
            raise ValueError("Cycle is too short for minimum green times")
        if available > 2 * self.config.max_green:
            raise ValueError("Cycle exceeds the combined maximum green times")

    @staticmethod
    def _demand(value) -> float:
        """Convert invalid or negative demand to zero."""
        try:
            number = float(value)
        except (TypeError, ValueError):
            return 0.0

        if not math.isfinite(number):
            return 0.0

        return max(0.0, number)

    def calculate(self, north_south: float, east_west: float) -> dict:
        """Return a validated timing plan for two traffic directions."""
        ns = self._demand(north_south)
        ew = self._demand(east_west)

        cfg = self.config
        clearance = 2 * (cfg.yellow_time + cfg.red_clearance)
        available = cfg.base_cycle - clearance

        # With no traffic data, use a balanced plan.
        if ns + ew == 0:
            ns_green = available // 2
            ew_green = available - ns_green
        else:
            # Give both directions minimum green time first.
            remaining = available - 2 * cfg.min_green
            ns_green = cfg.min_green + remaining * ns / (ns + ew)
            ew_green = cfg.min_green + remaining * ew / (ns + ew)

            # Enforce maximum green time and redistribute spare time.
            ns_green = min(cfg.max_green, ns_green)
            ew_green = min(cfg.max_green, ew_green)

            unused = available - ns_green - ew_green

            if unused > 0:
                add_ns = min(unused, cfg.max_green - ns_green)
                ns_green += add_ns
                unused -= add_ns

            if unused > 0:
                ew_green += min(unused, cfg.max_green - ew_green)

            ns_green = int(round(ns_green))
            ew_green = available - ns_green

        return {
            "north_south_green": int(ns_green),
            "east_west_green": int(ew_green),
            "yellow_time": cfg.yellow_time,
            "red_clearance": cfg.red_clearance,
            "cycle_length": (
                int(ns_green) + int(ew_green) + clearance
            ),
        }
