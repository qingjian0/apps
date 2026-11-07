package dsh.semantic

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import kotlinx.serialization.json.contentOrNull
import kotlinx.serialization.json.intOrNull

/** Reads one methods.jsonl.gz record emitted by scripts/audit_deepseek_apk.py. */
class StaticAuditJsonReader(private val mapper: StaticEvidenceMapper = StaticEvidenceMapper()) {
    private val json = Json { ignoreUnknownKeys = true }

    fun readLine(line: String, host: HostFingerprint, anchorFrequency: Map<String, Int> = emptyMap()): List<SemanticCandidate> {
        val obj = json.parseToJsonElement(line).jsonObject
        val owner = obj.string("class") ?: return emptyList()
        val name = obj.string("name") ?: return emptyList()
        val descriptor = obj.string("descriptor") ?: return emptyList()
        val parsed = parseMethodDescriptor(descriptor) ?: return emptyList()
        val invokes = obj["invokes"]?.jsonArray?.mapNotNull { it.jsonPrimitive.contentOrNull }.orEmpty()
        val roles = obj["roles"]?.jsonArray?.mapNotNull { role ->
            val value = role.jsonObject
            val label = value.string("role") ?: return@mapNotNull null
            val anchors = value["anchors"]?.jsonArray?.mapNotNull { it.jsonPrimitive.contentOrNull }.orEmpty()
            StaticRoleEvidence(label, anchors)
        }.orEmpty()
        val access = obj.string("access").orEmpty()
        val record = StaticMethodRecord(owner, name, descriptor, parsed.first, parsed.second,
            invokes, obj["opcode_count"]?.jsonPrimitive?.intOrNull ?: 0, roles,
            isStatic = access.split(' ').contains("static"))
        return mapper.map(host, record, anchorFrequency)
    }

    fun anchorKeys(line: String): List<String> {
        val obj = json.parseToJsonElement(line).jsonObject
        return obj["roles"]?.jsonArray?.flatMap { role ->
            role.jsonObject["anchors"]?.jsonArray?.mapNotNull { it.jsonPrimitive.contentOrNull }.orEmpty()
        }?.distinct().orEmpty()
    }

    private fun kotlinx.serialization.json.JsonObject.string(key: String): String? =
        this[key]?.jsonPrimitive?.contentOrNull

    private fun parseMethodDescriptor(value: String): Pair<List<String>, String>? {
        if (!value.startsWith("(")) return null
        var cursor = 1
        fun readType(allowVoid: Boolean): String? {
            val start = cursor
            while (cursor < value.length && value[cursor] == '[') cursor++
            if (cursor >= value.length) return null
            when (val type = value[cursor]) {
                'L' -> {
                    val end = value.indexOf(';', cursor)
                    if (end < 0) return null
                    cursor = end + 1
                }
                'V' -> {
                    if (!allowVoid || cursor != start) return null
                    cursor++
                }
                'Z', 'B', 'S', 'C', 'I', 'J', 'F', 'D' -> cursor++
                else -> return null
            }
            return value.substring(start, cursor)
        }
        val parameters = mutableListOf<String>()
        while (cursor < value.length && value[cursor] != ')') {
            parameters += readType(false) ?: return null
        }
        if (cursor >= value.length || value[cursor] != ')') return null
        cursor++
        val result = readType(true) ?: return null
        if (cursor != value.length) return null
        return parameters to result
    }
}
