import time
import unittest

from nanoclaw.aggregation import DecisionEngine, SensorAggregator, SensorReading


class SensorAggregationTests(unittest.TestCase):
    def test_ingest_tracks_node_status_and_bounded_history(self):
        aggregator = SensorAggregator(max_readings_per_node=2)
        aggregator.ingest(SensorReading(node_id="rack-a1", temperature_c=31.2, humidity_pct=60.0))
        aggregator.ingest(SensorReading(node_id="rack-a1", temperature_c=32.5, humidity_pct=61.0))
        aggregator.ingest(SensorReading(node_id="rack-a1", temperature_c=33.1, humidity_pct=62.0))

        node = aggregator.get_node("rack-a1")

        self.assertEqual(node.node_id, "rack-a1")
        self.assertEqual(node.status, "online")
        self.assertEqual(len(node.readings), 2)
        self.assertEqual(node.latest.temperature_c, 33.1)
        self.assertGreater(node.updated_at, 0)

    def test_decision_engine_flags_threshold_crossings(self):
        engine = DecisionEngine(temp_warning_c=30.0, temp_critical_c=40.0, humidity_warning_pct=70.0)
        reading = SensorReading(node_id="rack-a1", temperature_c=41.0, humidity_pct=72.0)

        decisions = engine.evaluate(reading)

        types = {decision.type for decision in decisions}
        self.assertIn("temperature_critical", types)
        self.assertIn("humidity_warning", types)
        self.assertTrue(all(decision.node_id == "rack-a1" for decision in decisions))
        self.assertTrue(all(decision.action for decision in decisions))

    def test_offline_detection_marks_stale_nodes(self):
        aggregator = SensorAggregator(stale_after_seconds=1)
        aggregator.ingest(SensorReading(node_id="rack-a1", temperature_c=25.0, humidity_pct=45.0, timestamp=time.time() - 5))

        stale = aggregator.mark_stale_nodes(now=time.time())

        self.assertEqual([node.node_id for node in stale], ["rack-a1"])
        self.assertEqual(aggregator.get_node("rack-a1").status, "stale")


if __name__ == "__main__":
    unittest.main()
