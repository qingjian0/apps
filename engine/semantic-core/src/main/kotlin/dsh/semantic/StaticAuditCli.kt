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
        var candidates = 0
        var accepted = 0
        var rejected = 0
        val roleCounts = sortedMapOf<String, Int>()
        BufferedReader(InputStreamReader(GZIPInputStream(FileInputStream(path)), Charsets.UTF_8)).use { input ->
            input.lineSequence().forEach { line ->
                methods++
                val mapped = reader.readLine(line, host)
                candidates += mapped.size
                mapped.forEach { candidate ->
                    roleCounts[candidate.role.value] = (roleCounts[candidate.role.value] ?: 0) + 1
                    val result = resolver.resolve(host, RolePolicy(candidate.role), listOf(candidate))
                    if (result.accepted) accepted++ else rejected++
                }
            }
        }
        println("STATIC_INGEST version=$version methods=$methods candidates=$candidates resolver_accepted=$accepted resolver_rejected=$rejected role_counts=$roleCounts")
    }
}
