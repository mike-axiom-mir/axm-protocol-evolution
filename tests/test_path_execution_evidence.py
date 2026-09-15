from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from protocol_evolution.path_execution_evidence import analyze_path_execution_observations

ROOT = Path(__file__).resolve().parents[1]
OBSERVATIONS = ROOT / "fixtures" / "path_execution_observations.json"
CHECKED_EVIDENCE = ROOT / "evidence" / "path_execution_evidence.json"


def canonical_digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def raw_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


class PathExecutionEvidenceTests(unittest.TestCase):
    def payload(self):
        return json.loads(OBSERVATIONS.read_text(encoding="utf-8"))

    def analyze(self, payload=None, root=ROOT):
        return analyze_path_execution_observations(payload or self.payload(), root)

    def minimal_copy(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        shutil.copytree(ROOT / "fixtures" / "generations", root / "fixtures" / "generations")
        (root / "fixtures").mkdir(exist_ok=True)
        shutil.copy2(ROOT / "fixtures" / "migration_paths.json", root / "fixtures" / "migration_paths.json")
        shutil.copytree(ROOT / "evidence" / "execution_outputs", root / "evidence" / "execution_outputs")
        return temp, root

    def test_current_observation_is_valid_and_narrow(self):
        result = self.analyze()
        self.assertTrue(result["valid"])
        self.assertEqual(result["observed_execution_path_count"], 1)
        self.assertTrue(result["migration_execution_observed_for_recorded_paths"])
        self.assertFalse(result["donor_execution_replayed_in_ci"])
        self.assertFalse(result["whole_project_semantic_equivalence_proven"])
        self.assertFalse(result["direct_vs_chain_equivalence_proven"])
        self.assertFalse(result["chain_experiment_input_ready"])
        self.assertFalse(result["canon_authority_granted"])
        self.assertFalse(result["adapter_translation_garden_ownership_changed"])

    def test_checked_evidence_matches_generated_truth(self):
        expected = json.loads(CHECKED_EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(self.analyze(), expected)

    def test_unknown_path_fails_closed(self):
        payload = self.payload()
        payload["observations"][0]["path_id"] = "not-admitted"
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any("unknown-admitted-path" in failure for failure in result["failures"]))

    def test_weak_donor_commit_fails_closed(self):
        payload = self.payload()
        payload["observations"][0]["donor_commit"] = "60ea68b"
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertIn("observation[0]:weak-donor-commit", result["failures"])

    def test_source_identity_mismatch_fails_closed(self):
        payload = self.payload()
        payload["observations"][0]["source_fixture_sha256"] = "sha256:" + "0" * 64
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertIn("observation[0]:source-sha256-mismatch", result["failures"])

    def test_changed_legacy_output_meaning_fails_even_when_rehashed(self):
        temp, root = self.minimal_copy()
        try:
            payload = self.payload()
            output = root / payload["observations"][0]["observed_output_path"]
            value = json.loads(output.read_text(encoding="utf-8"))
            value["audio"][0]["engine"] = "native"
            output.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            payload["observations"][0]["observed_output_sha256"] = raw_sha256(output)
            payload["observations"][0]["observed_output_canonical_digest"] = canonical_digest(value)
            result = self.analyze(payload, root)
            self.assertFalse(result["valid"])
            self.assertIn("observation[0]:legacy-meaning-not-preserved", result["failures"])
        finally:
            temp.cleanup()

    def test_source_mutation_flag_fails_closed(self):
        payload = self.payload()
        payload["observations"][0]["source_object_unchanged"] = False
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertIn("observation[0]:source-object-mutated-or-unverified", result["failures"])

    def test_forbidden_chain_promotion_fails_closed(self):
        payload = self.payload()
        payload["observations"][0]["forbidden_promotions"]["chain_experiment_input_ready"] = True
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertIn("observation[0]:forbidden-promotion-claim", result["failures"])

    def test_duplicate_observation_cannot_pad_execution_coverage(self):
        payload = self.payload()
        duplicate = copy.deepcopy(payload["observations"][0])
        duplicate["id"] = "second-id-same-path"
        payload["observations"].append(duplicate)
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any("duplicate-path-observation" in failure for failure in result["failures"]))


if __name__ == "__main__":
    unittest.main()
