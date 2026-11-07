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

    @Test fun joinsCallersCalleesAndCrossMethodFieldFlow() {
        val target = "Lx/A;->compose()V"
        val methods = gzipLines(listOf(
            """{"class":"Lx/A;","name":"compose","descriptor":"()V","field_reads":["Lx/State;->prompt:Ljava/lang/String;"],"field_writes":[],"control_flow":{"branch_count":2,"label_count":3,"return_count":1,"throw_count":0}}""",
            """{"class":"Lx/State;","name":"update","descriptor":"()V","field_reads":[],"field_writes":["Lx/State;->prompt:Ljava/lang/String;"],"control_flow":{"branch_count":1,"label_count":1,"return_count":1,"throw_count":0}}"""
        ))
        val edges = gzipLines(listOf(
            """{"from":"Lx/Caller;->start()V","to":"$target"}""",
            """{"from":"$target","to":"Lkotlinx/coroutines/flow/Flow;->emit(Ljava/lang/Object;)V"}"""
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
        val graph = StaticProgramGraph.load(methods, edges)
        val enriched = graph.enrich(candidate)
        val families = enriched.evidence.map { it.family }.toSet()
        assertTrue(EvidenceFamily.CALL_GRAPH in families)
        assertTrue(EvidenceFamily.DATA_FLOW in families)
        assertTrue(EvidenceFamily.CONTROL_FLOW in families)
        assertTrue(graph.graphStats()["sharedFields"] == 1)
    }
}
