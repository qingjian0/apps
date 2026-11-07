package dsh.semantic

import java.nio.file.Files
import java.util.zip.GZIPOutputStream
import kotlin.test.Test
import kotlin.test.assertTrue
import kotlin.test.assertFalse

class StaticProgramGraphTest {
    private fun gzipLines(lines: List<String>): String {
        val path = Files.createTempFile("semantic-graph", ".jsonl.gz")
        GZIPOutputStream(Files.newOutputStream(path)).bufferedWriter(Charsets.UTF_8).use { out ->
            lines.forEach { out.appendLine(it) }
        }
        path.toFile().deleteOnExit()
        return path.toString()
    }

    private fun textFile(content: String): String {
        val path = Files.createTempFile("semantic-graph-summary", ".json")
        Files.writeString(path, content)
        path.toFile().deleteOnExit()
        return path.toString()
    }

    @Test fun methodRecordCallbackRunsOncePerIndexLine() {
        val methods = gzipLines(listOf(
            """{"class":"Lx/A;","name":"one","descriptor":"()V","field_reads":[],"field_writes":[]}""",
            """{"class":"Lx/B;","name":"two","descriptor":"()V","field_reads":[],"field_writes":[]}"""
        ))
        val edges = gzipLines(emptyList())
        val classes = gzipLines(emptyList())
        val seen = mutableListOf<String>()
        StaticProgramGraph.load(methods, edges, classes, onMethodRecord = { seen += it.toString() })
        assertTrue(seen.size == 2)
        assertTrue(seen.any { it.contains("\"name\":\"one\"") })
        assertTrue(seen.any { it.contains("\"name\":\"two\"") })
    }

    @Test fun incompleteCfgDoesNotBecomeControlFlowEvidence() {
        val methods = gzipLines(listOf(
            """{"class":"Lx/A;","name":"compose","descriptor":"()V","field_reads":[],"field_writes":[],"control_flow":{"branch_count":4,"label_count":5,"return_count":1,"throw_count":0,"cfg":{"block_count":6,"edge_count":7,"unresolved_target_count":1,"complete":false}}}"""
        ))
        val edges = gzipLines(emptyList())
        val classes = gzipLines(listOf("""{"descriptor":"Lx/A;","super":"Ljava/lang/Object;","interfaces":[]}"""))
        val host = HostFingerprint("com.deepseek.chat", 300, "future", "cert", "dex-300", "loader")
        val candidate = SemanticCandidate(
            RoleId("prompt.compose"),
            MethodShape("Lx/A;", "compose", "()V", emptyList(), "V"),
            host,
            listOf(Evidence(EvidenceFamily.PROTOCOL_ANCHOR, "custom_instructions", 0.9))
        )
        val enriched = StaticProgramGraph.load(methods, edges, classes).enrich(candidate)
        assertTrue(enriched.evidence.none { it.family == EvidenceFamily.CONTROL_FLOW })
    }

