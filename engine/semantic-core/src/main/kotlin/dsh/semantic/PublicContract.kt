package dsh.semantic

import java.security.MessageDigest

/** Complete runtime identity. APK and DEX digests are lowercase SHA-256 hex strings. */
data class HostIdentity(
    val packageName: String,
    val versionName: String?,
    val versionCode: Long?,
    val signingCertSha256: String?,
    val baseApkSha256: String?,
    val splitApkSha256: Set<String>,
    val dexFingerprint: String?,
    val processName: String,
    /** Process-local ClassLoader identity; never persist the ClassLoader object itself. */
    val classLoaderId: String,
    val observedAtEpochMillis: Long
) {
    fun missingRequiredFields(): Set<IdentityField> = buildSet {
        if (packageName.isBlank()) add(IdentityField.PACKAGE_NAME)
        if (versionName.isNullOrBlank()) add(IdentityField.VERSION_NAME)
        if (versionCode == null) add(IdentityField.VERSION_CODE)
        if (!signingCertSha256.isSha256()) add(IdentityField.SIGNING_CERT_SHA256)
        if (!baseApkSha256.isSha256()) add(IdentityField.BASE_APK_SHA256)
        if (!dexFingerprint.isSha256()) add(IdentityField.DEX_FINGERPRINT)
        if (splitApkSha256.any { !it.matches(Regex("[a-fA-F0-9]{64}")) }) add(IdentityField.SPLIT_APK_SHA256)
        if (processName.isBlank()) add(IdentityField.PROCESS_NAME)
        if (classLoaderId.isBlank()) add(IdentityField.CLASS_LOADER_ID)
    }

    fun isComplete(): Boolean = missingRequiredFields().isEmpty()

    fun fingerprintId(): String {
        val canonical = listOf(
            packageName, versionName.orEmpty(), versionCode?.toString().orEmpty(),
            signingCertSha256.orEmpty(), baseApkSha256.orEmpty(),
            splitApkSha256.sorted().joinToString(","), dexFingerprint.orEmpty(), processName
        ).joinToString("|")
        return MessageDigest.getInstance("SHA-256")
            .digest(canonical.toByteArray(Charsets.UTF_8))
            .joinToString("") { "%02x".format(it) }
    }

    fun matches(binding: HostProfileBinding): Boolean =
        packageName == binding.packageName &&
            versionName == binding.versionName &&
            versionCode == binding.versionCode &&
            signingCertSha256.equals(binding.signingCertSha256, ignoreCase = true) &&
            baseApkSha256.equals(binding.baseApkSha256, ignoreCase = true) &&
            dexFingerprint.equals(binding.dexFingerprint, ignoreCase = true) &&
            splitApkSha256.map { it.lowercase() }.toSet() == binding.splitApkSha256.map { it.lowercase() }.toSet()
}

enum class IdentityField {
    PACKAGE_NAME, VERSION_NAME, VERSION_CODE, SIGNING_CERT_SHA256,
    BASE_APK_SHA256, SPLIT_APK_SHA256, DEX_FINGERPRINT, PROCESS_NAME, CLASS_LOADER_ID
}

private fun String?.isSha256(): Boolean = this != null && matches(Regex("[a-fA-F0-9]{64}"))

/** JVM method descriptor with an exact owner, method name, parameter and return signature. */
data class MethodDescriptor(
    val owner: String,
    val name: String,
    val descriptor: String
) {
    val stableIdentity: String get() = "$owner->$name$descriptor"
    val isValid: Boolean get() = isClassDescriptor(owner) && isValidMethodName(name) && isMethodDescriptor(descriptor)
    fun parameterDescriptors(): List<String>? = parseMethodParts(descriptor)?.first
    fun returnDescriptor(): String? = parseMethodParts(descriptor)?.second

    companion object {
        fun parse(owner: String, name: String, descriptor: String): MethodDescriptor? =
            MethodDescriptor(owner, name, descriptor).takeIf { it.isValid }
    }
}

private fun isValidMethodName(name: String): Boolean =
    name == "<init>" || name == "<clinit>" ||
        (name.isNotBlank() && name.none { it in ".;[/<>()" || it.isWhitespace() })

