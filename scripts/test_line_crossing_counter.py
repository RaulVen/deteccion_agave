"""Tests for trajectory counting; no video/model dependencies are imported."""
import math
import unittest

if __package__:
    from .line_crossing_counter import LineCrossingCounter
else:
    from line_crossing_counter import LineCrossingCounter


class LineCrossingCounterTests(unittest.TestCase):
    def test_first_sighting_below_line_does_not_count(self):
        counter = LineCrossingCounter(10)
        self.assertIsNone(counter.update(1, 0, 5, 15))
        self.assertIsNone(counter.update(1, 1, 5, 20))
        self.assertEqual(counter.events, [])
        self.assertEqual(counter.counts, {"down": 0, "up": 0})
        self.assertEqual(counter.total, 0)
        self.assertTrue(counter)

    def test_downward_crossing_interpolates_across_missing_frames(self):
        counter = LineCrossingCounter(10)
        counter.update(7, 2, 10, 5)
        event = counter.update(7, 6, 30, 15)
        self.assertEqual(event, {
            "track_id": 7, "direction": "down", "frame": 6,
            "previous_frame": 2, "previous_x": 10.0, "previous_y": 5.0,
            "x": 30.0, "y": 15.0, "line_y": 10.0,
            "crossing_x": 20.0, "crossing_frame_interpolated": 4.0,
            "gap_frames": 4,
        })
        self.assertEqual(counter.events, [event])
        self.assertIs(event, counter.events[0])
        event.update(confidence=0.9, event_number=1)
        self.assertEqual(counter.events[0]["confidence"], 0.9)
        self.assertEqual(counter.counts, {"down": 1, "up": 0})
        self.assertEqual(counter.total, 1)

    def test_bounces_do_not_recount_id_and_other_ids_are_independent(self):
        counter = LineCrossingCounter(10)
        for frame, y in enumerate((5, 15, 5, 15, 5, 15)):
            counter.update(1, frame, 20, y)
        counter.update(2, 0, 40, 5)
        counter.update(2, 5, 40, 15)
        self.assertEqual([event["track_id"] for event in counter.events], [1, 2])
        self.assertEqual(counter.counts, {"down": 2, "up": 0})

    def test_ignored_upward_crossing_still_updates_last_observation(self):
        counter = LineCrossingCounter(10)
        counter.update(1, 0, 0, 15)
        self.assertIsNone(counter.update(1, 3, 6, 5))
        event = counter.update(1, 5, 10, 15)
        self.assertEqual(event["previous_frame"], 3)
        self.assertEqual(event["previous_x"], 6)
        self.assertEqual(event["crossing_x"], 8)
        self.assertEqual(event["crossing_frame_interpolated"], 4)
        self.assertEqual(event["gap_frames"], 2)

    def test_up_mode_counts_only_one_upward_crossing(self):
        counter = LineCrossingCounter(10, "up")
        counter.update(5, 0, 2, 5)
        self.assertIsNone(counter.update(5, 1, 4, 15))
        event = counter.update(5, 3, 8, 5)
        self.assertEqual(event["direction"], "up")
        self.assertEqual(event["crossing_x"], 6)
        self.assertEqual(event["crossing_frame_interpolated"], 2)
        counter.update(5, 4, 10, 15)
        self.assertIsNone(counter.update(5, 5, 12, 5))
        self.assertEqual(counter.counts, {"down": 0, "up": 1})

    def test_both_mode_allows_one_event_per_direction_per_id(self):
        counter = LineCrossingCounter(10, "both")
        for frame, y in enumerate((5, 15, 5, 15, 5)):
            counter.update(2, frame, 3, y)
        self.assertEqual([e["direction"] for e in counter.events], ["down", "up"])
        self.assertEqual(counter.counts, {"down": 1, "up": 1})
        self.assertEqual(counter.total, 2)

    def test_arriving_exactly_on_line_counts_but_departing_does_not(self):
        for direction, before, after in (("down", 5, 15), ("up", 15, 5)):
            with self.subTest(direction=direction):
                counter = LineCrossingCounter(10, direction)
                counter.update(1, 0, 3, before)
                event = counter.update(1, 1, 7, 10)
                self.assertEqual(event["direction"], direction)
                self.assertEqual(event["crossing_x"], 7)
                self.assertEqual(event["crossing_frame_interpolated"], 1)
                self.assertIsNone(counter.update(1, 2, 8, 10))
                self.assertIsNone(counter.update(1, 3, 9, after))
                self.assertEqual(counter.total, 1)

                first_on_line = LineCrossingCounter(10, direction)
                first_on_line.update(1, 0, 3, 10)
                self.assertIsNone(first_on_line.update(1, 1, 7, after))
                self.assertEqual(first_on_line.total, 0)

    def test_duplicate_or_older_frame_is_rejected_without_changing_state(self):
        counter = LineCrossingCounter(10)
        counter.update(4, 10, 0, 5)
        for frame in (10, 9):
            with self.subTest(frame=frame), self.assertRaises(ValueError):
                counter.update(4, frame, 100, 15)
        self.assertEqual(counter.total, 0)
        event = counter.update(4, 12, 4, 15)
        self.assertEqual(event["previous_frame"], 10)
        self.assertEqual(event["previous_x"], 0)
        self.assertEqual(event["crossing_x"], 2)

    def test_same_frame_for_different_ids_is_allowed(self):
        counter = LineCrossingCounter(10)
        for track_id in (1, 2):
            counter.update(track_id, 10, 0, 5)
        for track_id in (1, 2):
            counter.update(track_id, 11, 0, 15)
        self.assertEqual(counter.total, 2)

    def test_invalid_line_or_direction_is_rejected(self):
        for value in (float("nan"), float("inf"), -float("inf"), "10", None, True):
            with self.subTest(line_y=value), self.assertRaises(ValueError):
                LineCrossingCounter(value)
        for direction in ("left", "DOWN", "", None):
            with self.subTest(direction=direction), self.assertRaises(ValueError):
                LineCrossingCounter(10, direction)

    def test_invalid_observations_do_not_advance_history(self):
        counter = LineCrossingCounter(10)
        counter.update(1, 0, 0, 5)
        bad_updates = [
            (1, 1, float("nan"), 15),
            (1, 1, 1, float("inf")),
            (1, 1, -float("inf"), 15),
            (1, 1, "1", 15),
            (1, 1, 1, True),
            (1, -1, 1, 15),
            (1, 0.5, 1, 15),
            (1, True, 1, 15),
            (1.5, 1, 1, 15),
            (True, 1, 1, 15),
        ]
        for args in bad_updates:
            with self.subTest(args=args), self.assertRaises(ValueError):
                counter.update(*args)
        event = counter.update(1, 1, 2, 15)
        self.assertEqual(event["previous_frame"], 0)
        self.assertEqual(counter.total, 1)

    def test_interpolation_handles_large_finite_coordinates(self):
        counter = LineCrossingCounter(0)
        counter.update(1, 0, -1e308, -1e308)
        event = counter.update(1, 2, 1e308, 1e308)
        self.assertTrue(math.isfinite(event["crossing_x"]))
        self.assertEqual(event["crossing_x"], 0)
        self.assertEqual(event["crossing_frame_interpolated"], 1)


if __name__ == "__main__":
    unittest.main()
