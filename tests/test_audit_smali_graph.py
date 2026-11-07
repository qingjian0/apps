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
        self.assertEqual("one-callsite-context", receiver["identity_scope"])
        self.assertFalse(receiver["runtime_identity_proven"])

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


if __name__ == "__main__":
    unittest.main()