private fun isClassDescriptor(value: String): Boolean =
    value.length >= 3 && value.startsWith("L") && value.endsWith(";") &&
        value.substring(1, value.length - 1).isNotBlank() &&
        value.substring(1, value.length - 1).none { it in ".;[(" }

private fun isMethodDescriptor(value: String): Boolean = parseMethodParts(value) != null

private fun parseMethodParts(value: String): Pair<List<String>, String>? {
    if (!value.startsWith("(")) return null
    val close = value.indexOf(')')
    if (close < 0 || close == value.lastIndex) return null
    var index = 1
    val parameters = mutableListOf<String>()
    while (index < close) {
        val next = parseFieldTypeEnd(value, index, allowVoid = false) ?: return null
        if (next > close) return null
        parameters += value.substring(index, next)
        index = next
    }
    if (index != close) return null
    val returnEnd = parseFieldTypeEnd(value, close + 1, allowVoid = true) ?: return null
    if (returnEnd != value.length) return null
    return parameters to value.substring(close + 1)
}

private fun parseFieldTypeEnd(value: String, start: Int, allowVoid: Boolean): Int? {
    if (start !in value.indices) return null
    return when (value[start]) {
        'V' -> if (allowVoid) start + 1 else null
        'Z', 'B', 'C', 'S', 'I', 'J', 'F', 'D' -> start + 1
        'L' -> {
            val end = value.indexOf(';', start + 1)
            if (end <= start + 1) null
            else {
                val body = value.substring(start + 1, end)
                if (body.any { it in ".;[(" }) null else end + 1
            }
        }
        '[' -> {
            var cursor = start
            while (cursor < value.length && value[cursor] == '[') cursor++
            if (cursor >= value.length || value[cursor] == 'V') null
            else parseFieldTypeEnd(value, cursor, allowVoid = false)
        }
        else -> null
    }
}

enum class EvidencePolarity { POSITIVE, NEGATIVE }
enum class EvidenceStrength { WEAK, MODERATE, STRONG, DIRECT }

data class EvidenceSource(
    val artifactSha256: String,
    val artifactPath: String,
    val method: MethodDescriptor?,
    val auditRunId: String?,
    val toolVersion: String
)

data class AuditableEvidence(
    val evidenceId: String,
    val family: EvidenceFamily,
    val role: RoleId,
    val source: EvidenceSource,
    val polarity: EvidencePolarity,
    val strength: EvidenceStrength,
    val complete: Boolean,
    val detailCode: String
) {
    init {
        require(evidenceId.isNotBlank())
        require(source.artifactSha256.matches(Regex("[a-fA-F0-9]{64}")))
        require(source.artifactPath.isNotBlank())
        require(source.toolVersion.isNotBlank())
        require(detailCode.matches(Regex("[A-Z0-9_.:-]{1,96}")))
    }
}

enum class ProfileStatus { DRAFT, STATIC_VERIFIED, RUNTIME_VERIFIED, DEPRECATED, QUARANTINED }

data class HostProfileBinding(
    val packageName: String,
    val versionName: String,
    val versionCode: Long,
    val signingCertSha256: String,
    val baseApkSha256: String,
    val splitApkSha256: Set<String>,
    val dexFingerprint: String
)

data class ProfileMethodCandidate(
    val method: MethodDescriptor,
    val requiredEvidenceFamilies: Set<EvidenceFamily>,
    val forbiddenEvidenceCodes: Set<String> = emptySet()
)

data class SemanticRoleProfile(
    val role: RoleId,
    val candidates: List<ProfileMethodCandidate>,
    val minimumEvidenceFamilies: Int,
    val requiredEvidenceFamilies: Set<EvidenceFamily>,
    val forbiddenEvidenceCodes: Set<String> = emptySet()
)

data class HookProfile(
    val schemaMajor: Int,
    val profileId: String,
    val revision: Int,
    val status: ProfileStatus,
    val host: HostProfileBinding,
    val roles: List<SemanticRoleProfile>
)

enum class ProfileRejection {
    UNSUPPORTED_SCHEMA, INVALID_PROFILE_ID, INVALID_REVISION, QUARANTINED,
    HOST_PACKAGE_MISMATCH, HOST_VERSION_MISMATCH, HOST_VERSION_CODE_MISMATCH,
    SIGNING_CERT_MISMATCH, BASE_APK_MISMATCH, SPLIT_APK_MISMATCH,
    DEX_FINGERPRINT_MISMATCH, INVALID_HOST_BINDING, DUPLICATE_ROLE,
    EMPTY_ROLE_CANDIDATES, INVALID_METHOD_DESCRIPTOR, INVALID_EVIDENCE_POLICY
}

