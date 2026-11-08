import importlib.util
import pathlib
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "audit_deepseek_apk.py"
SPEC = importlib.util.spec_from_file_location("audit_deepseek_apk", SCRIPT)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class SmaliGraphExtractionTest(unittest.TestCase):
    def test_jsonl_gzip_writer_emits_real_line_breaks(self):
        records = [{"index": 1, "identity": "first"}, {"index": 2, "identity": "second"}]
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "records.jsonl.gz"
            AUDIT.write_jsonl_gzip(path, records)
            import gzip
            with gzip.open(path, "rt", encoding="utf-8") as stream:
                lines = stream.read().splitlines()
        self.assertEqual(2, len(lines))
        self.assertEqual(records, [__import__("json").loads(line) for line in lines])

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


    def test_reaching_definitions_resolve_linear_register_flow(self):
        body = [
            "    const/4 v0, 0x1",
            "    move v1, v0",
            "    return v1",
        ]
        cfg = AUDIT.build_smali_cfg(body)
        facts = AUDIT.analyze_register_dataflow(body, cfg)
        self.assertTrue(facts["complete"])
        use = next(x for x in facts["uses"] if x["register"] == "v0")
        self.assertEqual("resolved", use["resolution"])
        self.assertEqual(["d0:v0"], use["reaching_definitions"])

    def test_reaching_definitions_kill_prior_definition_in_same_block(self):
        body = [
            "    const/4 v0, 0x1",
            "    const/4 v0, 0x2",
            "    move v1, v0",
            "    return v1",
        ]
        cfg = AUDIT.build_smali_cfg(body)
        facts = AUDIT.analyze_register_dataflow(body, cfg)
        self.assertTrue(facts["complete"])
        use = next(x for x in facts["uses"] if x["register"] == "v0")
        self.assertEqual("resolved", use["resolution"])
        self.assertEqual(["d1:v0"], use["reaching_definitions"])

    def test_reaching_definitions_preserve_branch_ambiguity(self):
        body = [
            "    if-eqz v1, :else",
            "    const/4 v0, 0x1",
            "    goto :join",
            "    :else",
            "    const/4 v0, 0x2",
            "    :join",
            "    move v2, v0",
            "    return v2",
        ]
        cfg = AUDIT.build_smali_cfg(body)
        facts = AUDIT.analyze_register_dataflow(body, cfg)
        self.assertTrue(facts["complete"])
        use = next(x for x in facts["uses"] if x["register"] == "v0")
        self.assertEqual("ambiguous", use["resolution"])
        self.assertEqual(2, len(use["reaching_definitions"]))
        self.assertGreaterEqual(facts["ambiguous_use_count"], 1)

    def test_reaching_definitions_fail_closed_for_incomplete_cfg(self):
        body = ["    if-eqz v0, :missing", "    return-void"]
        cfg = AUDIT.build_smali_cfg(body)
        facts = AUDIT.analyze_register_dataflow(body, cfg)
        self.assertFalse(facts["complete"])
        self.assertEqual("incomplete-cfg-or-nonconvergence", facts["reason"])


    def test_method_descriptor_and_parameter_word_layout(self):
        parsed = AUDIT.parse_method_descriptor("(Ljava/lang/String;J[D)Ljava/lang/Object;")
        self.assertEqual(["Ljava/lang/String;", "J", "[D"], parsed["parameters"])
        self.assertEqual("Ljava/lang/Object;", parsed["return_type"])
        self.assertEqual(
            ["p0", "p1", "p2", "p3", "p4"],
            AUDIT.parameter_registers_for_method("public", "(Ljava/lang/String;J[D)V"),
        )
        self.assertEqual(
            ["p0", "p1", "p2"],
            AUDIT.parameter_registers_for_method("public static", "(Ljava/lang/String;J)V"),
        )

    def test_method_entry_parameters_seed_reaching_definitions(self):
        body = ["    move-object v0, p1", "    return-object v0"]
        cfg = AUDIT.build_smali_cfg(body)
        facts = AUDIT.analyze_register_dataflow(body, cfg, ["p0", "p1"])
        use = next(x for x in facts["uses"] if x["register"] == "p1")
        self.assertEqual("resolved", use["resolution"])
        self.assertEqual(["entry:p1"], use["reaching_definitions"])
        self.assertEqual(2, facts["parameter_definition_count"])

    def test_invoke_site_captures_argument_words_and_move_result(self):
        body = [
            "    invoke-virtual {p0, v1, v2, v3}, Lx/Worker;->send(Ljava/lang/String;J)Ljava/lang/String;",
            "    move-result-object v4",
            "    return-object v4",
        ]
        sites = AUDIT.extract_invoke_sites(body)
        self.assertEqual(1, len(sites))
        self.assertEqual(["p0", "v1", "v2", "v3"], sites[0]["registers"])
        self.assertEqual(0, sites[0]["instruction"])
        self.assertEqual(1, sites[0]["result_instruction"])
        self.assertEqual("v4", sites[0]["result_register"])

    def test_object_points_to_tracks_allocation_and_move_alias(self):
        body = [
            "    new-instance v0, Lx/State;",
            "    move-object v1, v0",
            "    iput-object v2, v0, Lx/State;->value:Ljava/lang/String;",
            "    iget-object v3, v1, Lx/State;->value:Ljava/lang/String;",
            "    return-void",
        ]
        cfg = AUDIT.build_smali_cfg(body)
        sites = AUDIT.extract_field_access_sites(body)
        facts = AUDIT.analyze_object_points_to(
            body, cfg, "Lx/Owner;", "run", "()V", "public static", sites)
        self.assertTrue(facts["complete"])
        self.assertEqual(2, facts["singleton_receiver_count"])
        self.assertEqual(1, len(facts["same_instance_groups"]))
        self.assertTrue(facts["same_instance_groups"][0]["same_instance_within_single_activation"])
        self.assertEqual(
            facts["field_receivers"][0]["identity"],
            facts["field_receivers"][1]["identity"],
        )

    def test_object_points_to_does_not_merge_distinct_allocations(self):
        body = [
            "    new-instance v0, Lx/State;",
            "    new-instance v1, Lx/State;",
            "    iput-object v2, v0, Lx/State;->value:Ljava/lang/String;",
            "    iget-object v3, v1, Lx/State;->value:Ljava/lang/String;",
            "    return-void",
        ]
        cfg = AUDIT.build_smali_cfg(body)
        sites = AUDIT.extract_field_access_sites(body)
        facts = AUDIT.analyze_object_points_to(
            body, cfg, "Lx/Owner;", "run", "()V", "public static", sites)
        self.assertTrue(facts["complete"])
        self.assertEqual(2, facts["singleton_receiver_count"])
        self.assertEqual([], facts["same_instance_groups"])
        self.assertNotEqual(
            facts["field_receivers"][0]["identity"],
            facts["field_receivers"][1]["identity"],
        )

    def test_object_points_to_rejects_reexecuted_loop_allocation_identity(self):
        body = [
            "    :loop",
            "    new-instance v0, Lx/State;",
            "    if-eqz v1, :exit",
            "    goto :loop",
            "    :exit",
            "    iput-object v2, v0, Lx/State;->value:Ljava/lang/String;",
            "    return-void",
        ]
        cfg = AUDIT.build_smali_cfg(body)
        sites = AUDIT.extract_field_access_sites(body)
        facts = AUDIT.analyze_object_points_to(
            body, cfg, "Lx/Owner;", "run", "()V", "public static", sites)
        self.assertTrue(facts["complete"])
        self.assertEqual(1, facts["cyclic_allocation_site_count"])
        self.assertEqual("unknown", facts["field_receivers"][0]["identity_status"])
        self.assertEqual([], facts["same_instance_groups"])

    def test_object_points_to_keeps_exceptional_instruction_states(self):
        body = [
            "    .catch Ljava/lang/Throwable; {:try_start .. :try_end} :handler",
            "    :try_start",
            "    new-instance v0, Lx/First;",
            "    new-instance v0, Lx/Second;",
            "    :try_end",
            "    goto :done",
            "    :handler",
            "    iput-object v1, v0, Lx/Holder;->value:Ljava/lang/Object;",
            "    :done",
            "    return-void",
        ]
        cfg = AUDIT.build_smali_cfg(body)
        sites = AUDIT.extract_field_access_sites(body)
        facts = AUDIT.analyze_object_points_to(
            body, cfg, "Lx/Owner;", "run", "()V", "public static", sites)
        self.assertTrue(cfg["complete"])
        self.assertTrue(facts["complete"])
        self.assertEqual(1, len(facts["field_receivers"]))
        # The handler can observe the state after either allocation instruction.
        # A single allocation-site identity here would be an unsound narrowing.
        self.assertNotEqual("singleton", facts["field_receivers"][0]["identity_status"])
        self.assertEqual([], facts["same_instance_groups"])

    def test_object_points_to_tracks_reference_parameters(self):
        body = [
            "    move-object v0, p1",
            "    iput-object v2, v0, Lx/State;->value:Ljava/lang/String;",
            "    iget-object v3, p1, Lx/State;->value:Ljava/lang/String;",
            "    return-void",
        ]
        cfg = AUDIT.build_smali_cfg(body)
        sites = AUDIT.extract_field_access_sites(body)
        facts = AUDIT.analyze_object_points_to(
            body, cfg, "Lx/Owner;", "run", "(Lx/State;)V", "public", sites)
        self.assertTrue(facts["complete"])
        self.assertEqual(1, len(facts["same_instance_groups"]))
        self.assertEqual("singleton", facts["field_receivers"][0]["identity_status"])

    def test_object_points_to_marks_unsupported_object_source_unknown(self):
        body = [
            "    iget-object v0, p0, Lx/Owner;->state:Lx/State;",
            "    iget-object v1, v0, Lx/State;->value:Ljava/lang/String;",
            "    return-void",
        ]
        cfg = AUDIT.build_smali_cfg(body)
        sites = AUDIT.extract_field_access_sites(body)
        facts = AUDIT.analyze_object_points_to(
            body, cfg, "Lx/Owner;", "run", "()V", "public", sites)
        self.assertTrue(facts["complete"])
        self.assertEqual("unknown", facts["field_receivers"][1]["identity_status"])
        self.assertEqual(1, facts["unknown_receiver_count"])

    def test_field_access_site_preserves_slot_and_instance_register(self):
        body = [
            "    iget-object v0, p1, Lx/State;->value:Ljava/lang/String;",
            "    iput-object v0, p1, Lx/State;->value:Ljava/lang/String;",
            "    sget-object v2, Lx/State;->STATIC:Ljava/lang/String;",
        ]
        sites = AUDIT.extract_field_access_sites(body)
        self.assertEqual(3, len(sites))
        self.assertEqual("read", sites[0]["access"])
        self.assertEqual("p1", sites[0]["object_register"])
        self.assertEqual("write", sites[1]["access"])
        self.assertEqual("v0", sites[1]["value_register"])
        self.assertTrue(sites[2]["static"])
        self.assertIsNone(sites[2]["object_register"])

    def test_interprocedural_argument_and_return_edges(self):
        caller = {
            "class": "Lx/Caller;", "name": "call", "descriptor": "()V", "component": "base",
            "register_dataflow": {
                "complete": True,
                "uses": [{"instruction": 0, "register": "v1",
                          "reaching_definitions": ["d0:v1"]}],
                "definitions": [],
            },
            "invoke_sites": [{
                "instruction": 0, "line": 10, "opcode": "invoke-static",
                "owner": "Lx/Worker;", "name": "echo",
                "descriptor": "(Ljava/lang/String;)Ljava/lang/String;",
                "registers": ["v1"], "result_instruction": 1, "result_register": "v2",
            }],
        }
        callee = {
            "class": "Lx/Worker;", "name": "echo",
            "descriptor": "(Ljava/lang/String;)Ljava/lang/String;", "component": "base",
            "register_dataflow": {
                "complete": True,
                "definitions": [{"id": "entry:p0", "register": "p0", "kind": "parameter"}],
                "uses": [{"instruction": 2, "register": "p0", "opcode": "return-object",
                          "reaching_definitions": ["entry:p0"]}],
            },
            "invoke_sites": [],
        }
        graph = AUDIT.build_interprocedural_value_graph([caller, callee])
        self.assertEqual(1, graph["summary"]["argument_edges"])
        self.assertEqual(1, graph["summary"]["return_edges"])
        self.assertEqual({"argument", "return"}, {x["kind"] for x in graph["edges"]})
        argument = next(x for x in graph["edges"] if x["kind"] == "argument")
        self.assertEqual("entry:p0", argument["to_parameter"])
        returned = next(x for x in graph["edges"] if x["kind"] == "return")
        self.assertEqual("d1:v2", returned["to_definition"])

    def test_interprocedural_value_edge_limit_is_explicit_and_reported(self):
        caller = {
            "class": "Lx/Caller;", "name": "call", "descriptor": "()V", "component": "base",
            "register_dataflow": {
                "complete": True,
                "uses": [{"instruction": 0, "register": "v1", "reaching_definitions": ["d0:v1"]}],
                "definitions": [],
            },
            "invoke_sites": [{
                "instruction": 0, "line": 10, "opcode": "invoke-static",
                "owner": "Lx/Worker;", "name": "echo",
                "descriptor": "(Ljava/lang/String;)Ljava/lang/String;",
                "registers": ["v1"], "result_instruction": None, "result_register": None,
            }],
        }
        callee = {
            "class": "Lx/Worker;", "name": "echo",
            "descriptor": "(Ljava/lang/String;)Ljava/lang/String;", "component": "base",
            "register_dataflow": {
                "complete": True,
                "definitions": [{"id": "entry:p0", "register": "p0", "kind": "parameter"}],
                "uses": [],
            },
            "invoke_sites": [],
        }
        with patch.object(AUDIT, "MAX_INTERPROCEDURAL_VALUE_EDGES", 0):
            graph = AUDIT.build_interprocedural_value_graph([caller, callee])
        self.assertEqual(1, graph["summary"]["edge_count"])
        self.assertEqual(0, graph["summary"]["stored_edge_count"])
        self.assertTrue(graph["summary"]["edges_truncated"])

    def test_interprocedural_graph_rejects_incomplete_method_dataflow(self):
        caller = {
            "class": "Lx/Caller;", "name": "call", "descriptor": "()V",
            "register_dataflow": {"complete": False, "uses": []},
            "invoke_sites": [{
                "instruction": 0, "line": 1, "opcode": "invoke-static",
                "owner": "Lx/Worker;", "name": "run", "descriptor": "()V",
                "registers": [], "result_instruction": None, "result_register": None,
            }],
        }
        callee = {
            "class": "Lx/Worker;", "name": "run", "descriptor": "()V",
            "register_dataflow": {"complete": True, "uses": [], "definitions": []},
            "invoke_sites": [],
        }
        graph = AUDIT.build_interprocedural_value_graph([caller, callee])
        self.assertEqual(1, graph["summary"]["incomplete_dataflow_call_sites"])
        self.assertEqual([], graph["edges"])


    def test_interprocedural_points_to_projects_caller_allocation_to_callee_receiver(self):
        caller_body = [
            "    new-instance v0, Lx/Thing;",
            "    invoke-static {v0}, Lx/Worker;->consume(Lx/Thing;)V",
            "    return-void",
        ]
        caller_cfg = AUDIT.build_smali_cfg(caller_body)
        caller_invokes = AUDIT.extract_invoke_sites(caller_body)
        caller_pts = AUDIT.analyze_object_points_to(
            caller_body, caller_cfg, "Lx/Caller;", "run", "()V", "static",
            [], caller_invokes)
        callee_body = [
            "    iget-object v0, p0, Lx/Thing;->value:Ljava/lang/Object;",
            "    return-object v0",
        ]
        callee_cfg = AUDIT.build_smali_cfg(callee_body)
        callee_fields = AUDIT.extract_field_access_sites(callee_body)
        callee_pts = AUDIT.analyze_object_points_to(
            callee_body, callee_cfg, "Lx/Worker;", "consume",
            "(Lx/Thing;)V", "static", callee_fields, [])
        caller = {
            "class": "Lx/Caller;", "name": "run", "descriptor": "()V",
            "component": "base", "invoke_sites": caller_invokes,
            "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
            "object_points_to": caller_pts,
        }
        callee = {
            "class": "Lx/Worker;", "name": "consume",
            "descriptor": "(Lx/Thing;)V", "component": "base",
            "object_points_to": callee_pts,
        }
        graph = AUDIT.build_interprocedural_points_to_graph([caller, callee])
        self.assertEqual(1, graph["summary"]["resolved_call_contexts"])
        self.assertEqual(1, graph["summary"]["singleton_context_receiver_count"])
        receiver = graph["contextual_receivers"][0]
        self.assertEqual("singleton", receiver["identity_status"])
        self.assertEqual(caller_pts["invoke_arguments"][0]["points_to"][0], receiver["identity"])
        self.assertEqual("bounded-call-string-context", receiver["identity_scope"])
        self.assertFalse(receiver["runtime_identity_proven"])

    def test_interprocedural_points_to_propagates_identity_across_two_call_edges(self):
        a_body = [
            "    new-instance v0, Lx/Thing;",
            "    invoke-static {v0}, Lx/Worker;->middle(Lx/Thing;)V",
            "    return-void",
        ]
        b_body = [
            "    invoke-static {p0}, Lx/Sink;->consume(Lx/Thing;)V",
            "    return-void",
        ]
        c_body = [
            "    iget-object v0, p0, Lx/Thing;->value:Ljava/lang/Object;",
            "    return-void",
        ]
        def facts(owner, name, descriptor, access, body):
            cfg = AUDIT.build_smali_cfg(body)
            invokes = AUDIT.extract_invoke_sites(body)
            fields = AUDIT.extract_field_access_sites(body)
            pts = AUDIT.analyze_object_points_to(
                body, cfg, owner, name, descriptor, access, fields, invokes)
            return {
                "class": owner, "name": name, "descriptor": descriptor,
                "component": "base", "invoke_sites": invokes,
                "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
                "object_points_to": pts,
            }
        methods = [
            facts("Lx/Caller;", "start", "()V", "static", a_body),
            facts("Lx/Worker;", "middle", "(Lx/Thing;)V", "static", b_body),
            facts("Lx/Sink;", "consume", "(Lx/Thing;)V", "static", c_body),
        ]
        graph = AUDIT.build_interprocedural_points_to_graph(methods, max_call_depth=4)
        terminal = [
            row for row in graph["contextual_receivers"]
            if row["callee"] == "Lx/Sink;->consume(Lx/Thing;)V"
            and row["field"] == "Lx/Thing;->value:Ljava/lang/Object;"
            and row["identity_status"] == "singleton"
        ]
        self.assertTrue(terminal)
        self.assertTrue(any(row["call_depth"] == 2 for row in terminal))
        self.assertTrue(graph["summary"]["context_expansion_complete"])
        self.assertFalse(terminal[0]["runtime_identity_proven"])
        self.assertEqual("bounded-call-string-context", terminal[0]["identity_scope"])

    def test_interprocedural_points_to_propagates_factory_return_to_next_callsite(self):
        def method(owner, name, descriptor, body, access="static"):
            cfg = AUDIT.build_smali_cfg(body)
            invokes = AUDIT.extract_invoke_sites(body)
            fields = AUDIT.extract_field_access_sites(body)
            pts = AUDIT.analyze_object_points_to(
                body, cfg, owner, name, descriptor, access, fields, invokes)
            return {
                "class": owner, "name": name, "descriptor": descriptor,
                "component": "base", "invoke_sites": invokes,
                "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
                "object_points_to": pts,
                "control_flow": {
                    "branch_count": 0, "return_count": sum(
                        1 for line in body
                        if AUDIT.OP_RE.match(line) and AUDIT.OP_RE.match(line).group(1).startswith("return")
                    ), "cfg": cfg,
                },
            }
        caller = method("Lx/Caller;", "run", "()V", [
            "    invoke-static {}, Lx/Factory;->make()Lx/Thing;",
            "    move-result-object v0",
            "    iget-object v2, v0, Lx/Thing;->value:Ljava/lang/Object;",
            "    invoke-static {v0}, Lx/Sink;->consume(Lx/Thing;)V",
            "    return-void",
        ])
        factory = method("Lx/Factory;", "make", "()Lx/Thing;", [
            "    new-instance v0, Lx/Thing;",
            "    return-object v0",
        ])
        sink = method("Lx/Sink;", "consume", "(Lx/Thing;)V", [
            "    iget-object v0, p0, Lx/Thing;->value:Ljava/lang/Object;",
            "    return-void",
        ])
        graph = AUDIT.build_interprocedural_points_to_graph([caller, factory, sink])
        receiver = next(
            row for row in graph["contextual_receivers"]
            if row["callee"] == "Lx/Sink;->consume(Lx/Thing;)V"
        )
        self.assertEqual("singleton", receiver["identity_status"])
        self.assertTrue(receiver["identity"].startswith("context:"))
        factory_call = next(
            row for row in graph["call_contexts"]
            if row["callee"] == "Lx/Factory;->make()Lx/Thing;"
        )
        self.assertEqual("singleton", factory_call["return_value"]["identity_status"])
        self.assertEqual(1, graph["summary"]["return_identity_propagations"])
        direct_receiver = next(
            row for row in graph["contextual_receivers"]
            if row["callee"] == "Lx/Caller;->run()V"
            and row["field"] == "Lx/Thing;->value:Ljava/lang/Object;"
        )
        self.assertEqual("singleton", direct_receiver["identity_status"])
        self.assertEqual(receiver["identity"], direct_receiver["identity"])

    def test_interprocedural_points_to_composes_wrapper_return_summaries(self):
        def method(owner, name, descriptor, body):
            cfg = AUDIT.build_smali_cfg(body)
            invokes = AUDIT.extract_invoke_sites(body)
            fields = AUDIT.extract_field_access_sites(body)
            pts = AUDIT.analyze_object_points_to(
                body, cfg, owner, name, descriptor, "static", fields, invokes)
            return {
                "class": owner, "name": name, "descriptor": descriptor,
                "component": "base", "invoke_sites": invokes,
                "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
                "object_points_to": pts,
                "control_flow": {
                    "branch_count": 0, "return_count": sum(
                        1 for line in body
                        if AUDIT.OP_RE.match(line) and AUDIT.OP_RE.match(line).group(1).startswith("return")
                    ), "cfg": cfg,
                },
            }
        caller = method("Lx/Caller;", "run", "()V", [
            "    invoke-static {}, Lx/Wrapper;->make()Lx/Thing;",
            "    move-result-object v0",
            "    invoke-static {v0}, Lx/Sink;->consume(Lx/Thing;)V",
            "    return-void",
        ])
        wrapper = method("Lx/Wrapper;", "make", "()Lx/Thing;", [
            "    invoke-static {}, Lx/Factory;->make()Lx/Thing;",
            "    move-result-object v0",
            "    return-object v0",
        ])
        factory = method("Lx/Factory;", "make", "()Lx/Thing;", [
            "    new-instance v0, Lx/Thing;",
            "    return-object v0",
        ])
        sink = method("Lx/Sink;", "consume", "(Lx/Thing;)V", [
            "    iget-object v0, p0, Lx/Thing;->value:Ljava/lang/Object;",
            "    return-void",
        ])
        graph = AUDIT.build_interprocedural_points_to_graph(
            [caller, wrapper, factory, sink], max_call_depth=4)
        receiver = next(
            row for row in graph["contextual_receivers"]
            if row["callee"] == "Lx/Sink;->consume(Lx/Thing;)V"
        )
        self.assertEqual("singleton", receiver["identity_status"])
        self.assertTrue(receiver["identity"].startswith("context:"))
        wrapper_call = next(
            row for row in graph["call_contexts"]
            if row["caller"] == "Lx/Caller;->run()V"
            and row["callee"] == "Lx/Wrapper;->make()Lx/Thing;"
        )
        self.assertEqual("singleton", wrapper_call["return_value"]["identity_status"])
        self.assertGreaterEqual(graph["summary"]["return_summary_compositions"], 1)
        self.assertTrue(graph["summary"]["context_expansion_complete"])

    def test_interprocedural_points_to_propagates_returned_formal_identity(self):
        def method(owner, name, descriptor, body):
            cfg = AUDIT.build_smali_cfg(body)
            invokes = AUDIT.extract_invoke_sites(body)
            fields = AUDIT.extract_field_access_sites(body)
            pts = AUDIT.analyze_object_points_to(
                body, cfg, owner, name, descriptor, "static", fields, invokes)
            return {
                "class": owner, "name": name, "descriptor": descriptor,
                "component": "base", "invoke_sites": invokes,
                "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
                "object_points_to": pts,
                "control_flow": {
                    "branch_count": 0, "return_count": sum(
                        1 for line in body
                        if AUDIT.OP_RE.match(line) and AUDIT.OP_RE.match(line).group(1).startswith("return")
                    ), "cfg": cfg,
                },
            }
        caller = method("Lx/Caller;", "run", "()V", [
            "    new-instance v0, Lx/Thing;",
            "    invoke-static {v0}, Lx/Identity;->echo(Lx/Thing;)Lx/Thing;",
            "    move-result-object v1",
            "    invoke-static {v1}, Lx/Sink;->consume(Lx/Thing;)V",
            "    return-void",
        ])
        identity = method("Lx/Identity;", "echo", "(Lx/Thing;)Lx/Thing;", [
            "    return-object p0",
        ])
        sink = method("Lx/Sink;", "consume", "(Lx/Thing;)V", [
            "    iget-object v0, p0, Lx/Thing;->value:Ljava/lang/Object;",
            "    return-void",
        ])
        graph = AUDIT.build_interprocedural_points_to_graph([caller, identity, sink])
        receiver = next(
            row for row in graph["contextual_receivers"]
            if row["callee"] == "Lx/Sink;->consume(Lx/Thing;)V"
        )
        self.assertEqual("singleton", receiver["identity_status"])
        self.assertTrue(receiver["identity"].startswith("alloc:Lx/Caller;->run()V#0:"))
        self.assertEqual(1, graph["summary"]["return_identity_propagations"])

    def test_interprocedural_points_to_does_not_upgrade_unknown_factory_return(self):
        def method(owner, name, descriptor, body):
            cfg = AUDIT.build_smali_cfg(body)
            invokes = AUDIT.extract_invoke_sites(body)
            fields = AUDIT.extract_field_access_sites(body)
            pts = AUDIT.analyze_object_points_to(
                body, cfg, owner, name, descriptor, "static", fields, invokes)
            return {
                "class": owner, "name": name, "descriptor": descriptor,
                "component": "base", "invoke_sites": invokes,
                "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
                "object_points_to": pts,
                "control_flow": {
                    "branch_count": 0, "return_count": sum(
                        1 for line in body
                        if AUDIT.OP_RE.match(line) and AUDIT.OP_RE.match(line).group(1).startswith("return")
                    ), "cfg": cfg,
                },
            }
        caller = method("Lx/Caller;", "run", "()V", [
            "    invoke-static {}, Lx/Factory;->make()Lx/Thing;",
            "    move-result-object v0",
            "    invoke-static {v0}, Lx/Sink;->consume(Lx/Thing;)V",
            "    return-void",
        ])
        factory = method("Lx/Factory;", "make", "()Lx/Thing;", [
            "    sget-object v0, Lx/Factory;->cached:Lx/Thing;",
            "    return-object v0",
        ])
        sink = method("Lx/Sink;", "consume", "(Lx/Thing;)V", [
            "    iget-object v0, p0, Lx/Thing;->value:Ljava/lang/Object;",
            "    return-void",
        ])
        graph = AUDIT.build_interprocedural_points_to_graph([caller, factory, sink])
        receiver = next(
            row for row in graph["contextual_receivers"]
            if row["callee"] == "Lx/Sink;->consume(Lx/Thing;)V"
        )
        self.assertEqual("unknown", receiver["identity_status"])
        self.assertEqual(0, graph["summary"]["return_identity_propagations"])
        self.assertGreaterEqual(graph["summary"]["return_identity_unknown_count"], 1)

    def test_interprocedural_points_to_cuts_recursive_return_summary_composition(self):
        body = [
            "    invoke-static {}, Lx/Recursive;->make()Lx/Thing;",
            "    move-result-object v0",
            "    return-object v0",
        ]
        cfg = AUDIT.build_smali_cfg(body)
        invokes = AUDIT.extract_invoke_sites(body)
        pts = AUDIT.analyze_object_points_to(
            body, cfg, "Lx/Recursive;", "make", "()Lx/Thing;",
            "static", [], invokes)
        method = {
            "class": "Lx/Recursive;", "name": "make",
            "descriptor": "()Lx/Thing;", "component": "base",
            "invoke_sites": invokes, "invoke_sites_truncated": False,
            "invoke_sites_incomplete": False, "object_points_to": pts,
            "control_flow": {"branch_count": 0, "return_count": 1, "cfg": cfg},
        }
        graph = AUDIT.build_interprocedural_points_to_graph([method])
        self.assertGreaterEqual(graph["summary"]["return_summary_recursive_cuts"], 1)
        self.assertFalse(graph["summary"]["context_expansion_complete"])
        self.assertFalse(graph["summary"]["root_diagnostics"]["top_hot_roots"][0]["context_expansion_complete"])
        self.assertGreaterEqual(
            graph["summary"]["root_diagnostics"]["top_hot_roots"][0]["return_summary_recursive_cuts"], 1
        )
        self.assertFalse(graph["summary"]["recursive_fixed_point"])

    def test_interprocedural_points_to_cuts_recursive_contexts_fail_closed(self):
        body = [
            "    invoke-static {p0}, Lx/Recursive;->step(Lx/Thing;)V",
            "    return-void",
        ]
        cfg = AUDIT.build_smali_cfg(body)
        invokes = AUDIT.extract_invoke_sites(body)
        pts = AUDIT.analyze_object_points_to(
            body, cfg, "Lx/Recursive;", "step", "(Lx/Thing;)V",
            "static", [], invokes)
        method = {
            "class": "Lx/Recursive;", "name": "step",
            "descriptor": "(Lx/Thing;)V", "component": "base",
            "invoke_sites": invokes, "invoke_sites_truncated": False,
            "invoke_sites_incomplete": False, "object_points_to": pts,
        }
        graph = AUDIT.build_interprocedural_points_to_graph([method])
        self.assertEqual(1, graph["summary"]["recursive_contexts_cut"])
        self.assertFalse(graph["summary"]["context_expansion_complete"])
        self.assertFalse(graph["summary"]["recursive_fixed_point"])

    def test_interprocedural_points_to_keeps_distinct_callsite_contexts_separate(self):
        caller_body = [
            "    new-instance v0, Lx/Thing;",
            "    invoke-static {v0}, Lx/Worker;->consume(Lx/Thing;)V",
            "    new-instance v1, Lx/Thing;",
            "    invoke-static {v1}, Lx/Worker;->consume(Lx/Thing;)V",
            "    return-void",
        ]
        caller_cfg = AUDIT.build_smali_cfg(caller_body)
        caller_invokes = AUDIT.extract_invoke_sites(caller_body)
        caller_pts = AUDIT.analyze_object_points_to(
            caller_body, caller_cfg, "Lx/Caller;", "run", "()V", "static",
            [], caller_invokes)
        callee_body = [
            "    iget-object v0, p0, Lx/Thing;->value:Ljava/lang/Object;",
            "    return-object v0",
        ]
        callee_cfg = AUDIT.build_smali_cfg(callee_body)
        callee_fields = AUDIT.extract_field_access_sites(callee_body)
        callee_pts = AUDIT.analyze_object_points_to(
            callee_body, callee_cfg, "Lx/Worker;", "consume",
            "(Lx/Thing;)V", "static", callee_fields, [])
        caller = {
            "class": "Lx/Caller;", "name": "run", "descriptor": "()V",
            "component": "base", "invoke_sites": caller_invokes,
            "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
            "object_points_to": caller_pts,
        }
        callee = {
            "class": "Lx/Worker;", "name": "consume",
            "descriptor": "(Lx/Thing;)V", "component": "base",
            "object_points_to": callee_pts,
        }
        graph = AUDIT.build_interprocedural_points_to_graph([caller, callee])
        self.assertEqual(2, graph["summary"]["resolved_call_contexts"])
        self.assertEqual(2, graph["summary"]["singleton_context_receiver_count"])
        identities = [x["identity"] for x in graph["contextual_receivers"]]
        self.assertEqual(2, len(set(identities)))
        self.assertNotEqual(
            graph["contextual_receivers"][0]["context_id"],
            graph["contextual_receivers"][1]["context_id"])

    def test_interprocedural_points_to_does_not_upgrade_unknown_actual(self):
        caller_body = [
            "    move-result-object v0",
            "    invoke-static {v0}, Lx/Worker;->consume(Lx/Thing;)V",
            "    return-void",
        ]
        caller_cfg = AUDIT.build_smali_cfg(caller_body)
        caller_invokes = AUDIT.extract_invoke_sites(caller_body)
        caller_pts = AUDIT.analyze_object_points_to(
            caller_body, caller_cfg, "Lx/Caller;", "run", "()V", "static",
            [], caller_invokes)
        callee_body = [
            "    iget-object v0, p0, Lx/Thing;->value:Ljava/lang/Object;",
            "    return-object v0",
        ]
        callee_cfg = AUDIT.build_smali_cfg(callee_body)
        callee_fields = AUDIT.extract_field_access_sites(callee_body)
        callee_pts = AUDIT.analyze_object_points_to(
            callee_body, callee_cfg, "Lx/Worker;", "consume",
            "(Lx/Thing;)V", "static", callee_fields, [])
        caller = {
            "class": "Lx/Caller;", "name": "run", "descriptor": "()V",
            "component": "base", "invoke_sites": caller_invokes,
            "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
            "object_points_to": caller_pts,
        }
        callee = {
            "class": "Lx/Worker;", "name": "consume",
            "descriptor": "(Lx/Thing;)V", "component": "base",
            "object_points_to": callee_pts,
        }
        graph = AUDIT.build_interprocedural_points_to_graph([caller, callee])
        self.assertEqual(1, graph["summary"]["resolved_call_contexts"])
        self.assertEqual("unknown", graph["contextual_receivers"][0]["identity_status"])
        self.assertEqual(0, graph["summary"]["singleton_context_receiver_count"])

    def test_field_slot_index_groups_exact_field_without_claiming_instance_identity(self):
        methods = [
            {
                "class": "Lx/Writer;", "name": "write", "descriptor": "()V",
                "component": "base",
                "field_access_sites": [{
                    "field": "Lx/State;->value:Ljava/lang/String;", "access": "write",
                    "instruction": 2, "line": 3, "opcode": "iput-object",
                    "value_register": "v0", "object_register": "p1", "static": False,
                }],
            },
            {
                "class": "Lx/Reader;", "name": "read", "descriptor": "()V",
                "component": "base",
                "field_access_sites": [{
                    "field": "Lx/State;->value:Ljava/lang/String;", "access": "read",
                    "instruction": 1, "line": 2, "opcode": "iget-object",
                    "value_register": "v0", "object_register": "p1", "static": False,
                }],
            },
        ]
        groups = AUDIT.build_field_slot_index(methods)
        self.assertEqual(1, len(groups))
        self.assertEqual(1, groups[0]["cross_method_pair_count"])
        self.assertFalse(groups[0]["instance_identity_confirmed"])


    def test_wide_register_instructions_fail_closed_until_pair_model_exists(self):
        facts = AUDIT.analyze_register_use_def([
            "    move-wide v0, v2",
            "    return-wide v0",
        ])
        self.assertFalse(facts["complete"])
        self.assertEqual(2, facts["unknown_opcode_count"])
        self.assertTrue(all(
            item["reason"] == "wide-register-pair-not-modeled"
            for item in facts["unknown_opcodes"]
        ))


    def test_invoke_range_site_expands_register_words(self):
        body = [
            "    invoke-static/range {v4 .. v7}, Lx/Worker;->consume(JLjava/lang/String;)V",
            "    return-void",
        ]
        sites = AUDIT.extract_invoke_sites(body)
        self.assertEqual(["v4", "v5", "v6", "v7"], sites[0]["registers"])

    def test_interprocedural_resolution_requires_exact_full_descriptor(self):
        caller = {
            "class": "Lx/Caller;", "name": "call", "descriptor": "()V",
            "register_dataflow": {"complete": True, "uses": []},
            "invoke_sites": [{
                "instruction": 0, "line": 1, "opcode": "invoke-static",
                "owner": "Lx/Worker;", "name": "echo",
                "descriptor": "(Ljava/lang/String;)Ljava/lang/String;",
                "registers": ["v0"], "result_instruction": None, "result_register": None,
            }],
        }
        overload = {
            "class": "Lx/Worker;", "name": "echo",
            "descriptor": "(Ljava/lang/Object;)Ljava/lang/Object;",
            "register_dataflow": {"complete": True, "uses": [], "definitions": []},
            "invoke_sites": [],
        }
        graph = AUDIT.build_interprocedural_value_graph([caller, overload])
        self.assertEqual(1, graph["summary"]["unresolved_call_sites"])
        self.assertEqual(0, graph["summary"]["resolved_call_sites"])
        self.assertEqual([], graph["edges"])


    def test_custom_and_polymorphic_invokes_are_not_guessed_as_direct_calls(self):
        body = [
            "    invoke-custom {v0}, call_site_0",
            "    invoke-polymorphic {v0, v1}, Ljava/lang/invoke/MethodHandle;->invokeExact([Ljava/lang/Object;)Ljava/lang/Object;, (Ljava/lang/String;)V",
        ]
        self.assertEqual([], AUDIT.extract_invoke_sites(body))


    def test_nested_return_summary_does_not_survive_intervening_register_write(self):
        def method(owner, name, descriptor, body):
            cfg = AUDIT.build_smali_cfg(body)
            invokes = AUDIT.extract_invoke_sites(body)
            fields = AUDIT.extract_field_access_sites(body)
            pts = AUDIT.analyze_object_points_to(
                body, cfg, owner, name, descriptor, "static", fields, invokes)
            return {
                "class": owner, "name": name, "descriptor": descriptor,
                "component": "base", "invoke_sites": invokes,
                "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
                "object_points_to": pts,
                "control_flow": {
                    "branch_count": sum(
                        1 for line in body if AUDIT.BRANCH_RE.match(line)
                    ),
                    "return_count": sum(
                        1 for line in body
                        if AUDIT.OP_RE.match(line)
                        and AUDIT.OP_RE.match(line).group(1).startswith("return")
                    ),
                    "cfg": cfg,
                },
            }

        caller = method("Lx/Caller;", "run", "()V", [
            "    invoke-static {}, Lx/Wrapper;->make()Lx/Thing;",
            "    move-result-object v0",
            "    invoke-static {v0}, Lx/Sink;->consume(Lx/Thing;)V",
            "    return-void",
        ])
        wrapper = method("Lx/Wrapper;", "make", "()Lx/Thing;", [
            "    invoke-static {}, Lx/Factory;->make()Lx/Thing;",
            "    move-result-object v0",
            "    new-instance v0, Lx/Thing;",
            "    return-object v0",
        ])
        factory = method("Lx/Factory;", "make", "()Lx/Thing;", [
            "    new-instance v0, Lx/Thing;",
            "    return-object v0",
        ])
        sink = method("Lx/Sink;", "consume", "(Lx/Thing;)V", [
            "    iget-object v0, p0, Lx/Thing;->value:Ljava/lang/Object;",
            "    return-void",
        ])
        graph = AUDIT.build_interprocedural_points_to_graph(
            [caller, wrapper, factory, sink])
        wrapper_call = next(
            row for row in graph["call_contexts"]
            if row["caller"] == "Lx/Caller;->run()V"
            and row["callee"] == "Lx/Wrapper;->make()Lx/Thing;"
        )
        self.assertEqual("singleton", wrapper_call["return_value"]["identity_status"])
        self.assertIn("Lx/Wrapper;->make()Lx/Thing;", wrapper_call["return_value"]["points_to"][0])
        self.assertNotIn("Lx/Factory;->make()Lx/Thing;", wrapper_call["return_value"]["points_to"][0])

    def test_branching_wrapper_does_not_use_nested_return_override(self):
        def method(owner, name, descriptor, body):
            cfg = AUDIT.build_smali_cfg(body)
            invokes = AUDIT.extract_invoke_sites(body)
            fields = AUDIT.extract_field_access_sites(body)
            pts = AUDIT.analyze_object_points_to(
                body, cfg, owner, name, descriptor, "static", fields, invokes)
            return {
                "class": owner, "name": name, "descriptor": descriptor,
                "component": "base", "invoke_sites": invokes,
                "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
                "object_points_to": pts,
                "control_flow": {
                    "branch_count": sum(
                        1 for line in body if AUDIT.BRANCH_RE.match(line)
                    ),
                    "return_count": sum(
                        1 for line in body
                        if AUDIT.OP_RE.match(line)
                        and AUDIT.OP_RE.match(line).group(1).startswith("return")
                    ),
                    "cfg": cfg,
                },
            }

        caller = method("Lx/Caller;", "run", "()V", [
            "    invoke-static {}, Lx/Wrapper;->make(Z)Lx/Thing;",
            "    move-result-object v0",
            "    return-void",
        ])
        wrapper = method("Lx/Wrapper;", "make", "(Z)Lx/Thing;", [
            "    invoke-static {}, Lx/Factory;->make()Lx/Thing;",
            "    move-result-object v0",
            "    if-eqz p0, :alternate",
            "    return-object v0",
            "    :alternate",
            "    return-object v0",
        ])
        factory = method("Lx/Factory;", "make", "()Lx/Thing;", [
            "    new-instance v0, Lx/Thing;",
            "    return-object v0",
        ])
        graph = AUDIT.build_interprocedural_points_to_graph(
            [caller, wrapper, factory])
        wrapper_call = next(
            row for row in graph["call_contexts"]
            if row["callee"] == "Lx/Wrapper;->make(Z)Lx/Thing;"
        )
        self.assertEqual("unknown", wrapper_call["return_value"]["identity_status"])
        self.assertEqual([], wrapper_call["return_value"]["points_to"])


    def test_factory_with_distinct_return_allocations_stays_multiple(self):
        def method(owner, name, descriptor, body):
            cfg = AUDIT.build_smali_cfg(body)
            invokes = AUDIT.extract_invoke_sites(body)
            fields = AUDIT.extract_field_access_sites(body)
            pts = AUDIT.analyze_object_points_to(
                body, cfg, owner, name, descriptor, "static", fields, invokes)
            return {
                "class": owner, "name": name, "descriptor": descriptor,
                "component": "base", "invoke_sites": invokes,
                "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
                "object_points_to": pts,
                "control_flow": {
                    "branch_count": sum(
                        1 for line in body if AUDIT.BRANCH_RE.match(line)
                    ),
                    "return_count": sum(
                        1 for line in body
                        if AUDIT.OP_RE.match(line)
                        and AUDIT.OP_RE.match(line).group(1).startswith("return")
                    ),
                    "cfg": cfg,
                },
            }

        caller = method("Lx/Caller;", "run", "()V", [
            "    invoke-static {v0}, Lx/Factory;->make(I)Lx/Thing;",
            "    move-result-object v1",
            "    invoke-static {v1}, Lx/Sink;->consume(Lx/Thing;)V",
            "    return-void",
        ])
        factory = method("Lx/Factory;", "make", "(I)Lx/Thing;", [
            "    if-eqz p0, :second",
            "    new-instance v0, Lx/Thing;",
            "    return-object v0",
            "    :second",
            "    new-instance v0, Lx/Thing;",
            "    return-object v0",
        ])
        sink = method("Lx/Sink;", "consume", "(Lx/Thing;)V", [
            "    iget-object v0, p0, Lx/Thing;->value:Ljava/lang/Object;",
            "    return-void",
        ])
        graph = AUDIT.build_interprocedural_points_to_graph(
            [caller, factory, sink])
        factory_call = next(
            row for row in graph["call_contexts"]
            if row["callee"] == "Lx/Factory;->make(I)Lx/Thing;"
        )
        self.assertEqual("multiple", factory_call["return_value"]["identity_status"])
        self.assertEqual(2, len(factory_call["return_value"]["points_to"]))
        sink_receiver = next(
            row for row in graph["contextual_receivers"]
            if row["callee"] == "Lx/Sink;->consume(Lx/Thing;)V"
        )
        self.assertNotEqual("singleton", sink_receiver["identity_status"])


