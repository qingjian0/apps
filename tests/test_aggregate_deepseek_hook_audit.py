import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.aggregate_deepseek_hook_audit import (
    prepared_method,
    prepared_similarity,
    project_candidate,
    version_identity,
)


def component(version_name, version_code="289", package="com.deepseek.chat", split=None):
    return {
        "apk": "base.apk" if split is None else f"{split}.apk",
        "sha256": "a" * 64,
        "manifest": {
            "package": package,
            "split": split,
            "version_name": version_name,
            "version_code": version_code,
        },
    }


class VersionIdentityTest(unittest.TestCase):
    def test_matching_base_manifest_is_trusted(self):
        result = version_identity("2.7.2", {
            "component_metadata": [component("2.7.2", "289")]
        })
        self.assertEqual(result["status"], "verified")
        self.assertTrue(result["trusted_for_cross_version"])

    def test_manifest_label_mismatch_is_quarantined(self):
        result = version_identity("2.7.3", {
            "component_metadata": [component("2.5.2", "273")]
        })
        self.assertEqual(result["status"], "label-mismatch")
        self.assertFalse(result["trusted_for_cross_version"])
        self.assertEqual(result["manifest_version_name"], "2.5.2")

    def test_split_manifests_do_not_override_base_identity(self):
        result = version_identity("2.7.4", {
            "component_metadata": [
                component("2.7.4", "294"),
                component(None, "294", split="config.arm64_v8a"),
                component(None, "294", split="config.zh"),
            ]
        })
        self.assertEqual(result["status"], "verified")
        self.assertEqual(result["base_component"], "base.apk")

    def test_missing_manifest_version_name_is_not_trusted(self):
        result = version_identity("2.7.5", {
            "component_metadata": [component(None, "295")]
        })
        self.assertEqual(result["status"], "version-name-missing")
        self.assertFalse(result["trusted_for_cross_version"])

    def test_wrong_package_is_not_trusted(self):
        result = version_identity("2.7.2", {
            "component_metadata": [component("2.7.2", "289", package="com.example.other")]
        })
        self.assertEqual(result["status"], "package-mismatch")
        self.assertFalse(result["trusted_for_cross_version"])


class CandidateProjectionTest(unittest.TestCase):
    def test_projection_discards_large_dataflow_payloads(self):
        method = {
            "class": "Lx;",
            "name": "a",
            "descriptor": "()V",
            "roles": [{"role": "request_route", "anchors": ["/api/v0/chat/completion"]}],
            "invokes": ["Lkotlinx/coroutines/Flow;->collect()V"],
            "strings": ["/api/v0/chat/completion"],
            "opcode_histogram": {"invoke-virtual": 4},
            "opcode_count": 4,
            "register_dataflow": {"definitions": list(range(10000))},
            "control_flow": {"blocks": list(range(10000))},
        }
        projected = project_candidate(method)
        self.assertNotIn("register_dataflow", projected)
        self.assertNotIn("control_flow", projected)
        self.assertEqual(projected["class"], "Lx;")

    def test_prepared_similarity_is_stable_for_identical_candidates(self):
        method = {
            "class": "Lx;",
            "name": "a",
            "descriptor": "()V",
            "roles": [{"role": "request_route", "anchors": ["/api/v0/chat/completion"]}],
            "invokes": ["Lkotlinx/coroutines/Flow;->collect()V"],
            "strings": ["/api/v0/chat/completion"],
            "opcode_histogram": {"invoke-virtual": 4, "return-object": 1},
        }
        self.assertEqual(prepared_similarity(prepared_method(method), prepared_method(method)), 1.0)


if __name__ == "__main__":
    unittest.main()