data class ProfileValidationResult(
    val accepted: Boolean,
    val rejections: Set<ProfileRejection>
)

class HookProfileValidator(private val supportedSchemaMajor: Int = 1) {
    fun validate(profile: HookProfile, host: HostIdentity): ProfileValidationResult {
        val errors = linkedSetOf<ProfileRejection>()
        if (profile.schemaMajor != supportedSchemaMajor) errors += ProfileRejection.UNSUPPORTED_SCHEMA
        if (!profile.profileId.matches(Regex("[a-zA-Z0-9][a-zA-Z0-9._-]{1,95}"))) errors += ProfileRejection.INVALID_PROFILE_ID
        if (profile.revision < 1) errors += ProfileRejection.INVALID_REVISION
        if (profile.status == ProfileStatus.QUARANTINED || profile.status == ProfileStatus.DEPRECATED) errors += ProfileRejection.QUARANTINED
        if (!host.isComplete()) errors += ProfileRejection.INVALID_HOST_BINDING

        val binding = profile.host
        if (binding.packageName != host.packageName) errors += ProfileRejection.HOST_PACKAGE_MISMATCH
        if (binding.versionName != host.versionName) errors += ProfileRejection.HOST_VERSION_MISMATCH
        if (binding.versionCode != host.versionCode) errors += ProfileRejection.HOST_VERSION_CODE_MISMATCH
        if (!binding.signingCertSha256.equals(host.signingCertSha256, true)) errors += ProfileRejection.SIGNING_CERT_MISMATCH
        if (!binding.baseApkSha256.equals(host.baseApkSha256, true)) errors += ProfileRejection.BASE_APK_MISMATCH
        if (binding.splitApkSha256.map { it.lowercase() }.toSet() != host.splitApkSha256.map { it.lowercase() }.toSet()) errors += ProfileRejection.SPLIT_APK_MISMATCH
        if (!binding.dexFingerprint.equals(host.dexFingerprint, true)) errors += ProfileRejection.DEX_FINGERPRINT_MISMATCH

        val roleIds = profile.roles.map { it.role }
        if (roleIds.size != roleIds.toSet().size) errors += ProfileRejection.DUPLICATE_ROLE
        profile.roles.forEach { role ->
            if (role.candidates.isEmpty()) errors += ProfileRejection.EMPTY_ROLE_CANDIDATES
            if (role.minimumEvidenceFamilies < 1 || role.minimumEvidenceFamilies < role.requiredEvidenceFamilies.size || !role.requiredEvidenceFamilies.containsAll(role.candidates.flatMap { it.requiredEvidenceFamilies }.toSet())) {
                errors += ProfileRejection.INVALID_EVIDENCE_POLICY
            }
            if (role.candidates.any { !it.method.isValid }) errors += ProfileRejection.INVALID_METHOD_DESCRIPTOR
            if (role.candidates.map { it.method.stableIdentity }.size != role.candidates.map { it.method.stableIdentity }.toSet().size) errors += ProfileRejection.INVALID_EVIDENCE_POLICY
        }
        return ProfileValidationResult(errors.isEmpty(), errors)
    }
}


enum class AuthorizationRejection {
    INCOMPLETE_HOST_IDENTITY, PROFILE_NOT_RUNTIME_VERIFIED, PROFILE_IDENTITY_REJECTED,
    ROLE_NOT_IN_PROFILE, RESOLUTION_NOT_ACCEPTED, METHOD_NOT_IN_PROFILE,
    EVIDENCE_INCOMPLETE, EVIDENCE_NEGATIVE, HOST_IDENTITY_EVIDENCE_MISSING,
    RUNTIME_EVIDENCE_MISSING, RUNTIME_EVIDENCE_NOT_BOUND_TO_METHOD
}

/** Constructor is module-internal: consumers must obtain a plan from HookAuthorizationPolicy. */
data class AuthorizedHookPlan internal constructor(
    val host: HostIdentity,
    val profileId: String,
    val profileRevision: Int,
    val role: RoleId,
    val method: MethodDescriptor,
    val evidenceIds: Set<String>
)

