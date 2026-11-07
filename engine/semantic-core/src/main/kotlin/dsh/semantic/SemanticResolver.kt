package dsh.semantic

/** Evidence-diverse, ambiguity-intolerant resolver. It never installs hooks itself. */
class SemanticResolver {
    fun resolve(host: HostFingerprint, policy: RolePolicy, candidates: List<SemanticCandidate>): Resolution {
        if (!host.isUsableForHooking()) return rejected(policy.role, "untrusted-or-incomplete-host")
        val matching = candidates.filter { it.role == policy.role && it.host == host && it.method.isWellFormed() }
        if (matching.isEmpty()) return rejected(policy.role, "no-well-formed-host-matched-candidates")
        val ranked = matching.map { candidate ->
            val families = candidate.evidence.map { it.family }.toSet()
            val score = candidate.evidence.groupBy { it.family }.values.sumOf { group -> group.maxOfOrNull { it.weight } ?: 0.0 }
            Triple(candidate, score, families)
        }.sortedWith(compareByDescending<Triple<SemanticCandidate, Double, Set<EvidenceFamily>>> { it.second }.thenBy { it.first.method.stableIdentity })
        val best = ranked.first()
        val second = ranked.getOrNull(1)?.second ?: 0.0
        val forbidden = best.first.negativeEvidence.intersect(policy.forbiddenNegativeEvidence)
        if (forbidden.isNotEmpty()) return Resolution(policy.role, null, best.second, second, best.third, "forbidden-negative-evidence:" + forbidden.sorted().joinToString())
        if (best.third.size < policy.minimumEvidenceFamilies) return Resolution(policy.role, null, best.second, second, best.third, "insufficient-independent-evidence")
        if (!best.third.containsAll(policy.requiredFamilies)) return Resolution(policy.role, null, best.second, second, best.third, "required-evidence-family-missing")
        if (best.second < policy.minimumScore) return Resolution(policy.role, null, best.second, second, best.third, "score-below-threshold")
        if (ranked.size > 1 && best.second - second < policy.minimumWinnerMargin) return Resolution(policy.role, null, best.second, second, best.third, "ambiguous-candidates")
        return Resolution(policy.role, best.first, best.second, second, best.third)
    }
    private fun rejected(role: RoleId, reason: String) = Resolution(role, null, 0.0, 0.0, emptySet(), reason)
}
