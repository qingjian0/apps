package dsh.semantic

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

class SemanticResolverTest {
    private val host = HostFingerprint("com.deepseek.chat", 289, "2.7.2", "cert", "dex-sha", "loader-1")
    private val role = RoleId("prompt.compose")
    private val policy = RolePolicy(role, minimumEvidenceFamilies = 3, minimumScore = 2.0, minimumWinnerMargin = 0.3)
    private fun candidate(name: String, evidence: List<Evidence>, hostOverride: HostFingerprint = host) = SemanticCandidate(
        role, MethodShape("Lx/y;", name, "()V", emptyList(), "V"), hostOverride, evidence
    )
    private fun runtimeConfirmed(resolution: Resolution): Resolution = resolution.copy(selected = resolution.selected?.let { candidate -> candidate.copy(evidence = candidate.evidence + listOf(Evidence(EvidenceFamily.HOST_IDENTITY, "package+version+signature+dex+loader", 1.0), Evidence(EvidenceFamily.RUNTIME_BEHAVIOR, "triggered-in-target-operation", 1.0))) })
    private val goodEvidence = listOf(
        Evidence(EvidenceFamily.PROTOCOL_ANCHOR, "prompt-template-schema", 0.9),
        Evidence(EvidenceFamily.TYPE_SHAPE, "prompt-dto-input", 0.8),
        Evidence(EvidenceFamily.DATA_FLOW, "dto-to-request-field", 0.9)
    )

    @Test fun resolvesRenamedMethodFromIndependentEvidence() {
        val result = SemanticResolver().resolve(host, policy, listOf(candidate("a", goodEvidence)))
        assertTrue(result.accepted)
        assertEquals("a", result.selected?.method?.name)
    }

    @Test fun repeatedSameFamilyEvidenceCannotFakeDiversity() {
        val repeated = List(10) { Evidence(EvidenceFamily.PROTOCOL_ANCHOR, "marker-$it", 1.0) }
        val result = SemanticResolver().resolve(host, policy, listOf(candidate("a", repeated)))
        assertFalse(result.accepted)
        assertEquals("insufficient-independent-evidence", result.rejection)
    }

    @Test fun ambiguousCandidatesFailClosed() {
        val result = SemanticResolver().resolve(host, policy, listOf(candidate("a", goodEvidence), candidate("b", goodEvidence)))
        assertFalse(result.accepted)
        assertEquals("ambiguous-candidates", result.rejection)
    }

    @Test fun candidateFromDifferentHostIsIgnored() {
        val other = host.copy(dexDigest = "other-dex")
        val result = SemanticResolver().resolve(host, policy, listOf(candidate("a", goodEvidence, other)))
        assertFalse(result.accepted)
        assertEquals("no-well-formed-host-matched-candidates", result.rejection)
    }

    @Test fun malformedMethodDescriptorIsRejected() {
        val malformed = candidate("a", goodEvidence).copy(method = MethodShape("not-a-descriptor", "a", "broken", emptyList(), "V"))
        val result = SemanticResolver().resolve(host, policy, listOf(malformed))
        assertFalse(result.accepted)
        assertEquals("no-well-formed-host-matched-candidates", result.rejection)
    }

    @Test fun nonDeepSeekHostIsRejected() {
        val untrusted = host.copy(packageName = "example.other")
        val result = SemanticResolver().resolve(untrusted, policy, listOf(candidate("a", goodEvidence)))
        assertFalse(result.accepted)
        assertEquals("untrusted-or-incomplete-host", result.rejection)
    }

    @Test fun forbiddenNegativeEvidenceRejectsCandidate() {
        val candidate = candidate("a", goodEvidence).copy(negativeEvidence = setOf("ui-click-handler"))
        val guarded = policy.copy(forbiddenNegativeEvidence = setOf("ui-click-handler"))
        val result = SemanticResolver().resolve(host, guarded, listOf(candidate))
        assertFalse(result.accepted)
        assertTrue(result.rejection!!.startsWith("forbidden-negative-evidence"))
    }

    @Test fun backendFailureForOneRoleDoesNotBlockAnotherRole() {
        val failedRole = RoleId("prompt.compose")
        val workingRole = RoleId("agent.plan")
        val failedCandidate = candidate("bad", goodEvidence).copy(role = failedRole)
        val workingCandidate = candidate("good", goodEvidence).copy(role = workingRole)
        val resolver = SemanticResolver()
        val failedResolution = runtimeConfirmed(resolver.resolve(host, RolePolicy(failedRole, minimumEvidenceFamilies = 3), listOf(failedCandidate)))
        val workingResolution = runtimeConfirmed(resolver.resolve(host, RolePolicy(workingRole, minimumEvidenceFamilies = 3), listOf(workingCandidate)))
        val backend = object : HookBackend {
            override fun install(method: MethodShape, role: RoleId): HookHandle {
                if (role == failedRole) throw IllegalStateException("simulated failure")
                return object : HookHandle { override fun uninstall() {} }
            }
        }
        val coordinator = HookCoordinator(backend)
        assertEquals(InstallStatus.FAILED, coordinator.install(host, RolePolicy(failedRole, minimumEvidenceFamilies = 3), failedResolution).status)
        assertEquals(InstallStatus.INSTALLED, coordinator.install(host, RolePolicy(workingRole, minimumEvidenceFamilies = 3), workingResolution).status)
        assertEquals(1, coordinator.installedCount())
    }

