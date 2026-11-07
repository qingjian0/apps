package dsh.semantic

data class StaticRoleEvidence(val roleLabel: String, val anchors: List<String>)
data class StaticMethodRecord(
    val ownerDescriptor: String,
    val methodName: String,
    val descriptor: String,
    val parameterTypes: List<String>,
    val returnType: String,
    val invokes: List<String>,
    val opcodeCount: Int,
    val roles: List<StaticRoleEvidence>,
    val isStatic: Boolean? = null
)

/** Maps evidence labels to stable feature roles; obfuscated names are diagnostics only. */
class StaticEvidenceMapper {
    private val roleAliases = mapOf(
        "request_route" to "network.route", "pow" to "network.pow",
        "sse_transport" to "sse.parse", "sse_dispatch" to "sse.dispatch",
        "flow_coroutine" to "stream.flow", "serialization" to "serializer.model",
        "agent_tool" to "agent.result", "session" to "conversation.session",
        "prompt_pipeline" to "prompt.compose", "agent_planning" to "agent.plan",
        "tool_registry_execution" to "tool.registry", "local_api_gateway" to "local_api.request",
        "multimodal_image" to "multimodal.image", "multimodal_audio" to "multimodal.audio",
        "attachment_file" to "attachment.file", "search_web" to "search.query",
        "storage_sync" to "storage.preference", "account_capability" to "account.capability",
        "ui_settings" to "settings.toggle"
    )

    fun map(host: HostFingerprint, record: StaticMethodRecord): List<SemanticCandidate> {
        val method = MethodShape(record.ownerDescriptor, record.methodName, record.descriptor,
            record.parameterTypes, record.returnType, record.isStatic)
        return record.roles.mapNotNull { roleEvidence ->
            val roleName = roleAliases[roleEvidence.roleLabel] ?: return@mapNotNull null
            val evidence = buildList {
                roleEvidence.anchors.distinct().forEach { add(Evidence(EvidenceFamily.PROTOCOL_ANCHOR, it, 0.9)) }
                if (record.descriptor.isNotBlank() && record.returnType.isNotBlank())
                    add(Evidence(EvidenceFamily.TYPE_SHAPE, "arity=" + record.parameterTypes.size + ";return=" + record.returnType, 0.65))
                if (record.invokes.isNotEmpty()) add(Evidence(EvidenceFamily.CALL_GRAPH, "outgoing-call-count=" + record.invokes.size, 0.55))
                if (record.invokes.any { it.startsWith("Lkotlin/") || it.startsWith("Lkotlinx/") || it.startsWith("Lio/ktor/") || it.startsWith("Ljava/") || it.startsWith("Landroid/") })
                    add(Evidence(EvidenceFamily.FRAMEWORK_INTERACTION, "stable-framework-call-family", 0.75))
                if (record.opcodeCount > 0) add(Evidence(EvidenceFamily.BYTECODE_SHAPE, "method-body-opcodes=" + record.opcodeCount, 0.5))
            }
            if (evidence.isEmpty()) null else SemanticCandidate(RoleId(roleName), method, host, evidence)
        }
    }
}
