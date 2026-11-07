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

    def test_builds_conditional_and_goto_control_flow_edges(self):
        body = [
            "    const/4 v0, 0x0",
            "    if-eqz v0, :cond_0",
            "    invoke-static {}, Lx/Worker;->run()V",
            "    goto :goto_0",
            "    :cond_0",
            "    const/4 v1, 0x1",
            "    :goto_0",
            "    return-void",
        ]
        cfg = AUDIT.build_smali_cfg(body)
        self.assertTrue(cfg["complete"])
        self.assertEqual(6, cfg["instruction_count"])
        self.assertGreaterEqual(cfg["block_count"], 4)
        self.assertIn("conditional", {edge["kind"] for edge in cfg["edges"]})
        self.assertIn("goto", {edge["kind"] for edge in cfg["edges"]})
        self.assertIn("fallthrough", {edge["kind"] for edge in cfg["edges"]})

    def test_switch_payload_resolves_case_targets_without_counting_payload_as_code(self):
        body = [
            "    packed-switch v0, :pswitch_data_0",
            "    goto :end",
            "    :case_0",
            "    return-void",
            "    :end",
            "    return-void",
            "    :pswitch_data_0",
            "    .packed-switch 0x0",
            "        0x0 -> :case_0",
            "    .end packed-switch",
        ]
        cfg = AUDIT.build_smali_cfg(body)
        self.assertTrue(cfg["complete"])
        self.assertEqual(4, cfg["instruction_count"])
        self.assertIn("switch", {edge["kind"] for edge in cfg["edges"]})
        self.assertIn("switch-default", {edge["kind"] for edge in cfg["edges"]})

    def test_unresolved_branch_target_marks_cfg_incomplete(self):
        cfg = AUDIT.build_smali_cfg(["    if-eqz v0, :missing", "    return-void"])
        self.assertFalse(cfg["complete"])
        self.assertEqual(1, cfg["unresolved_target_count"])
        self.assertIn(":missing", cfg["unresolved_targets"])

    def test_truncated_edge_inventory_marks_cfg_incomplete(self):
        body = ["    if-eqz v0, :end" for _ in range(130)]
        body += [":end", "    return-void"]
        cfg = AUDIT.build_smali_cfg(body)
        self.assertGreater(cfg["edge_count"], 256)
        self.assertTrue(cfg["edges_truncated"])
        self.assertFalse(cfg["complete"])

    def test_exception_handler_edges_are_explicit(self):
        body = [
            "    :try_start_0",
            "    invoke-static {}, Lx/Worker;->run()V",
            "    :try_end_0",
            "    return-void",
            "    :catch_0",
            "    move-exception v0",
            "    return-void",
            "    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0",
        ]
        cfg = AUDIT.build_smali_cfg(body)
        self.assertTrue(cfg["complete"])
        self.assertIn("exception", {edge["kind"] for edge in cfg["edges"]})

    def test_register_use_def_tracks_move_field_and_invoke_registers(self):
        facts = AUDIT.analyze_register_use_def([
            "    const/4 v0, 0x1",
            "    move v1, v0",
            "    iget-object v2, p1, Lx/State;->value:Ljava/lang/String;",
            "    iput-object v2, p1, Lx/State;->result:Ljava/lang/String;",
            "    invoke-static {v1, v2}, Lx/Worker;->run(II)V",
            "    return-void",
        ])
        self.assertTrue(facts["complete"])
        self.assertIn("v0", facts["written_registers"])
        self.assertIn("v1", facts["written_registers"])
        self.assertIn("v2", facts["written_registers"])
        self.assertIn("v0", facts["read_registers"])
        self.assertIn("v1", facts["read_registers"])
        self.assertIn("v2", facts["read_registers"])
        self.assertIn("p1", facts["read_registers"])

    def test_unknown_register_opcode_marks_use_def_incomplete(self):
        facts = AUDIT.analyze_register_use_def(["    foo-op v0, v1"])
        self.assertFalse(facts["complete"])
        self.assertEqual(1, facts["unknown_opcode_count"])
        self.assertEqual("foo-op", facts["unknown_opcodes"][0]["opcode"])

    def test_register_ranges_and_two_address_reads_are_expanded(self):
        facts = AUDIT.analyze_register_use_def([
            "    invoke-static/range {v2 .. v5}, Lx/Worker;->run()V",
            "    add-int/2addr v2, v3",
        ])
        self.assertTrue(facts["complete"])
        invoke = facts["instructions"][0]
        self.assertEqual(["v2", "v3", "v4", "v5"], invoke["reads"])
        arithmetic = facts["instructions"][1]
        self.assertIn("v2", arithmetic["reads"])
        self.assertEqual(["v2"], arithmetic["writes"])

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

    def test_signer_parser_handles_android_signer_rotation_entries(self):
        output = (
            "Signer (minSdkVersion=33, maxSdkVersion=2147483647) certificate SHA-256 digest: "
            "c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa\n"
            "Signer (minSdkVersion=24, maxSdkVersion=32) certificate SHA-256 digest: "
            "1eecc46fdc2173437d70140f163aaa97941d41b04d91da3eb689aec4f339abeb\n"
        )
        parsed = AUDIT.parse_signing_certificates(output)
        self.assertEqual("c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa", parsed["signing_sha256"])
        self.assertEqual(2, len(parsed["signing_sha256s"]))

    def test_signer_parser_supports_numbered_signer_format(self):
        output = "Signer #1 certificate SHA-256 digest: c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa\n"
        parsed = AUDIT.parse_signing_certificates(output)
        self.assertEqual(1, len(parsed["signing_sha256s"]))


if __name__ == "__main__":
    unittest.main()
