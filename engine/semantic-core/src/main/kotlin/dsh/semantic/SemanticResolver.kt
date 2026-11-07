package dsh.semantic

/** Evidence-diverse, ambiguity-intolerant resolver. It never installs hooks itself. */
class SemanticResolver {
    private data class Evaluation(
        val candidate: SemanticCandidate,
        val score: Double,
        val families: Set<EvidenceFamily>,
        val forbidden: Set<String>,
        val missingFamilies: Set<EvidenceFamily>
    )

    fun resolve(host: HostFingerprint, policy: RolePolicy, candidates: List<SemanticCandidate>): Resolution {
        if (!host.isRecognizedTargetHost()) return rejected(policy.role, "untrusted-or-incomplete-host")
        val matching = candidates.filter { it.role == policy.role && it.host == host && it.method.isWellFormed() }
        if (matching.isEmpty()) return rejected(policy.role, "no-well-formed-host-matched-candidates")

        val evaluated = matching.map { candidate ->
            val families = candidate.evidence.map { it.family }.toSet()
            Evaluation(
                candidate = candidate,
                score = score(candidate.evidence),
                families = families,
                forbidden = candidate.negativeEvidence.intersect(policy.forbiddenNegativeEvidence),
                missingFamilies = policy.requiredFamilies - families
            )
        }
        // Ineligible high-scoring candidates must never shadow a lower-scoring candidate
        // that actually satisfies the role's evidence contract.
        val eligible = evaluated.filter {
            it.forbidden.isEmpty() &&
                it.families.size >= policy.minimumEvidenceFamilies &&
                it.missingFamilies.isEmpty() &&
                it.score >= policy.minimumScore
        }.sortedWith(compareByDescending<Evaluation> { it.score }.thenBy { it.candidate.method.stableIdentity })

        if (eligible.isEmpty()) {
            val best = evaluated.sortedWith(
                compareBy<Evaluation> { it.forbidden.isNotEmpty() }
                    .thenBy { it.families.size < policy.minimumEvidenceFamilies }
                    .thenBy { it.missingFamilies.size }
                    .thenBy { it.score }
                    .thenBy { it.candidate.method.stableIdentity }
            ).last()
            val reason = when {
                best.forbidden.isNotEmpty() -> "forbidden-negative-evidence:" + best.forbidden.sorted().joinToString()
                best.families.size < policy.minimumEvidenceFamilies -> "insufficient-independent-evidence"
                best.missingFamilies.isNotEmpty() -> "required-evidence-family-missing"
                best.score < policy.minimumScore -> "score-below-threshold"
                else -> "no-eligible-candidate"
            }
            return Resolution(policy.role, null, best.score, 0.0, best.families, reason)
        }

        val best = eligible.first()
        val second = eligible.getOrNull(1)?.score ?: 0.0
        if (eligible.size > 1 && best.score - second < policy.minimumWinnerMargin) {
            return Resolution(policy.role, null, best.score, second, best.families, "ambiguous-candidates")
        }
        return Resolution(policy.role, best.candidate, best.score, second, best.families)
    }

    /**
     * Evidence families remain independent units. Within PROTOCOL_ANCHOR only,
     * additional distinct strong anchors contribute a small capped coherence bonus;
     * repeated strings never increase evidence-family diversity.
     */
    private fun score(evidence: List<Evidence>): Double =
        evidence.groupBy { it.family }.entries.sumOf { (family, group) ->
            val weights = group.map { it.weight }.sortedDescending()
            val strongest = weights.firstOrNull() ?: 0.0
            if (family == EvidenceFamily.PROTOCOL_ANCHOR) {
                strongest + weights.drop(1).filter { it >= 0.65 }.sum() .times(0.10).coerceAtMost(0.20)
            } else {
                strongest
            }
        }

    private fun rejected(role: RoleId, reason: String) =
        Resolution(role, null, 0.0, 0.0, emptySet(), reason)
}
