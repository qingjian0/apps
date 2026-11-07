package dsh.semantic

import java.nio.file.Files
import java.util.zip.GZIPOutputStream
import kotlin.test.Test
import kotlin.test.assertTrue

class StaticProgramGraphTest {
    private fun gzipLines(lines: List<String>): String {
        val path = Files.createTempFile("semantic-graph", ".jsonl.gz")
        GZIPOutputStream(Files.newOutputStream(path)).bufferedWriter(Charsets.UTF_8).use { out ->
            lines.forEach { out.appendLine(it) }
        }
        path.toFile().deleteOnExit()
        return path.toString()
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
        assertTrue(EvidenceFamily.DATA_FLOW in families)
        assertTrue(EvidenceFamily.CONTROL_FLOW in families)
        assertTrue(EvidenceFamily.TYPE_SHAPE in families)
        assertTrue(enriched.evidence.any { it.family == EvidenceFamily.TYPE_SHAPE && it.key.contains("interface-implementors=2") })
        assertTrue(enriched.evidence.any { it.family == EvidenceFamily.CALL_GRAPH && it.key.contains("neighbor-rare-anchor-hits=1") })
        assertTrue(enriched.evidence.any { it.family == EvidenceFamily.DATA_FLOW && it.key.contains("field-neighbor-rare-anchor-hits=1") })
        assertTrue(graph.graphStats()["sharedFields"] == 1)
        assertTrue(graph.graphStats()["classes"] == 3)
    }
}