class InterproceduralExceptionReturnTest(unittest.TestCase):
    def test_exceptional_wrapper_does_not_project_nested_return_identity(self):
        def method(owner, name, descriptor, body):
            cfg = AUDIT.build_smali_cfg(body)
            invokes = AUDIT.extract_invoke_sites(body)
            fields = AUDIT.extract_field_access_sites(body)
            pts = AUDIT.analyze_object_points_to(
                body, cfg, owner, name, descriptor, "static", fields, invokes)
            return {
                "class": owner, "name": name, "descriptor": descriptor,
                "component": "base", "invoke_sites": invokes,
                "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
                "object_points_to": pts,
                "control_flow": {
                    "branch_count": sum(
                        1 for line in body if AUDIT.BRANCH_RE.match(line)
                    ),
                    "return_count": sum(
                        1 for line in body
                        if AUDIT.OP_RE.match(line)
                        and AUDIT.OP_RE.match(line).group(1).startswith("return")
                    ),
                    "cfg": cfg,
                },
            }

        caller = method("Lx/Caller;", "run", "()V", [
            "    invoke-static {}, Lx/Wrapper;->make()Lx/Thing;",
            "    move-result-object v0",
            "    invoke-static {v0}, Lx/Sink;->consume(Lx/Thing;)V",
            "    return-void",
        ])
        wrapper = method("Lx/Wrapper;", "make", "()Lx/Thing;", [
            "    invoke-static {}, Lx/Factory;->make()Lx/Thing;",
            "    move-result-object v0",
            "    :try_start_0",
            "    invoke-static {}, Lx/Worker;->mayThrow()V",
            "    :try_end_0",
            "    return-object v0",
            "    :catch_0",
            "    move-exception v1",
            "    return-object v0",
            "    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0",
        ])
        factory = method("Lx/Factory;", "make", "()Lx/Thing;", [
            "    new-instance v0, Lx/Thing;",
            "    return-object v0",
        ])
        worker = method("Lx/Worker;", "mayThrow", "()V", ["    return-void"])
        sink = method("Lx/Sink;", "consume", "(Lx/Thing;)V", [
            "    iget-object v0, p0, Lx/Thing;->value:Ljava/lang/Object;",
            "    return-void",
        ])

        self.assertTrue(any(
            edge["kind"] == "exception"
            for edge in wrapper["control_flow"]["cfg"]["edges"]
        ))
        self.assertEqual(0, wrapper["control_flow"]["branch_count"])

        graph = AUDIT.build_interprocedural_points_to_graph(
            [caller, wrapper, factory, worker, sink]
        )
        wrapper_call = next(
            row for row in graph["call_contexts"]
            if row["callee"] == "Lx/Wrapper;->make()Lx/Thing;"
        )
        self.assertEqual("unknown", wrapper_call["return_value"]["identity_status"])
        sink_receiver = next(
            row for row in graph["contextual_receivers"]
            if row["callee"] == "Lx/Sink;->consume(Lx/Thing;)V"
        )
        self.assertEqual("unknown", sink_receiver["identity_status"])
        self.assertEqual(0, graph["summary"]["return_identity_propagations"])


