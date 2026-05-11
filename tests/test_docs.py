import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
DOCKERFILE = (ROOT / "Dockerfile").read_text(encoding="utf-8")


class NanoClawDocsTests(unittest.TestCase):
    def test_readme_mentions_gateway_and_api(self):
        self.assertIn("Raspberry Pi Gateway Quick Start", README)
        self.assertIn("/api/v1/telemetry", README)
        self.assertIn("Local Decision Engine", README)
        self.assertIn("temperature_critical", README)

    def test_dockerfile_installs_project_after_copying_src(self):
        self.assertIn("COPY pyproject.toml README.md ./", DOCKERFILE)
        self.assertIn("COPY src/ src/", DOCKERFILE)
        self.assertIn("RUN pip install --no-cache-dir .", DOCKERFILE)
        self.assertIn("uvicorn", DOCKERFILE)


if __name__ == "__main__":
    unittest.main()
