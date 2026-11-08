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

    private fun evidence(
        id: String,
        family: EvidenceFamily,
        methodRef: MethodDescriptor? = method,
        runId: String? = "audit-run-1"
    ) = AuditableEvidence(
        evidenceId = id,
        family = family,
        role = RoleId("network.route"),
        source = EvidenceSource(host.baseApkSha256!!, "audit/base.apk", methodRef, runId, "test-fixture"),
        polarity = EvidencePolarity.POSITIVE,
        strength = EvidenceStrength.DIRECT,
        complete = true,
        detailCode = when (family) {
            EvidenceFamily.HOST_IDENTITY -> "HOST_IDENTITY_MATCHED"
            EvidenceFamily.RUNTIME_BEHAVIOR -> "RUNTIME_TRIGGER_MATCHED"
            EvidenceFamily.CALL_GRAPH -> "CALL_EDGE_CONFIRMED"
            else -> "TYPE_SHAPE_CONFIRMED"
        }
    )

    private fun runtimeEvidence(methodRef: MethodDescriptor = method) = listOf(
        evidence("call-graph-1", EvidenceFamily.CALL_GRAPH),
        evidence("type-shape-1", EvidenceFamily.TYPE_SHAPE),
        evidence("host-identity-1", EvidenceFamily.HOST_IDENTITY, null, null),
        evidence("runtime-trigger-1", EvidenceFamily.RUNTIME_BEHAVIOR, methodRef, "device-run-1")
    )

    private fun acceptedResolution(): Resolution {
        val role = RoleId("network.route")
        val legacyHost = HostFingerprint(
            host.packageName, host.versionCode, host.versionName,
            host.signingCertSha256, host.dexFingerprint!!, host.classLoaderId
        )
        val candidate = SemanticCandidate(
            role,
            MethodShape(method.owner, method.name, method.descriptor, method.parameterDescriptors()!!, method.returnDescriptor()!!),
            legacyHost,
            listOf(
                Evidence(EvidenceFamily.CALL_GRAPH, "request-to-transport", 0.9),
                Evidence(EvidenceFamily.TYPE_SHAPE, "request-shape", 0.9)
            )
        )
        return SemanticResolver().resolve(
            legacyHost,
            RolePolicy(role, minimumEvidenceFamilies = 2, minimumScore = 1.0, requiredFamilies = setOf(EvidenceFamily.CALL_GRAPH, EvidenceFamily.TYPE_SHAPE)),
            listOf(candidate)
        )
    }

    @Test fun malformedSplitApkDigestMakesIdentityIncomplete() {
        val incomplete = host.copy(splitApkSha256 = setOf("not-a-sha256"))
        assertFalse(incomplete.isComplete())
        assertTrue(IdentityField.SPLIT_APK_SHA256 in incomplete.missingRequiredFields())
    }

    @Test fun methodShapeRejectsParameterOrReturnTypeDisagreement() {
        val wrongParameters = MethodShape("Lx/y;", "submit", "(I)V", listOf("Ljava/lang/String;"), "V")
        val wrongReturn = MethodShape("Lx/y;", "submit", "(I)V", listOf("I"), "Ljava/lang/Object;")
        assertFalse(wrongParameters.isWellFormed())
        assertFalse(wrongReturn.isWellFormed())
    }

    @Test fun staticResolutionCannotProduceAuthorizedPlan() {
        val result = HookAuthorizationPolicy().authorize(
            host, profile.copy(status = ProfileStatus.RUNTIME_VERIFIED),
            RoleId("network.route"), acceptedResolution(),
            runtimeEvidence().filterNot { it.family == EvidenceFamily.RUNTIME_BEHAVIOR }
        )
        assertFalse(result.authorized)
        assertTrue(AuthorizationRejection.RUNTIME_EVIDENCE_MISSING in result.rejections)
    }

    @Test fun onlyRuntimeVerifiedExactProfileCanAuthorizeHook() {
        val result = HookAuthorizationPolicy().authorize(
            host, profile.copy(status = ProfileStatus.RUNTIME_VERIFIED),
            RoleId("network.route"), acceptedResolution(), runtimeEvidence()
        )
        assertTrue(result.authorized, result.rejections.toString())
        assertEquals(method, result.plan?.method)
    }

    @Test fun staticVerifiedProfileCannotAuthorizeEvenWithRuntimeEvidence() {
        val result = HookAuthorizationPolicy().authorize(
            host, profile, RoleId("network.route"), acceptedResolution(), runtimeEvidence()
        )
        assertFalse(result.authorized)
        assertTrue(AuthorizationRejection.PROFILE_NOT_RUNTIME_VERIFIED in result.rejections)
    }

    @Test fun runtimeEvidenceMustBindToExactMethod() {
        val otherMethod = MethodDescriptor("Lx/y/Request;", "other", "()V")
        val result = HookAuthorizationPolicy().authorize(
            host, profile.copy(status = ProfileStatus.RUNTIME_VERIFIED),
            RoleId("network.route"), acceptedResolution(), runtimeEvidence(otherMethod)
        )
        assertFalse(result.authorized)
        assertTrue(AuthorizationRejection.RUNTIME_EVIDENCE_MISSING in result.rejections)
        assertTrue(AuthorizationRejection.RUNTIME_EVIDENCE_NOT_BOUND_TO_METHOD in result.rejections)
    }

    @Test fun profileEvidenceRequirementsAreEnforcedBeforeAuthorization() {
        val incomplete = runtimeEvidence().filterNot { it.family == EvidenceFamily.TYPE_SHAPE }
        val result = HookAuthorizationPolicy().authorize(
            host, profile.copy(status = ProfileStatus.RUNTIME_VERIFIED),
            RoleId("network.route"), acceptedResolution(), incomplete
        )
        assertFalse(result.authorized)
        assertTrue(AuthorizationRejection.PROFILE_EVIDENCE_REQUIREMENTS_MISSING in result.rejections)
    }

    @Test fun authorizedPlanIsThePublicCoordinatorInstallInputAndIsIdempotent() {
        var installs = 0
        val authorization = HookAuthorizationPolicy().authorize(
            host, profile.copy(status = ProfileStatus.RUNTIME_VERIFIED),
            RoleId("network.route"), acceptedResolution(), runtimeEvidence()
        )
        val plan = assertNotNull(authorization.plan)
        val coordinator = HookCoordinator(object : HookBackend {
            override fun install(method: MethodShape, role: RoleId): HookHandle {
                installs++
                return object : HookHandle { override fun uninstall() {} }
            }
        })
        assertEquals(InstallStatus.INSTALLED, coordinator.install(plan).status)
        assertEquals(InstallStatus.ALREADY_INSTALLED, coordinator.install(plan).status)
        assertEquals(1, installs)
    }

}
