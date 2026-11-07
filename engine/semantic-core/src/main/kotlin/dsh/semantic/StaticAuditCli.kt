package dsh.semantic

import java.io.BufferedReader
import java.io.FileInputStream
import java.io.InputStreamReader
import java.security.MessageDigest
import java.util.zip.GZIPInputStream

/** Cloud CI smoke-ingests the real methods.jsonl.gz indexes without installing any hooks. */
fun main(args: Array<String>) {
    require(args.isNotEmpty() && args.size % 3 == 0) {
        "Arguments must be groups of: methods.jsonl.gz version dexDigest"
    }
    val reader = StaticAuditJsonReader()
    val resolver = SemanticResolver()
    args.toList().chunked(3).forEach { (path, version, dexDigest) ->
        val host = HostFingerprint("com.deepseek.chat", null, version, null, dexDigest, "static-audit")
        var methods = 0
        val byRole = mutableMapOf<RoleId, MutableList<SemanticCandidate>>()
        BufferedReader(InputStreamReader(GZIPInputStream(FileInputStream(path)), Charsets.UTF_8)).use { input ->
            input.lineSequence().forEach { line ->
                methods++
                reader.readLine(line, host).forEach { candidate ->
                    byRole.getOrPut(candidate.role) { mutableListOf() }.add(candidate)
                }
            }
        }
        var acceptedRoles = 0
        val roleSummary = sortedMapOf<String, String>()
        byRole.entries.sortedBy { it.key.value }.forEach { entry ->
            val role = entry.key
            val result = resolver.resolve(host, RolePolicy(role), entry.value)
            roleSummary[role.value] = if (result.accepted) {
                acceptedRoles++
                "resolved:" + (result.selected?.method?.stableIdentity ?: "unknown")
            } else {
                "rejected:" + result.rejection
            }
        }
        val candidateCount = byRole.values.sumOf { it.size }
        println("STATIC_INGEST version=" + version + " methods=" + methods + " candidates=" + candidateCount + " roles=" + byRole.size + " resolver_accepted_roles=" + acceptedRoles + " resolver_rejected_roles=" + (byRole.size - acceptedRoles) + " role_summary=" + roleSummary)
    }
}
