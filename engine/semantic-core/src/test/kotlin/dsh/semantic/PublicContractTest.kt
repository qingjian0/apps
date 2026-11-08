package dsh.semantic

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

class PublicContractTest {
    private val digest = "a".repeat(64)
    private val host = HostIdentity(
        packageName = "com.deepseek.chat",
        versionName = "2.7.5",
        versionCode = 295,
        signingCertSha256 = digest,
        baseApkSha256 = "b".repeat(64),
        splitApkSha256 = setOf("c".repeat(64)),
        dexFingerprint = "d".repeat(64),
        processName = "com.deepseek.chat",
        classLoaderId = "loader-session-1",
        observedAtEpochMillis = 1L
    )
    private val method = MethodDescriptor("Lx/y/Request;", "submit", "(Ljava/lang/String;[B)Ljava/lang/Object;")
    private val profile = HookProfile(
        schemaMajor = 1,
        profileId = "deepseek-code295",
        revision = 1,
        status = ProfileStatus.STATIC_VERIFIED,
        host = HostProfileBinding(
            packageName = host.packageName,
            versionName = host.versionName!!,
            versionCode = host.versionCode!!,
            signingCertSha256 = host.signingCertSha256!!,
            baseApkSha256 = host.baseApkSha256!!,
            splitApkSha256 = host.splitApkSha256,
            dexFingerprint = host.dexFingerprint!!
        ),
        roles = listOf(
            SemanticRoleProfile(
                role = RoleId("network.route"),
                candidates = listOf(ProfileMethodCandidate(method, setOf(EvidenceFamily.CALL_GRAPH))),
                minimumEvidenceFamilies = 3,
                requiredEvidenceFamilies = setOf(EvidenceFamily.CALL_GRAPH, EvidenceFamily.TYPE_SHAPE)
            )
        )
    )

    @Test fun completeIdentityProducesStableFingerprint() {
        assertTrue(host.isComplete())
        assertEquals(host.fingerprintId(), host.fingerprintId())
        assertEquals(64, host.fingerprintId().length)
    }

    @Test fun incompleteIdentityListsMissingFields() {
        val incomplete = host.copy(baseApkSha256 = null, signingCertSha256 = null)
        assertFalse(incomplete.isComplete())
        assertTrue(IdentityField.BASE_APK_SHA256 in incomplete.missingRequiredFields())
        assertTrue(IdentityField.SIGNING_CERT_SHA256 in incomplete.missingRequiredFields())
    }

    @Test fun methodDescriptorRequiresExactValidJvmGrammar() {
        assertNotNull(MethodDescriptor.parse("Lx/y;", "a", "(I[Ljava/lang/String;)V"))
        assertNotNull(MethodDescriptor.parse("Lx/y;", "<init>", "()V"))
        assertEquals(null, MethodDescriptor.parse("Lx/y;", "a", "(V)V"))
        assertEquals(null, MethodDescriptor.parse("Lx/y;", "a", "(I)"))
        assertEquals(null, MethodDescriptor.parse("Lx.y;", "a", "()V"))
        assertEquals(null, MethodDescriptor.parse("Lx/y;", "a", "([V)V"))
    }

    @Test fun exactHostProfileIsAccepted() {
        val result = HookProfileValidator().validate(profile, host)
        assertTrue(result.accepted, result.rejections.toString())
    }

    @Test fun versionOrApkIdentityMismatchRejectsProfile() {
        val otherVersion = host.copy(versionName = "2.7.4", versionCode = 294)
        val result = HookProfileValidator().validate(profile, otherVersion)
        assertFalse(result.accepted)
        assertTrue(ProfileRejection.HOST_VERSION_MISMATCH in result.rejections)
        assertTrue(ProfileRejection.HOST_VERSION_CODE_MISMATCH in result.rejections)
    }

    @Test fun quarantinedOrUnknownSchemaProfileCannotLoad() {
        val quarantined = profile.copy(status = ProfileStatus.QUARANTINED)
        assertTrue(ProfileRejection.QUARANTINED in HookProfileValidator().validate(quarantined, host).rejections)
        val unknownSchema = profile.copy(schemaMajor = 99)
        assertTrue(ProfileRejection.UNSUPPORTED_SCHEMA in HookProfileValidator().validate(unknownSchema, host).rejections)
    }

    @Test fun malformedCandidateDescriptorRejectsWholeProfile() {
        val malformed = profile.copy(roles = listOf(
            profile.roles.single().copy(candidates = listOf(
                ProfileMethodCandidate(MethodDescriptor("Lx/y;", "submit", "(V)V"), setOf(EvidenceFamily.CALL_GRAPH))
            ))
        ))
        val result = HookProfileValidator().validate(malformed, host)
        assertFalse(result.accepted)
        assertTrue(ProfileRejection.INVALID_METHOD_DESCRIPTOR in result.rejections)
    }

    @Test fun duplicateRolesAndEmptyCandidatesAreRejected() {
        val duplicate = profile.copy(roles = listOf(profile.roles.single(), profile.roles.single()))
        assertTrue(ProfileRejection.DUPLICATE_ROLE in HookProfileValidator().validate(duplicate, host).rejections)
        val empty = profile.copy(roles = listOf(profile.roles.single().copy(candidates = emptyList())))
        assertTrue(ProfileRejection.EMPTY_ROLE_CANDIDATES in HookProfileValidator().validate(empty, host).rejections)
    }
}
