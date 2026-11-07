package dsh.semantic

@JvmInline
value class RoleId(val value: String) {
    init { require(value.matches(Regex("[a-z][a-z0-9_.-]{1,95}"))) }
}

enum class EvidenceFamily { PROTOCOL_ANCHOR, TYPE_SHAPE, CALL_GRAPH, CONTROL_FLOW, BYTECODE_SHAPE, DATA_FLOW, FRAMEWORK_INTERACTION, RUNTIME_BEHAVIOR, HOST_IDENTITY }

data class HostFingerprint(val packageName: String, val versionCode: Long?, val versionName: String?, val signingDigest: String?, val dexDigest: String, val classLoaderId: String) {
    fun isUsableForHooking() = packageName == "com.deepseek.chat" && dexDigest.isNotBlank() && classLoaderId.isNotBlank()
    fun hasCompleteRuntimeIdentity() = isUsableForHooking() && versionCode != null && !versionName.isNullOrBlank() && !signingDigest.isNullOrBlank()
}

data class Evidence(val family: EvidenceFamily, val key: String, val weight: Double, val detail: String = "") {
    init { require(key.isNotBlank()); require(weight.isFinite() && weight in 0.0..1.0) }
}

data class MethodShape(val ownerDescriptor: String, val name: String, val descriptor: String, val parameterTypes: List<String>, val returnType: String, val isStatic: Boolean? = null) {
    val stableIdentity: String get() = ownerDescriptor + "->" + name + descriptor
    fun isWellFormed(): Boolean = ownerDescriptor.matches(Regex("L[^;]+;")) && name.isNotBlank() && descriptor.startsWith("(") && descriptor.contains(")") && descriptor.substringAfter(")").isNotBlank() && returnType.isNotBlank()
}

data class SemanticCandidate(val role: RoleId, val method: MethodShape, val host: HostFingerprint, val evidence: List<Evidence>, val negativeEvidence: Set<String> = emptySet(), val sourceVersion: String? = host.versionName)

data class RolePolicy(val role: RoleId, val minimumEvidenceFamilies: Int = 3, val minimumScore: Double = 2.0, val minimumWinnerMargin: Double = 0.5, val requiredFamilies: Set<EvidenceFamily> = emptySet(), val forbiddenNegativeEvidence: Set<String> = emptySet()) {
    init { require(minimumEvidenceFamilies >= 1); require(minimumScore >= 0.0); require(minimumWinnerMargin >= 0.0) }
}

data class Resolution(val role: RoleId, val selected: SemanticCandidate?, val score: Double, val runnerUpScore: Double, val evidenceFamilies: Set<EvidenceFamily>, val rejection: String? = null) {
    val accepted: Boolean get() = selected != null && rejection == null
}
