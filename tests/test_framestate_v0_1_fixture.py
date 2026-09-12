from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "generations" / "framestate-v0.1"


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


class FrameStateV01FixtureTests(unittest.TestCase):
    def test_exact_historical_artifact_matches_declared_git_blob(self):
        manifest = json.loads((FIXTURE / "manifest.json").read_text(encoding="utf-8"))
        artifact = (FIXTURE / manifest["artifact"]).read_bytes()
        self.assertEqual(manifest["source_ref"], "5b5f73cb78667d9af981af3b38cd7a7ce3a5dab7")
        self.assertEqual(manifest["source_path"], "examples/first_light.json")
        self.assertEqual(git_blob_sha(artifact), manifest["source_blob_sha"])
        self.assertEqual(manifest["source_blob_sha"], "3a6f64e8f0355812360abd0546f2b997cdb0db28")

    def test_fixture_claim_does_not_invent_speech_semantics(self):
        manifest = json.loads((FIXTURE / "manifest.json").read_text(encoding="utf-8"))
        project = json.loads((FIXTURE / "project.json").read_text(encoding="utf-8"))
        self.assertEqual(project["schema"], "axm.framestate.project/v0.1")
        self.assertEqual(manifest["semantic_claims"], {"audio_model": "tone_only"})
        self.assertTrue(project["audio"])
        self.assertTrue(all(event.get("kind") == "tone" for event in project["audio"]))
        self.assertNotIn("undeclared_speech_engine", manifest["semantic_claims"])


if __name__ == "__main__":
    unittest.main()
