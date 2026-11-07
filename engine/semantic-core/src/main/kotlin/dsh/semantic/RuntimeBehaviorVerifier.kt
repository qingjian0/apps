package dsh.semantic

/** Runtime facts contain structural metadata only: no argument values, prompt text, tokens or payloads. */
data class RuntimeObservation(
    val host: HostFingerprint,
    val methodIdentity: String,
    val scenarioId: String,
    val phase: String,
    val threadKind: String,
    val durationBucket: String? = null
)

data class BehaviorScenario(
    val scenarioId: String,
    val baselineScenarioId: String,
    val requiredPhases: Set<String>,
    val minimumTargetHits: Int = 1
)

class RuntimeBehaviorVerifier {
    fun enrich(
        candidate: SemanticCandidate,
        observations: List<RuntimeObservation>,
        scenario: BehaviorScenario
    ): SemanticCandidate? {
        if (candidate.host != observations.firstOrNull()?.host && observations.none { it.host == candidate.host }) return null
        val target = observations.filter { it.host == candidate.host && it.scenarioId == scenario.scenarioId }
        val baseline = observations.filter { it.host == candidate.host && it.scenarioId == scenario.baselineScenarioId }
        val targetHits = target.count { it.methodIdentity == candidate.method.stableIdentity }
        val baselineHits = baseline.count { it.methodIdentity == candidate.method.stableIdentity }
        if (targetHits < scenario.minimumTargetHits || targetHits <= baselineHits) return null
        val observedPhases = target.map { it.phase }.toSet()
        if (!observedPhases.containsAll(scenario.requiredPhases)) return null
        val phaseFingerprint = scenario.requiredPhases.sorted().joinToString(",")
        val runtimeEvidence = Evidence(
            EvidenceFamily.RUNTIME_BEHAVIOR,
            "scenario=" + scenario.scenarioId + ";method-hit-count=" + targetHits + ";phases=" + phaseFingerprint,
            0.95
        )
        return candidate.copy(evidence = candidate.evidence.filterNot { it.family == EvidenceFamily.RUNTIME_BEHAVIOR } + runtimeEvidence)
    }
}
