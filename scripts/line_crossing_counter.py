"""Count tracked centroids crossing a horizontal line without vision dependencies."""
from __future__ import annotations

from dataclasses import dataclass
import math
from numbers import Integral, Real


def _finite_number(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real number")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite real number") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} must be a finite real number")
    return result


def _integer(value: int, name: str, *, nonnegative: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ValueError(f"{name} must be an integer")
    result = int(value)
    if nonnegative and result < 0:
        raise ValueError(f"{name} must be nonnegative")
    return result


@dataclass(frozen=True, slots=True)
class _Observation:
    frame: int
    x: float
    y: float


class LineCrossingCounter:
    """Count each track ID at most once per requested direction.

    Image y coordinates increase downwards. A downward crossing satisfies
    ``previous_y < line_y <= current_y``; upward uses the reversed inequalities.
    Merely appearing below/above the line is not a crossing. An observation
    exactly on the line may complete a crossing, but departing from the line
    does not create another one.

    Frames must increase strictly for each ID; different IDs may share a frame.
    Missing observations are allowed. ``gap_frames`` is the difference between
    the two observed frame indices, not the number of unobserved frames between
    them. The crossing position/time is a linear estimate between observations.
    In ``both`` mode, one ID can contribute one down event and one up event.
    """

    def __init__(self, line_y: float, direction: str = "down") -> None:
        self.line_y = _finite_number(line_y, "line_y")
        if direction not in ("down", "up", "both"):
            raise ValueError("direction must be 'down', 'up', or 'both'")
        self.direction = direction
        self.events: list[dict] = []
        self.counts = {"down": 0, "up": 0}
        self._previous: dict[int, _Observation] = {}
        self._counted: dict[str, set[int]] = {"down": set(), "up": set()}

    @property
    def total(self) -> int:
        """Number of events, including both directions when enabled."""
        return self.counts["down"] + self.counts["up"]

    def update(
        self,
        track_id: int,
        frame_index: int,
        center_x: float,
        center_y: float,
    ) -> dict | None:
        """Record a centroid and return its newly counted crossing, if any.

        Invalid inputs or repeated/out-of-order frames raise ``ValueError``
        before changing this ID's observation or any counts.
        """
        track_id = _integer(track_id, "track_id")
        frame_index = _integer(frame_index, "frame_index", nonnegative=True)
        x = _finite_number(center_x, "center_x")
        y = _finite_number(center_y, "center_y")
        previous = self._previous.get(track_id)
        if previous is not None and frame_index <= previous.frame:
            raise ValueError("frame_index must increase strictly for each track_id")

        current = _Observation(frame_index, x, y)
        if previous is None:
            self._previous[track_id] = current
            return None

        crossing = None
        if previous.y < self.line_y <= y:
            crossing = "down"
        elif previous.y > self.line_y >= y:
            crossing = "up"

        if (
            crossing is None
            or self.direction not in (crossing, "both")
            or track_id in self._counted[crossing]
        ):
            self._previous[track_id] = current
            return None

        delta_y = y - previous.y
        distance_y = self.line_y - previous.y
        if math.isfinite(delta_y) and math.isfinite(distance_y):
            fraction = distance_y / delta_y
        else:
            # Opposite, very large finite coordinates can overflow subtraction.
            scale = max(abs(previous.y), abs(y), abs(self.line_y))
            fraction = (self.line_y / scale - previous.y / scale) / (
                y / scale - previous.y / scale
            )
        gap_frames = frame_index - previous.frame
        event = {
            "track_id": track_id,
            "direction": crossing,
            "frame": frame_index,
            "previous_frame": previous.frame,
            "previous_x": previous.x,
            "previous_y": previous.y,
            "x": x,
            "y": y,
            "line_y": self.line_y,
            "crossing_x": (1.0 - fraction) * previous.x + fraction * x,
            "crossing_frame_interpolated": previous.frame + fraction * gap_frames,
            "gap_frames": gap_frames,
        }
        self._previous[track_id] = current
        self._counted[crossing].add(track_id)
        self.counts[crossing] += 1
        self.events.append(event)
        return event