    @Test fun coordinatorIsIdempotentAndRoleIsolated() {
        var installs = 0
        val backend = object : HookBackend {
            override fun install(method: MethodShape, role: RoleId): HookHandle {
                installs++
                return object : HookHandle { override fun uninstall() {} }
            }
        }
        val resolver = SemanticResolver()
        val resolution = runtimeConfirmed(resolver.resolve(host, policy, listOf(candidate("a", goodEvidence))))
        val coordinator = HookCoordinator(backend)
        assertEquals(InstallStatus.INSTALLED, coordinator.install(host, policy, resolution).status)
        assertEquals(InstallStatus.ALREADY_INSTALLED, coordinator.install(host, policy, resolution).status)
        assertEquals(1, installs)
        assertEquals(1, coordinator.installedCount())
        assertEquals(emptyList(), coordinator.uninstallAll())
        assertEquals(0, coordinator.installedCount())
    }
    @Test fun staticOnlyResolutionCannotInstallHook() {
        val resolution = SemanticResolver().resolve(host, policy, listOf(candidate("a", goodEvidence)))
        val backend = object : HookBackend {
            override fun install(method: MethodShape, role: RoleId): HookHandle =
                object : HookHandle { override fun uninstall() {} }
        }
        val result = HookCoordinator(backend).install(host, policy, resolution)
        assertEquals(InstallStatus.REJECTED, result.status)
        assertEquals("runtime-evidence-required", result.reason)
    }

    @Test fun incompleteRuntimeIdentityCannotInstallHookEvenWithRuntimeMarkers() {
        val incomplete = host.copy(signingDigest = null)
        val resolution = runtimeConfirmed(SemanticResolver().resolve(incomplete, policy, listOf(candidate("a", goodEvidence, incomplete))))
        val backend = object : HookBackend {
            override fun install(method: MethodShape, role: RoleId): HookHandle =
                object : HookHandle { override fun uninstall() {} }
        }
        val result = HookCoordinator(backend).install(incomplete, policy, resolution)
        assertEquals(InstallStatus.REJECTED, result.status)
        assertEquals("runtime-host-identity-incomplete", result.reason)
    }

    @Test fun borderlineWinnerMarginFailsClosed() {
        val weaker = candidate("b", listOf(
            Evidence(EvidenceFamily.PROTOCOL_ANCHOR, "prompt-template-schema", 0.85),
            Evidence(EvidenceFamily.TYPE_SHAPE, "prompt-dto-input", 0.8),
            Evidence(EvidenceFamily.DATA_FLOW, "dto-to-request-field", 0.9)
        ))
        val result = SemanticResolver().resolve(host, RolePolicy(role, minimumEvidenceFamilies = 3), listOf(candidate("a", goodEvidence), weaker))
        assertFalse(result.accepted)
        assertEquals("ambiguous-candidates", result.rejection)
    }

    @Test fun thirdPartySdkCandidateIsRejectedByDefaultPolicy() {
        val sdkCandidate = candidate("o", goodEvidence).copy(
            method = MethodShape("Lcn/fly/verify/bq;", "o", "(Z)Ljava/lang/String;", listOf("Z"), "Ljava/lang/String;"),
            negativeEvidence = setOf("third-party-sdk-owner")
        )
        val result = SemanticResolver().resolve(host, RolePolicy(role, minimumEvidenceFamilies = 3), listOf(sdkCandidate))
        assertFalse(result.accepted)
        assertTrue(result.rejection!!.startsWith("forbidden-negative-evidence"))
    }

    @Test fun productionPoliciesRequireRoleSpecificIndependentEvidence() {
        val promptPolicy = RolePolicy.forRole(RoleId("prompt.compose"))
        assertTrue(promptPolicy.minimumEvidenceFamilies >= 4)
        assertTrue(promptPolicy.requiredFamilies.containsAll(setOf(
            EvidenceFamily.PROTOCOL_ANCHOR, EvidenceFamily.CALL_GRAPH,
            EvidenceFamily.TYPE_SHAPE, EvidenceFamily.DATA_FLOW
        )))
        val ssePolicy = RolePolicy.forRole(RoleId("sse.parse"))
        assertTrue(EvidenceFamily.CONTROL_FLOW in ssePolicy.requiredFamilies)
    }

    @Test fun productionRolePolicyRejectsCandidateMissingRequiredDataFlow() {
        val productionPolicy = RolePolicy.forRole(role)
        val incompleteEvidence = goodEvidence.filterNot { it.family == EvidenceFamily.DATA_FLOW } + listOf(
            Evidence(EvidenceFamily.FRAMEWORK_INTERACTION, "stable-framework-boundary", 0.8),
            Evidence(EvidenceFamily.CONTROL_FLOW, "branch-shape", 0.8)
        )
        val result = SemanticResolver().resolve(host, productionPolicy, listOf(candidate("a", incompleteEvidence)))
        assertFalse(result.accepted)
        assertEquals("required-evidence-family-missing", result.rejection)
    }

}
