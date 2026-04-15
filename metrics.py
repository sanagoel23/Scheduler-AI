from dataclasses import dataclass
from time import perf_counter


@dataclass
class Metrics:
    """Tracks performance counters for CSP solving."""

    recursive_calls: int = 0
    constraint_checks: int = 0
    started_at: float = 0.0
    ended_at: float = 0.0

    def start(self) -> None:
        self.started_at = perf_counter()

    def stop(self) -> None:
        self.ended_at = perf_counter()

    @property
    def execution_time_ms(self) -> float:
        return (self.ended_at - self.started_at) * 1000

    def as_dict(self) -> dict:
        return {
            "recursive_calls": self.recursive_calls,
            "constraint_checks": self.constraint_checks,
            "execution_time_ms": round(self.execution_time_ms, 4),
        }
