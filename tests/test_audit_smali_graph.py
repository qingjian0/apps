import importlib.util
import pathlib
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "audit_deepseek_apk.py"
SPEC = importlib.util.spec_from_file_location("audit_deepseek_apk", SCRIPT)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class SmaliGraphExtractionTest(unittest.TestCase):
    def test_extracts_field_reads_writes_and_control_flow(self):
        source = """.class public Lx/Test;
.super Ljava/lang/Object;
.method public compose(Lx/State;)V
    .locals 2
    iget-object v0, p1, Lx/State;->prompt:Ljava/lang/String;
    if-eqz v0, :cond_0
    iput-object v0, p1, Lx/State;->result:Ljava/lang/String;
:cond_0
    return-void
.end method
"""
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "Test.smali").write_text(source)
            classes, methods, edges = AUDIT.analyze_smali(root)
        self.assertEqual(1, len(classes))
        self.assertEqual(1, len(methods))
        method = methods[0]
        self.assertIn("Lx/State;->prompt:Ljava/lang/String;", method["field_reads"])
        self.assertIn("Lx/State;->result:Ljava/lang/String;", method["field_writes"])
        self.assertEqual(1, method["control_flow"]["branch_count"])
        self.assertGreaterEqual(method["control_flow"]["label_count"], 1)
        self.assertEqual(1, method["control_flow"]["return_count"])

    def test_method_without_fields_has_empty_flow_sets(self):
        source = """.class public Lx/Plain;
.super Ljava/lang/Object;
.method public ping()V
    return-void
.end method
"""
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "Plain.smali").write_text(source)
            _, methods, _ = AUDIT.analyze_smali(root)
        self.assertEqual([], methods[0]["field_reads"])
        self.assertEqual([], methods[0]["field_writes"])
        self.assertEqual(0, methods[0]["control_flow"]["branch_count"])

    def test_redaction_marker_cannot_trigger_prompt_anchor(self):
        redacted = AUDIT.safe_strings('    const-string v0, "prompt body must not persist"')
        self.assertEqual(["<redacted-content>"], redacted)
        self.assertNotIn("prompt", redacted[0].lower())

    def test_binary_badging_metadata_parser(self):
        output = "package: name='com.deepseek.chat' versionCode='294' versionName='2.7.4' split='config.arm64_v8a'\n"
        parsed = AUDIT.parse_aapt_badging(output)
        self.assertEqual("com.deepseek.chat", parsed["package"])
        self.assertEqual("294", parsed["version_code"])
        self.assertEqual("2.7.4", parsed["version_name"])
        self.assertEqual("config.arm64_v8a", parsed["split"])

    def test_badging_parser_records_missing_version_as_unknown(self):
        parsed = AUDIT.parse_aapt_badging("package: name='com.deepseek.chat'\n")
        self.assertEqual("com.deepseek.chat", parsed["package"])
        self.assertNotIn("version_code", parsed)


if __name__ == "__main__":
    unittest.main()