class CallerControlFlowReturnBoundaryTest(unittest.TestCase):
    def test_caller_branch_after_move_result_blocks_return_identity_projection(self):
        def method(owner, name, descriptor, body):
            cfg = AUDIT.build_smali_cfg(body)
            invokes = AUDIT.extract_invoke_sites(body)
            fields = AUDIT.extract_field_access_sites(body)
            pts = AUDIT.analyze_object_points_to(
                body, cfg, owner, name, descriptor, "static", fields, invokes)
            return {
                "class": owner, "name": name, "descriptor": descriptor,
                "component": "base", "invoke_sites": invokes,
                "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
                "object_points_to": pts,
                "control_flow": {
                    "branch_count": sum(
                        1 for line in body if AUDIT.BRANCH_RE.match(line)
                    ),
                    "return_count": sum(
                        1 for line in body
                        if AUDIT.OP_RE.match(line)
                        and AUDIT.OP_RE.match(line).group(1).startswith("return")
                    ),
                    "cfg": cfg,
                },
            }

        caller = method("Lx/Caller;", "run", "()V", [
            "    invoke-static {}, Lx/Factory;->make()Lx/Thing;",
            "    move-result-object v0",
            "    if-eqz v1, :alternate",
            "    goto :join",
            "    :alternate",
            "    const/4 v2, 0x0",
            "    :join",
            "    invoke-static {v0}, Lx/Sink;->consume(Lx/Thing;)V",
            "    return-void",
        ])
        factory = method("Lx/Factory;", "make", "()Lx/Thing;", [
            "    new-instance v0, Lx/Thing;",
            "    return-object v0",
        ])
        sink = method("Lx/Sink;", "consume", "(Lx/Thing;)V", [
            "    iget-object v0, p0, Lx/Thing;->value:Ljava/lang/Object;",
            "    return-void",
        ])

        self.assertGreater(caller["control_flow"]["branch_count"], 0)
        graph = AUDIT.build_interprocedural_points_to_graph([caller, factory, sink])
        factory_call = next(
            row for row in graph["call_contexts"]
            if row["callee"] == "Lx/Factory;->make()Lx/Thing;"
        )
        self.assertEqual("singleton", factory_call["return_value"]["identity_status"])
        self.assertEqual(0, graph["summary"]["return_identity_propagations"])
        sink_call = next(
            row for row in graph["call_contexts"]
            if row["callee"] == "Lx/Sink;->consume(Lx/Thing;)V"
        )
        self.assertEqual("unknown", sink_call["arguments"][0]["identity_status"])
        sink_receiver = next(
            row for row in graph["contextual_receivers"]
            if row["callee"] == "Lx/Sink;->consume(Lx/Thing;)V"
        )
        self.assertEqual("unknown", sink_receiver["identity_status"])


    def test_interprocedural_points_to_reports_root_and_record_budget_diagnostics(self):
        def method(owner, name, invokes=None, roles=None):
            return {
                "class": owner, "name": name, "descriptor": "()V",
                "component": "base", "roles": roles or [],
                "invoke_sites": invokes or [],
                "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
                "object_points_to": {
                    "complete": True, "invoke_arguments": [],
                    "field_receivers": [], "return_values": [],
                    "instruction_writes": [],
                },
            }

        def call(target, instruction):
            return {
                "instruction": instruction, "line": instruction + 1,
                "owner": target, "name": "run", "descriptor": "()V",
                "opcode": "invoke-static", "registers": [],
                "result_instruction": None, "result_register": None,
            }

        caller = method(
            "Lx/Caller;", "entry",
            [call("Lx/First;", 0), call("Lx/Second;", 1)],
            roles=[{"role": "request", "anchors": ["chat_completion"]}],
        )
        first = method("Lx/First;", "run")
        second = method("Lx/Second;", "run")
        graph = AUDIT.build_interprocedural_points_to_graph(
            [caller, first, second], max_records=1
        )
        summary = graph["summary"]
        self.assertEqual(3, summary["root_method_count"])
        self.assertEqual(1, summary["semantic_candidate_root_count"])
        self.assertEqual(1, summary["record_limit"])
        self.assertTrue(summary["records_truncated"])
        self.assertEqual(1, summary["call_context_records_dropped"])
        self.assertGreaterEqual(summary["queue_states_processed"], 1)
        self.assertEqual(5, summary["queue_states_enqueued"])
        self.assertEqual(5, summary["queue_states_processed"])
        self.assertFalse(summary["context_expansion_complete"])


    def test_interprocedural_points_to_marks_unresolved_calls_incomplete_per_root(self):
        root = {
            "class": "Lx/Root;", "name": "entry", "descriptor": "()V",
            "component": "base", "roles": [{"role": "request", "anchors": ["entry"]}],
            "invoke_sites": [{
                "instruction": 0, "line": 1, "owner": "Lexternal/Library;",
                "name": "run", "descriptor": "()V", "opcode": "invoke-static",
                "registers": [], "result_instruction": None, "result_register": None,
            }],
            "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
            "object_points_to": {
                "complete": True, "invoke_arguments": [], "field_receivers": [],
                "return_values": [], "instruction_writes": [],
            },
        }
        graph = AUDIT.build_interprocedural_points_to_graph(
            [root], root_scope="semantic-candidates"
        )
        summary = graph["summary"]
        self.assertEqual(1, summary["unresolved_call_sites"])
        self.assertFalse(summary["context_expansion_complete"])
        root_row = summary["root_diagnostics"]["top_hot_roots"][0]
        self.assertEqual(1, root_row["unresolved_call_sites"])
        self.assertFalse(root_row["context_expansion_complete"])

    def test_interprocedural_points_to_candidate_scope_is_explicit_and_keeps_callees(self):
        def method(owner, name, invokes=None, roles=None):
            return {
                "class": owner, "name": name, "descriptor": "()V",
                "component": "base", "roles": roles or [],
                "invoke_sites": invokes or [],
                "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
                "object_points_to": {
                    "complete": True, "invoke_arguments": [],
                    "field_receivers": [], "return_values": [],
                    "instruction_writes": [],
                },
            }

        caller = method(
            "Lx/Caller;", "entry",
            [{
                "instruction": 0, "line": 1, "owner": "Lx/Worker;",
                "name": "run", "descriptor": "()V", "opcode": "invoke-static",
                "registers": [], "result_instruction": None, "result_register": None,
            }],
            roles=[{"role": "request", "anchors": ["chat_completion"]}],
        )
        worker = method("Lx/Worker;", "run")
        unrelated = method("Lx/Unrelated;", "run")
        graph = AUDIT.build_interprocedural_points_to_graph(
            [caller, worker, unrelated], root_scope="semantic-candidates"
        )
        summary = graph["summary"]
        self.assertEqual("semantic-role-roots-only", summary["analysis_scope"])
        self.assertFalse(summary["scope_is_whole_program"])
        self.assertEqual(3, summary["eligible_root_method_count"])
        self.assertEqual(1, summary["root_method_count"])
        self.assertEqual(1, summary["semantic_candidate_root_count"])
        self.assertEqual(1, len(graph["call_contexts"]))
        self.assertEqual("Lx/Worker;->run()V", graph["call_contexts"][0]["callee"])
        self.assertTrue(summary["context_expansion_complete"])

    def test_interprocedural_points_to_preserves_root_provenance_for_shared_callee(self):
        def method(owner, name, invokes=None, roles=None):
            return {
                "class": owner, "name": name, "descriptor": "()V",
                "component": "base", "roles": roles or [],
                "invoke_sites": invokes or [],
                "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
                "object_points_to": {
                    "complete": True, "invoke_arguments": [],
                    "field_receivers": [], "return_values": [],
                    "instruction_writes": [],
                },
            }

        def call(target, instruction):
            return {
                "instruction": instruction, "line": instruction + 1,
                "owner": target, "name": "run", "descriptor": "()V",
                "opcode": "invoke-static", "registers": [],
                "result_instruction": None, "result_register": None,
            }

        first = method(
            "Lx/FirstRoot;", "entry", [call("Lx/Shared;", 0)],
            roles=[{"role": "request", "anchors": ["first"]}],
        )
        second = method(
            "Lx/SecondRoot;", "entry", [call("Lx/Shared;", 0)],
            roles=[{"role": "agent", "anchors": ["second"]}],
        )
        shared = method("Lx/Shared;", "run")
        graph = AUDIT.build_interprocedural_points_to_graph(
            [first, second, shared], root_scope="semantic-candidates"
        )

        expected_roots = {
            "Lx/FirstRoot;->entry()V",
            "Lx/SecondRoot;->entry()V",
        }
        self.assertEqual(
            expected_roots,
            {row["root_method_key"] for row in graph["call_contexts"]},
        )
        self.assertEqual(
            2, len({row["context_id"] for row in graph["call_contexts"]})
        )
        self.assertEqual(2, graph["summary"]["root_diagnostics"]["root_count"])
        self.assertEqual(
            0, graph["summary"]["root_diagnostics"]["roots_marked_incomplete"]
        )
        self.assertTrue(all(
            row["context_expansion_complete"]
            for row in graph["summary"]["root_diagnostics"]["top_hot_roots"]
        ))

    def test_interprocedural_points_to_budget_isolated_per_root_and_keeps_traversing(self):
        def method(owner, name, invokes=None, roles=None, receivers=None):
            return {
                "class": owner, "name": name, "descriptor": "()V",
                "component": "base", "roles": roles or [],
                "invoke_sites": invokes or [],
                "invoke_sites_truncated": False, "invoke_sites_incomplete": False,
                "object_points_to": {
                    "complete": True, "invoke_arguments": [],
                    "field_receivers": receivers or [], "return_values": [],
                    "instruction_writes": [],
                },
            }

        def call(target, instruction):
            return {
                "instruction": instruction, "line": instruction + 1,
                "owner": target, "name": "run", "descriptor": "()V",
                "opcode": "invoke-static", "registers": [],
                "result_instruction": None, "result_register": None,
            }

        hot_root = method(
            "Lx/HotRoot;", "entry",
            [call("Lx/HotA;", 0), call("Lx/HotB;", 1)],
            roles=[{"role": "request", "anchors": ["hot"]}],
        )
        independent_root = method(
            "Lx/IndependentRoot;", "entry",
            [call("Lx/Independent;", 0)],
            roles=[{"role": "agent", "anchors": ["independent"]}],
        )
        def receiver(field):
            return {
                "instruction": 0, "field": field, "access": "read",
                "receiver_register": "v0",
                "points_to": ["alloc:" + field + "#0:Ljava/lang/Object;"],
                "unknown": False, "identity_status": "singleton",
                "identity": "alloc:" + field + "#0:Ljava/lang/Object;",
            }

        hot_a = method("Lx/HotA;", "run", receivers=[receiver("Lx/HotA;->value:Ljava/lang/Object;")])
        hot_b = method("Lx/HotB;", "run", receivers=[receiver("Lx/HotB;->value:Ljava/lang/Object;")])
        independent = method(
            "Lx/Independent;", "run",
            receivers=[receiver("Lx/Independent;->value:Ljava/lang/Object;")],
        )

        graph = AUDIT.build_interprocedural_points_to_graph(
            [hot_root, independent_root, hot_a, hot_b, independent],
            max_records=2, root_scope="semantic-candidates",
        )
        summary = graph["summary"]
        rows = {
            row["root_method_key"]: row
            for row in summary["root_diagnostics"]["top_hot_roots"]
        }
        hot_key = "Lx/HotRoot;->entry()V"
        independent_key = "Lx/IndependentRoot;->entry()V"

        self.assertEqual(2, summary["root_method_count"])
        self.assertEqual(1, summary["per_root_record_limit"])
        self.assertEqual("fair-share-per-root; storage truncation never stops graph traversal", summary["record_budget_policy"])
        self.assertEqual(1, rows[hot_key]["call_contexts_stored"])
        self.assertEqual(1, rows[hot_key]["call_contexts_dropped"])
        self.assertEqual(1, rows[independent_key]["call_contexts_stored"])
        self.assertEqual(0, rows[independent_key]["call_contexts_dropped"])
        self.assertEqual(1, rows[hot_key]["receiver_records_stored"])
        self.assertEqual(1, rows[hot_key]["receiver_records_dropped"])
        self.assertEqual(1, rows[independent_key]["receiver_records_stored"])
        self.assertEqual(0, rows[independent_key]["receiver_records_dropped"])
        self.assertEqual(
            {hot_key, independent_key},
            {row["root_method_key"] for row in graph["call_contexts"]},
        )
        # The over-budget call is still traversed; storage truncation is not a work cutoff.
        self.assertEqual(3, summary["resolved_call_contexts"])
        self.assertEqual(5, summary["queue_states_processed"])
        self.assertFalse(summary["context_expansion_complete"])

    def test_interprocedural_points_to_rejects_unknown_root_scope(self):
        with self.assertRaises(ValueError):
            AUDIT.build_interprocedural_points_to_graph([], root_scope="guessed")

    def test_interprocedural_points_to_rejects_non_positive_record_budget(self):
        with self.assertRaises(ValueError):
            AUDIT.build_interprocedural_points_to_graph([], max_records=0)


    def test_static_candidate_evidence_grade_requires_independent_families_and_never_authorizes_hook(self):
        anchor_only = AUDIT.static_candidate_evidence(
            {"roles": [{"role": "request"}], "invokes": []},
            incoming_count=0, outgoing_count=0,
            class_fact={"super": "Ljava/lang/Object;", "interfaces": []},
        )
        self.assertEqual("E0_ROLE_MATCH_ONLY", anchor_only["static_evidence_level"])
        self.assertEqual([], anchor_only["evidence_families"])
        self.assertFalse(anchor_only["runtime_confirmed"])
        self.assertFalse(anchor_only["hook_authorized"])

        literal_anchor = AUDIT.static_candidate_evidence(
            {
                "roles": [{"role": "request", "anchors": ["/api/v0/chat/completion"]}],
                "strings": ["/api/v0/chat/completion"],
                "invokes": [],
            },
            incoming_count=0, outgoing_count=0, class_fact=None,
        )
        self.assertEqual("E0_ONE_STATIC_FAMILY", literal_anchor["static_evidence_level"])
        self.assertEqual(["protocol_anchor"], literal_anchor["evidence_families"])

        corroborated = AUDIT.static_candidate_evidence(
            {
                "roles": [{"role": "request"}],
                "invokes": ["Lkotlinx/coroutines/flow/Flow;->collect()V"],
                "control_flow": {"cfg": {"complete": True, "edge_count": 2}},
                "object_points_to": {"complete": True, "singleton_receiver_count": 1},
            },
            incoming_count=3, outgoing_count=2,
            class_fact={"super": "Lx/Base;", "interfaces": ["Lx/Role;"]},
        )
        self.assertEqual("E3_FOUR_OR_MORE_STATIC_FAMILIES", corroborated["static_evidence_level"])
        self.assertGreaterEqual(corroborated["evidence_family_count"], 4)
        self.assertIn("call_graph", corroborated["evidence_families"])
        self.assertIn("stable_api_calls", corroborated["evidence_families"])
        self.assertIn("intraprocedural_points_to", corroborated["evidence_families"])
        self.assertFalse(corroborated["runtime_confirmed"])
        self.assertFalse(corroborated["hook_authorized"])


if __name__ == "__main__":
    unittest.main()