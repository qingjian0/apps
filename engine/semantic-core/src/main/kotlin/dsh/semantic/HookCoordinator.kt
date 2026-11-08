package dsh.semantic

interface HookBackend { fun install(method: MethodShape, role: RoleId): HookHandle }
interface HookHandle { fun uninstall() }
enum class InstallStatus { INSTALLED, ALREADY_INSTALLED, REJECTED, FAILED }
data class InstallResult(val role: RoleId, val status: InstallStatus, val reason: String? = null)

/** Role-isolated, idempotent coordinator; Android Hook APIs are injected by a platform adapter. */
class HookCoordinator(private val backend: HookBackend) {
    private val lock = Any()
    private val installed = mutableMapOf<String, HookHandle>()

    /** Public installation entry point: only a policy-issued authorization plan is accepted. */
    fun install(plan: AuthorizedHookPlan): InstallResult {
        val host = plan.host
        if (!host.isComplete()) return InstallResult(plan.role, InstallStatus.REJECTED, "runtime-host-identity-incomplete")
        if (!plan.method.isValid) return InstallResult(plan.role, InstallStatus.REJECTED, "invalid-method-descriptor")
        val method = MethodShape(
            ownerDescriptor = plan.method.owner,
            name = plan.method.name,
            descriptor = plan.method.descriptor,
            parameterTypes = plan.method.parameterDescriptors().orEmpty(),
            returnType = plan.method.returnDescriptor().orEmpty()
        )
        if (!method.isWellFormed()) return InstallResult(plan.role, InstallStatus.REJECTED, "method-signature-inconsistent")
        val key = listOf(host.fingerprintId(), host.processName, host.classLoaderId, plan.role.value, method.stableIdentity).joinToString("|")
        return installOnce(key, plan.role, method)
    }

    /**
     * Internal compatibility path retained for in-module tests/migration only.
     * External SDK consumers cannot install from a plain static Resolution.
     */
    internal fun install(host: HostFingerprint, policy: RolePolicy, resolution: Resolution): InstallResult {
        if (!resolution.accepted || resolution.selected == null) return InstallResult(policy.role, InstallStatus.REJECTED, resolution.rejection ?: "unverified-resolution")
        val candidate = resolution.selected
        if (candidate.role != policy.role || candidate.host != host) return InstallResult(policy.role, InstallStatus.REJECTED, "host-or-role-mismatch")
        if (!host.hasCompleteRuntimeIdentity()) return InstallResult(policy.role, InstallStatus.REJECTED, "runtime-host-identity-incomplete")
        val evidenceFamilies = candidate.evidence.map { it.family }.toSet()
        if (EvidenceFamily.HOST_IDENTITY !in evidenceFamilies || EvidenceFamily.RUNTIME_BEHAVIOR !in evidenceFamilies)
            return InstallResult(policy.role, InstallStatus.REJECTED, "runtime-evidence-required")
        val key = listOf(host.packageName, host.dexDigest, host.classLoaderId, policy.role.value, candidate.method.stableIdentity).joinToString("|")
        return installOnce(key, policy.role, candidate.method)
    }

    private fun installOnce(key: String, role: RoleId, method: MethodShape): InstallResult = synchronized(lock) {
        if (key in installed) return@synchronized InstallResult(role, InstallStatus.ALREADY_INSTALLED)
        try {
            installed[key] = backend.install(method, role)
            InstallResult(role, InstallStatus.INSTALLED)
        } catch (error: Throwable) {
            InstallResult(role, InstallStatus.FAILED, error::class.simpleName ?: "backend-error")
        }
    }

    fun uninstallAll(): List<String> = synchronized(lock) {
        val failures = mutableListOf<String>()
        installed.toMap().forEach { (key, handle) ->
            try {
                handle.uninstall()
                installed.remove(key)
            } catch (error: Throwable) {
                failures += (error::class.simpleName ?: "uninstall-error")
            }
        }
        failures.toList()
    }

    fun installedCount(): Int = synchronized(lock) { installed.size }
}