data class HookAuthorizationResult(
    val plan: AuthorizedHookPlan?,
    val rejections: Set<AuthorizationRejection>
) {
    val authorized: Boolean get() = plan != null && rejections.isEmpty()
}

/**
 * Separates static resolution from installation authorization. A static candidate can never
 * create an AuthorizedHookPlan; the profile and complete, positive runtime evidence are required.
 */
class HookAuthorizationPolicy(private val profileValidator: HookProfileValidator = HookProfileValidator()) {
    fun authorize(
        host: HostIdentity,
        profile: HookProfile,
        roleId: RoleId,
        resolution: Resolution,
        evidence: List<AuditableEvidence>
    ): HookAuthorizationResult {
        val errors = linkedSetOf<AuthorizationRejection>()
        if (!host.isComplete()) errors += AuthorizationRejection.INCOMPLETE_HOST_IDENTITY
        if (profile.status != ProfileStatus.RUNTIME_VERIFIED) errors += AuthorizationRejection.PROFILE_NOT_RUNTIME_VERIFIED
        if (!profileValidator.validate(profile, host).accepted) errors += AuthorizationRejection.PROFILE_IDENTITY_REJECTED

        val roleProfile = profile.roles.singleOrNull { it.role == roleId }
        if (roleProfile == null) errors += AuthorizationRejection.ROLE_NOT_IN_PROFILE
        if (!resolution.accepted || resolution.selected == null || resolution.role != roleId) {
            errors += AuthorizationRejection.RESOLUTION_NOT_ACCEPTED
        }

        val selected = resolution.selected
        val method = selected?.let {
            MethodDescriptor.parse(it.method.ownerDescriptor, it.method.name, it.method.descriptor)
        }
        if (selected != null && (selected.role != roleId || selected.host.packageName != host.packageName ||
                selected.host.versionCode != host.versionCode || selected.host.versionName != host.versionName ||
                selected.host.signingDigest != host.signingCertSha256 || selected.host.dexDigest != host.dexFingerprint ||
                selected.host.classLoaderId != host.classLoaderId)) {
            errors += AuthorizationRejection.PROFILE_IDENTITY_REJECTED
        }
        if (method == null || roleProfile?.candidates?.none { it.method == method } != false) {
            errors += AuthorizationRejection.METHOD_NOT_IN_PROFILE
        }

        val roleEvidence = evidence.filter { it.role == roleId }
        if (roleEvidence.any { !it.complete }) errors += AuthorizationRejection.EVIDENCE_INCOMPLETE
        if (roleEvidence.any { it.polarity == EvidencePolarity.NEGATIVE }) errors += AuthorizationRejection.EVIDENCE_NEGATIVE
        val positiveComplete = roleEvidence.filter { it.complete && it.polarity == EvidencePolarity.POSITIVE }
        if (positiveComplete.none { it.family == EvidenceFamily.HOST_IDENTITY && it.source.artifactSha256.equals(host.baseApkSha256, true) }) {
            errors += AuthorizationRejection.HOST_IDENTITY_EVIDENCE_MISSING
        }
        val runtimeEvidence = positiveComplete.filter {
            it.family == EvidenceFamily.RUNTIME_BEHAVIOR &&
                it.source.artifactSha256.equals(host.baseApkSha256, true) &&
                it.source.auditRunId?.isNotBlank() == true &&
                it.source.method == method
        }
        if (runtimeEvidence.isEmpty()) errors += AuthorizationRejection.RUNTIME_EVIDENCE_MISSING
        if (positiveComplete.any { it.family == EvidenceFamily.RUNTIME_BEHAVIOR && it.source.method != method }) {
            errors += AuthorizationRejection.RUNTIME_EVIDENCE_NOT_BOUND_TO_METHOD
        }

        val plan = if (errors.isEmpty() && method != null) AuthorizedHookPlan(
            host = host,
            profileId = profile.profileId,
            profileRevision = profile.revision,
            role = roleId,
            method = method,
            evidenceIds = positiveComplete.map { it.evidenceId }.toSet()
        ) else null
        return HookAuthorizationResult(plan, errors)
    }
}
