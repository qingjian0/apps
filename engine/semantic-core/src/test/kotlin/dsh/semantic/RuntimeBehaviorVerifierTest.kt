package dsh.semantic

import kotlin.test.Test
import kotlin.test.assertFalse
import kotlin.test.assertNull
import kotlin.test.assertTrue

class RuntimeBehaviorVerifierTest {
    private val host = HostFingerprint("com.deepseek.chat", 301, "future", "cert", "dex-301", "loader-301")
    private val candidate = SemanticCandidate(
        RoleId("prompt.compose"), MethodShape("Lq/a;", "m9", "()V", emptyList(), "V"), host,
        listOf(
            Evidence(EvidenceFamily.PROTOCOL_ANCHOR, "custom_instructions", 0.9),
            Evidence(EvidenceFamily.TYPE_SHAPE, "prompt-dto", 0.8),
            Evidence(EvidenceFamily.DATA_FLOW, "prompt-source-to-request-field", 0.85)
        )
    )
    private val scenario = BehaviorScenario("send-with-custom-prompt", "idle", setOf("prompt.source.read", "request.dto.write"))

    @Test fun targetScenarioRuntimeEvidenceCanDisambiguateStaticCandidate() {
        val observations = listOf(
            RuntimeObservation(host, candidate.method.stableIdentity, scenario.scenarioId, "prompt.source.read", "main"),
            RuntimeObservation(host, "Lq/b;->wrap()V", scenario.scenarioId, "request.dto.write", "main"),
            RuntimeObservation(host, "Lq/c;->render()V", "idle", "ui.render", "main")
        )
        val enriched = RuntimeBehaviorVerifier().enrich(candidate, observations, scenario)
        assertTrue(enriched != null)
        val result = SemanticResolver().resolve(host, RolePolicy(candidate.role), listOf(enriched!!))
        assertTrue(result.accepted)
    }

    @Test fun baselineOccurrencePreventsFalseRuntimeConfirmation() {
        val observations = listOf(
            RuntimeObservation(host, candidate.method.stableIdentity, scenario.scenarioId, "prompt.source.read", "main"),
            RuntimeObservation(host, candidate.method.stableIdentity, "idle", "prompt.source.read", "main"),
            RuntimeObservation(host, "Lq/b;->wrap()V", scenario.scenarioId, "request.dto.write", "main")
        )
        assertNull(RuntimeBehaviorVerifier().enrich(candidate, observations, scenario))
    }

    @Test fun missingScenarioPhaseDoesNotEnrichCandidate() {
        val observations = listOf(
            RuntimeObservation(host, candidate.method.stableIdentity, scenario.scenarioId, "prompt.source.read", "main")
        )
        assertNull(RuntimeBehaviorVerifier().enrich(candidate, observations, scenario))
    }
}
