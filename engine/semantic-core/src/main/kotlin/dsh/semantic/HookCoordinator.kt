package dsh.semantic

interface HookBackend { fun install(method: MethodShape, role: RoleId): HookHandle }
interface HookHandle { fun uninstall() }
enum class InstallStatus { INSTALLED, ALREADY_INSTALLED, REJECTED, FAILED }
data class InstallResult(val role: RoleId, val status: InstallStatus, val reason: String? = null)

/** Role-isolated, idempotent coordinator; Android Hook APIs are injected by a platform adapter. */
class HookCoordinator(private val backend: HookBackend) {
    private val lock = Any()
    private val installed = mutableMapOf<String, HookHandle>()
    fun install(host: HostFingerprint, policy: RolePolicy, resolution: Resolution): InstallResult {
        if (!resolution.accepted || resolution.selected == null) return InstallResult(policy.role, InstallStatus.REJECTED, resolution.rejection ?: "unverified-resolution")
        val candidate = resolution.selected
        if (candidate.role != policy.role || candidate.host != host) return InstallResult(policy.role, InstallStatus.REJECTED, "host-or-role-mismatch")
        if (!host.hasCompleteRuntimeIdentity()) return InstallResult(policy.role, InstallStatus.REJECTED, "runtime-host-identity-incomplete")
        val evidenceFamilies = candidate.evidence.map { it.family }.toSet()
        if (EvidenceFamily.HOST_IDENTITY !in evidenceFamilies || EvidenceFamily.RUNTIME_BEHAVIOR !in evidenceFamilies)
            return InstallResult(policy.role, InstallStatus.REJECTED, "runtime-evidence-required")
        val key = listOf(host.packageName, host.dexDigest, host.classLoaderId, policy.role.value, candidate.method.stableIdentity).joinToString("|")
        synchronized(lock) {
            if (key in installed) return InstallResult(policy.role, InstallStatus.ALREADY_INSTALLED)
            return try { installed[key] = backend.install(candidate.method, policy.role); InstallResult(policy.role, InstallStatus.INSTALLED) }
            catch (error: Throwable) { InstallResult(policy.role, InstallStatus.FAILED, error::class.simpleName ?: "backend-error") }
        }
    }
    fun uninstallAll(): List<String> = synchronized(lock) {
        val failures = mutableListOf<String>()
        installed.toMap().forEach { (key, handle) -> try { handle.uninstall(); installed.remove(key) } catch (error: Throwable) { failures += (error::class.simpleName ?: "uninstall-error") } }
        failures.toList()
    }
    fun installedCount(): Int = synchronized(lock) { installed.size }
}