    @Test fun joinsCallersCalleesAndCrossMethodFieldFlow() {
        val target = "Lx/A;->compose()V"
        val methods = gzipLines(listOf(
            """{"class":"Lx/A;","name":"compose","descriptor":"()V","field_reads":["Lx/State;->prompt:Ljava/lang/String;"],"field_writes":[],"control_flow":{"branch_count":2,"label_count":3,"return_count":1,"throw_count":0,"cfg":{"block_count":4,"edge_count":4,"unresolved_target_count":0,"complete":true}}}""",
            """{"class":"Lx/State;","name":"update","descriptor":"()V","field_reads":[],"field_writes":["Lx/State;->prompt:Ljava/lang/String;"],"roles":[{"role":"prompt_pipeline","anchors":["custom_instructions"]}],"control_flow":{"branch_count":1,"label_count":1,"return_count":1,"throw_count":0}}""",
            """{"class":"Lx/Caller;","name":"start","descriptor":"()V","field_reads":[],"field_writes":[],"roles":[{"role":"prompt_pipeline","anchors":["custom_instructions"]}],"control_flow":{"branch_count":0,"label_count":0,"return_count":1,"throw_count":0}}"""
        ))
        val edges = gzipLines(listOf(
            """{"from":"Lx/Caller;->start()V","to":"$target"}""",
            """{"from":"$target","to":"Lkotlinx/coroutines/flow/Flow;->emit(Ljava/lang/Object;)V"}"""
        ))
        val classes = gzipLines(listOf(
            """{"descriptor":"Lx/A;","super":"Ljava/lang/Object;","interfaces":["Lx/PromptComposer;"]}""",
            """{"descriptor":"Lx/B;","super":"Ljava/lang/Object;","interfaces":["Lx/PromptComposer;"]}""",
            """{"descriptor":"Lx/PromptComposer;","super":"Ljava/lang/Object;","interfaces":[]}"""
        ))
        val host = HostFingerprint("com.deepseek.chat", 300, "future", "cert", "dex-300", "loader")
        val candidate = SemanticCandidate(
            RoleId("prompt.compose"),
            MethodShape("Lx/A;", "compose", "()V", emptyList(), "V"),
            host,
            listOf(
                Evidence(EvidenceFamily.PROTOCOL_ANCHOR, "custom_instructions", 0.9),
                Evidence(EvidenceFamily.TYPE_SHAPE, "zero-arg-void", 0.7),
                Evidence(EvidenceFamily.BYTECODE_SHAPE, "small-method", 0.5)
            )
        )
        val graph = StaticProgramGraph.load(methods, edges, classes)
        val enriched = graph.enrich(candidate)
        val families = enriched.evidence.map { it.family }.toSet()
        assertTrue(EvidenceFamily.CALL_GRAPH in families)
        // Matching field descriptors alone do not prove the same object instance.
        assertFalse(EvidenceFamily.DATA_FLOW in families)
        assertTrue(EvidenceFamily.CONTROL_FLOW in families)
        assertTrue(EvidenceFamily.TYPE_SHAPE in families)
        assertTrue(enriched.evidence.any { it.family == EvidenceFamily.TYPE_SHAPE && it.key.contains("interface-implementors=2") })
        assertTrue(enriched.evidence.any { it.family == EvidenceFamily.CALL_GRAPH && it.key.contains("neighbor-rare-anchor-hits=1") })
        assertTrue(graph.graphStats()["sharedFields"] == 1)
        assertTrue(graph.graphStats()["classes"] == 3)
    }

