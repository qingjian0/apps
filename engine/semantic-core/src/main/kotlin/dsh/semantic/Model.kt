package dsh.semantic

@JvmInline
value class RoleId(val value: String) {
    init { require(value.matches(Regex("[a-z][a-z0-9_.-]{1,95}"))) }
}

enum class EvidenceFamily { PROTOCOL_ANCHOR, TYPE_SHAPE, CALL_GRAPH, CONTROL_FLOW, BYTECODE_SHAPE, DATA_FLOW, FRAMEWORK_INTERACTION, RUNTIME_BEHAVIOR, HOST_IDENTITY }

data class HostFingerprint(val packageName: String, val versionCode: Long?, val versionName: String?, val signingDigest: String?, val dexDigest: String, val classLoaderId: String) {
    fun isRecognizedTargetHost() = packageName == "com.deepseek.chat" && dexDigest.isNotBlank()
    fun hasCompleteRuntimeIdentity() = isRecognizedTargetHost() && versionCode != null && !versionName.isNullOrBlank() && !signingDigest.isNullOrBlank() && classLoaderId.isNotBlank()
}

data class Evidence(val family: EvidenceFamily, val key: String, val weight: Double, val detail: String = "") {
    init { require(key.isNotBlank()); require(weight.isFinite() && weight in 0.0..1.0) }
}

data class MethodShape(val ownerDescriptor: String, val name: String, val descriptor: String, val parameterTypes: List<String>, val returnType: String, val isStatic: Boolean? = null) {
    val stableIdentity: String get() = ownerDescriptor + "->" + name + descriptor
    fun isWellFormed(): Boolean {\n        val parsed = MethodDescriptor.parse(ownerDescriptor, name, descriptor) ?: return false\n        return parsed.parameterDescriptors() == parameterTypes && parsed.returnDescriptor() == returnType\n    }
}

data class SemanticCandidate(val role: RoleId, val method: MethodShape, val host: HostFingerprint, val evidence: List<Evidence>, val negativeEvidence: Set<String> = emptySet(), val sourceVersion: String? = host.versionName)

data class RolePolicy(
    val role: RoleId,
    val minimumEvidenceFamilies: Int = 4,
    val minimumScore: Double = 2.0,
    val minimumWinnerMargin: Double = 0.5,
    val requiredFamilies: Set<EvidenceFamily> = emptySet(),
    val forbiddenNegativeEvidence: Set<String> = setOf("framework-owner", "third-party-sdk-owner")
) {
    init { require(minimumEvidenceFamilies >= 1); require(minimumScore >= 0.0); require(minimumWinnerMargin >= 0.0) }

    companion object {
        fun forRole(role: RoleId): RolePolicy {
            val core = setOf(EvidenceFamily.PROTOCOL_ANCHOR, EvidenceFamily.CALL_GRAPH, EvidenceFamily.TYPE_SHAPE)
            val additional = when (role.value) {
                "prompt.compose", "agent.plan", "agent.result", "tool.registry", "conversation.session",
                "storage.preference", "search.query", "multimodal.image", "multimodal.audio",
                "attachment.file", "account.capability", "settings.toggle" -> setOf(EvidenceFamily.DATA_FLOW)
                "network.route", "stream.flow" -> setOf(EvidenceFamily.FRAMEWORK_INTERACTION)
                "sse.parse", "sse.dispatch", "network.pow" -> setOf(EvidenceFamily.CONTROL_FLOW)
                else -> emptySet()
            }
            return RolePolicy(
                role = role,
                minimumEvidenceFamilies = 4,
                minimumScore = 2.0,
                minimumWinnerMargin = 0.5,
                requiredFamilies = core + additional
            )
        }
    }
}

data class Resolution(val role: RoleId, val selected: SemanticCandidate?, val score: Double, val runnerUpScore: Double, val evidenceFamilies: Set<EvidenceFamily>, val rejection: String? = null) {
    val accepted: Boolean get() = selected != null && rejection == null
}
