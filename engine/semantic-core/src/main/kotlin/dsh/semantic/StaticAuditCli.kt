package dsh.semantic

import java.io.BufferedReader
import java.io.FileInputStream
import java.io.InputStreamReader
import java.util.zip.GZIPInputStream

/** Ingests real APK method and call-edge indexes; this is analysis only, never Hook installation. */
fun main(args: Array<String>) {
    require(args.isNotEmpty() && args.size % 5 == 0) {
        "Arguments must be groups of: methods.jsonl.gz call-edges.jsonl.gz classes.jsonl.gz version dexDigest"
    }
    val reader = StaticAuditJsonReader()
    val resolver = SemanticResolver()
    args.toList().chunked(5).forEach { (methodsPath, edgesPath, classesPath, version, dexDigest) ->
        val host = HostFingerprint("com.deepseek.chat", null, version, null, dexDigest, "static-audit")
        val anchorFrequency = mutableMapOf<String, Int>()
        BufferedReader(InputStreamReader(GZIPInputStream(FileInputStream(methodsPath)), Charsets.UTF_8)).use { input ->
            input.lineSequence().forEach { line ->
                reader.anchorKeys(line).forEach { key -> anchorFrequency[key] = (anchorFrequency[key] ?: 0) + 1 }
            }
        }
        val graph = StaticProgramGraph.load(methodsPath, edgesPath, classesPath)
        val byRole = mutableMapOf<RoleId, MutableList<SemanticCandidate>>()
        var methods = 0
        BufferedReader(InputStreamReader(GZIPInputStream(FileInputStream(methodsPath)), Charsets.UTF_8)).use { input ->
            input.lineSequence().forEach { line ->
                methods++
                reader.readLine(line, host, anchorFrequency).forEach { candidate ->
                    byRole.getOrPut(candidate.role) { mutableListOf() }.add(graph.enrich(candidate))
                }
            }
        }
        var acceptedRoles = 0
        val roleSummary = sortedMapOf<String, String>()
        byRole.entries.sortedBy { it.key.value }.forEach { entry ->
            val role = entry.key
            val candidates = entry.value
            val result = resolver.resolve(host, RolePolicy.forRole(role), candidates)
            roleSummary[role.value] = if (result.accepted) {
                acceptedRoles++
                "resolved:" + (result.selected?.method?.stableIdentity ?: "unknown") +
                    ";score=" + result.score + ";runnerUp=" + result.runnerUpScore
            } else {
                val top = candidates.sortedByDescending { candidate ->
                    candidate.evidence.groupBy { it.family }.values.sumOf { group -> group.maxOfOrNull { it.weight } ?: 0.0 }
                }.take(3).joinToString("|") { it.method.stableIdentity }
                "rejected:" + result.rejection + ";candidateCount=" + candidates.size + ";top=" + top
            }
        }
        val graphStats = graph.graphStats()
        println(
            "STATIC_INGEST version=" + version +
                " methods=" + methods +
                " candidates=" + byRole.values.sumOf { it.size } +
                " roles=" + byRole.size +
                " graph=" + graphStats +
                " resolver_accepted_roles=" + acceptedRoles +
                " resolver_rejected_roles=" + (byRole.size - acceptedRoles) +
                " role_summary=" + roleSummary
        )
    }
}