    @Test fun interproceduralPointsToIsLoadedOnlyAsDiagnosticAndOnlyWhenComplete() {
        val target = "Lx/Target;->consume(Ljava/lang/Object;)V"
        val caller = "Lx/Caller;->send()V"
        val methods = gzipLines(listOf(
            """{"class":"Lx/Target;","name":"consume","descriptor":"(Ljava/lang/Object;)V","field_reads":[],"field_writes":[],"roles":[{"role":"prompt_pipeline","anchors":["custom_instructions"]}]}""",
            """{"class":"Lx/Caller;","name":"send","descriptor":"()V","field_reads":[],"field_writes":[]}"""
        ))
        val edges = gzipLines(emptyList())
        val classes = gzipLines(listOf(
            """{"descriptor":"Lx/Target;","super":"Ljava/lang/Object;","interfaces":[]}""",
            """{"descriptor":"Lx/Caller;","super":"Ljava/lang/Object;","interfaces":[]}"""
        ))
        val pointsTo = gzipLines(listOf(
            """{"caller":"$caller","callee":"$target","identity_scope":"bounded-call-string-context","identity_status":"singleton","identity":"alloc:caller#0:Lx/Thing;","runtime_identity_proven":false}"""
        ))
        val completeSummary = textFile(
            """{"interprocedural_points_to":{"records_truncated":false,"context_expansion_complete":true,"recursive_fixed_point":false,"runtime_identity_proven":false}}"""
        )
        val host = HostFingerprint("com.deepseek.chat", 300, "future", "cert", "dex-300", "loader")
        val candidate = SemanticCandidate(
            RoleId("prompt.compose"),
            MethodShape("Lx/Target;", "consume", "(Ljava/lang/Object;)V",
                listOf("Ljava/lang/Object;"), "V"),
            host,
            listOf(Evidence(EvidenceFamily.PROTOCOL_ANCHOR, "custom_instructions", 0.9))
        )
        val graph = StaticProgramGraph.load(
            methods, edges, classes, summaryPath = completeSummary, pointsToPath = pointsTo
        )
        val enriched = graph.enrich(candidate)
        assertTrue(graph.graphStats()["interproceduralPointsToLoaded"] == 1)
        assertTrue(graph.graphStats()["interproceduralContextualReceivers"] == 1)
        assertTrue(graph.graphStats()["interproceduralSingletonContextReceivers"] == 1)
        // A static contextual points-to projection is diagnostic only, never DATA_FLOW evidence.
        assertFalse(enriched.evidence.any { it.family == EvidenceFamily.DATA_FLOW })

        val truncatedSummary = textFile(
            """{"interprocedural_points_to":{"records_truncated":true,"context_expansion_complete":false,"recursive_fixed_point":false,"runtime_identity_proven":false}}"""
        )
        val truncatedGraph = StaticProgramGraph.load(
            methods, edges, classes, summaryPath = truncatedSummary, pointsToPath = pointsTo
        )
        assertTrue(truncatedGraph.graphStats()["interproceduralPointsToLoaded"] == 0)
        assertTrue(truncatedGraph.graphStats()["interproceduralContextualReceivers"] == 0)

        val runtimeClaimSummary = textFile(
            """{"interprocedural_points_to":{"records_truncated":false,"context_expansion_complete":true,"recursive_fixed_point":false,"runtime_identity_proven":true}}"""
        )
        val runtimeClaimGraph = StaticProgramGraph.load(
            methods, edges, classes, summaryPath = runtimeClaimSummary, pointsToPath = pointsTo
        )
        assertTrue(runtimeClaimGraph.graphStats()["interproceduralPointsToLoaded"] == 0)
    }

    @Test fun interproceduralValueEdgesBecomeDataFlowEvidenceOnlyWhenNotTruncated() {
        val target = "Lx/Target;->compose(Ljava/lang/String;)Ljava/lang/String;"
        val caller = "Lx/Caller;->send()V"
        val methods = gzipLines(listOf(
            """{"class":"Lx/Target;","name":"compose","descriptor":"(Ljava/lang/String;)Ljava/lang/String;","field_reads":[],"field_writes":[],"roles":[{"role":"prompt_pipeline","anchors":["custom_instructions"]}]}""",
            """{"class":"Lx/Caller;","name":"send","descriptor":"()V","field_reads":[],"field_writes":[]}"""
        ))
        val edges = gzipLines(emptyList())
        val classes = gzipLines(listOf(
            """{"descriptor":"Lx/Target;","super":"Ljava/lang/Object;","interfaces":[]}""",
            """{"descriptor":"Lx/Caller;","super":"Ljava/lang/Object;","interfaces":[]}"""
        ))
        val valueEdges = gzipLines(listOf(
            """{"kind":"argument","from_method":"$caller","from_definition":"d1:v0","to_method":"$target","to_parameter":"entry:p0"}"""
        ))
        val completeSummary = textFile("""{"interprocedural_value_flow":{"edges_truncated":false}}""")
        val host = HostFingerprint("com.deepseek.chat", 300, "future", "cert", "dex-300", "loader")
        val candidate = SemanticCandidate(
            RoleId("prompt.compose"),
            MethodShape("Lx/Target;", "compose", "(Ljava/lang/String;)Ljava/lang/String;",
                listOf("Ljava/lang/String;"), "Ljava/lang/String;"),
            host,
            listOf(Evidence(EvidenceFamily.PROTOCOL_ANCHOR, "custom_instructions", 0.9))
        )
        val graph = StaticProgramGraph.load(methods, edges, classes, valueEdges, completeSummary)
        val enriched = graph.enrich(candidate)
        val flowEvidence = enriched.evidence.single { it.family == EvidenceFamily.DATA_FLOW }
        assertTrue(flowEvidence.key.contains("interprocedural-argument-edges=1"))
        assertTrue(graph.graphStats()["interproceduralArgumentEdges"] == 1)
        assertTrue(graph.graphStats()["interproceduralValueFlowExpectedEdges"] == 1)
        assertTrue(graph.graphStats()["interproceduralValueFlowStoredEdges"] == 1)
        assertTrue(graph.graphStats()["interproceduralValueFlowLoadedEdges"] == 1)
        assertTrue(graph.graphStats()["interproceduralValueFlowSkippedMissingMethods"] == 0)
        assertTrue(graph.graphStats()["interproceduralValueFlowFilePresent"] == 1)
        assertTrue(graph.graphStats()["interproceduralValueFlowComplete"] == 1)

        val truncatedSummary = textFile("""{"interprocedural_value_flow":{"edges_truncated":true}}""")
        val truncatedGraph = StaticProgramGraph.load(methods, edges, classes, valueEdges, truncatedSummary)
        val truncated = truncatedGraph.enrich(candidate)
        assertFalse(truncated.evidence.any { it.family == EvidenceFamily.DATA_FLOW })
        assertTrue(truncatedGraph.graphStats()["interproceduralArgumentEdges"] == 0)
    }
 
