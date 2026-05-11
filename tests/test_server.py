import asyncio
from collections import deque
import importlib
import sys
import types
import unittest

from nanoclaw.aggregation import DecisionEngine, SensorAggregator


class FakeFastAPI:
    def __init__(self, *args, **kwargs):
        pass

    def get(self, *args, **kwargs):
        return self._route

    def post(self, *args, **kwargs):
        return self._route

    @staticmethod
    def _route(func):
        return func


class FakeHTTPException(Exception):
    def __init__(self, status_code, detail):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def load_server_module():
    try:
        import fastapi  # noqa: F401
    except ModuleNotFoundError:
        fake_fastapi = types.ModuleType("fastapi")
        fake_fastapi.FastAPI = FakeFastAPI
        fake_fastapi.HTTPException = FakeHTTPException
        sys.modules["fastapi"] = fake_fastapi
    return importlib.import_module("nanoclaw.server")


class NanoClawServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = load_server_module()

    def setUp(self):
        self.server.aggregator = SensorAggregator()
        self.server.decision_engine = DecisionEngine()
        self.server.decision_log = deque(maxlen=1000)

    def test_ingest_telemetry_rejects_empty_node_id_as_400(self):
        with self.assertRaises(self.server.HTTPException) as raised:
            asyncio.run(self.server.ingest_telemetry({"node_id": ""}))

        self.assertEqual(raised.exception.status_code, 400)
        self.assertEqual(raised.exception.detail, "node_id is required")

    def test_ingest_telemetry_preserves_zero_timestamp(self):
        result = asyncio.run(
            self.server.ingest_telemetry(
                {
                    "node_id": "rack-a1",
                    "temperature_c": 25.0,
                    "humidity_pct": 45.0,
                    "timestamp": 0.0,
                }
            )
        )

        self.assertEqual(result["node"]["updated_at"], 0.0)
        self.assertEqual(result["node"]["latest"]["timestamp"], 0.0)


if __name__ == "__main__":
    unittest.main()