    @Test fun incompleteValueFlowIngestionNeverBecomesDataFlowEvidence() {
        val target = "Lx/Target;->compose(Ljava/lang/String;)Ljava/lang/String;"
        val caller = "Lx/Caller;->send()V"
        val methods = gzipLines(listOf(
            """{"class":"Lx/Target;","name":"compose","descriptor":"(Ljava/lang/String;)Ljava/lang/String;","field_reads":[],"field_writes":[],"roles":[{"role":"prompt_pipeline","anchors":["custom_instructions"]}]}""",
            """{"class":"Lx/Caller;","name":"send","descriptor":"()V","field_reads":[],"field_writes":[]}"""
        ))
        val edges = gzipLines(emptyList())
        val classes = gzipLines(listOf(
            """{"descriptor":"Lx/Target;","super":"Ljava/lang/Object;","interfaces":[]}""",
            """{"descriptor":"Lx/Caller;","super":"Ljava/lang/Object;","interfaces":[]}"""
        ))
        val valueEdges = gzipLines(listOf(
            """{"kind":"argument","from_method":"$caller","from_definition":"d1:v0","to_method":"$target","to_parameter":"entry:p0"}""",
            """{"kind":"argument","from_method":"Lx/Missing;->unknown()V","from_definition":"d1:v0","to_method":"$target","to_parameter":"entry:p0"}"""
        ))
        val summary = textFile("""{"interprocedural_value_flow":{"edge_count":2,"stored_edge_count":2,"edges_truncated":false}}""")
        val host = HostFingerprint("com.deepseek.chat", 300, "future", "cert", "dex-300", "loader")
        val candidate = SemanticCandidate(
            RoleId("prompt.compose"),
            MethodShape("Lx/Target;", "compose", "(Ljava/lang/String;)Ljava/lang/String;",
                listOf("Ljava/lang/String;"), "Ljava/lang/String;"),
            host,
            listOf(Evidence(EvidenceFamily.PROTOCOL_ANCHOR, "custom_instructions", 0.9))
        )
        val graph = StaticProgramGraph.load(methods, edges, classes, valueEdges, summary)
        val enriched = graph.enrich(candidate)
        assertFalse(enriched.evidence.any { it.family == EvidenceFamily.DATA_FLOW })
        assertTrue(graph.graphStats()["interproceduralValueFlowLoadedEdges"] == 1)
        assertTrue(graph.graphStats()["interproceduralValueFlowSkippedMissingMethods"] == 1)
        assertTrue(graph.graphStats()["interproceduralValueFlowComplete"] == 0)
    }

}
