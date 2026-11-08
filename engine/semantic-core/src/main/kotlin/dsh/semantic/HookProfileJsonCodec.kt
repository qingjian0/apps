package dsh.semantic

import kotlinx.serialization.SerializationException
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.contentOrNull
import kotlinx.serialization.json.intOrNull
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import kotlinx.serialization.json.longOrNull

data class HookProfileDecodeResult(
    val profile: HookProfile?,
    val errorCode: String? = null,
    val detail: String? = null
) {
    val decoded: Boolean get() = profile != null && errorCode == null
}

data class HookProfileLoadResult(
    val profile: HookProfile?,
    val rejection: Set<ProfileRejection>,
    val decodeError: String? = null
) {
    val accepted: Boolean get() = profile != null && rejection.isEmpty() && decodeError == null
}

/** Strict JSON codec for data-only Profile Packs. Profiles never contain executable code. */
class HookProfileJsonCodec(
    private val json: Json = Json { isLenient = false; ignoreUnknownKeys = false }
) {
    fun decode(raw: String): HookProfileDecodeResult = try {
        val root = json.parseToJsonElement(raw).asObject()
        val host = root.requiredObject("host")
        val roles = root.requiredArray("roles").map { roleElement ->
            val role = roleElement.asObject()
            val candidates = role.requiredArray("candidates").map { candidateElement ->
                val candidate = candidateElement.asObject()
                val method = candidate.requiredObject("method")
                ProfileMethodCandidate(
                    method = MethodDescriptor(
                        owner = method.requiredString("owner"),
                        name = method.requiredString("name"),
                        descriptor = method.requiredString("descriptor")
                    ),
                    requiredEvidenceFamilies = candidate.requiredEnumSet("requiredEvidenceFamilies"),
                    forbiddenEvidenceCodes = candidate.optionalStringSet("forbiddenEvidenceCodes")
                )
            }
            SemanticRoleProfile(
                role = RoleId(role.requiredString("role")),
                candidates = candidates,
                minimumEvidenceFamilies = role.requiredInt("minimumEvidenceFamilies"),
                requiredEvidenceFamilies = role.requiredEnumSet("requiredEvidenceFamilies"),
                forbiddenEvidenceCodes = role.optionalStringSet("forbiddenEvidenceCodes")
            )
        }
        val profile = HookProfile(
            schemaMajor = root.requiredInt("schemaMajor"),
            profileId = root.requiredString("profileId"),
            revision = root.requiredInt("revision"),
            status = root.requiredEnum("status"),
            host = HostProfileBinding(
                packageName = host.requiredString("packageName"),
                versionName = host.requiredString("versionName"),
                versionCode = host.requiredLong("versionCode"),
                signingCertSha256 = host.requiredString("signingCertSha256"),
                baseApkSha256 = host.requiredString("baseApkSha256"),
                splitApkSha256 = host.requiredStringSet("splitApkSha256"),
                dexFingerprint = host.requiredString("dexFingerprint")
            ),
            roles = roles
        )
        HookProfileDecodeResult(profile)
    } catch (error: SerializationException) {
        HookProfileDecodeResult(null, "INVALID_JSON", error.message)
    } catch (error: IllegalArgumentException) {
        HookProfileDecodeResult(null, "INVALID_PROFILE_SHAPE", error.message)
    } catch (error: IllegalStateException) {
        HookProfileDecodeResult(null, "INVALID_PROFILE_SHAPE", error.message)
    }

    fun decodeAndValidate(raw: String, host: HostIdentity): HookProfileLoadResult {
        val decoded = decode(raw)
        val profile = decoded.profile ?: return HookProfileLoadResult(null, emptySet(), decoded.errorCode)
        val validation = HookProfileValidator().validate(profile, host)
        return HookProfileLoadResult(
            profile = profile.takeIf { validation.accepted },
            rejection = validation.rejections
        )
    }
}

private fun JsonElement.asObject(): JsonObject =
    this as? JsonObject ?: throw IllegalArgumentException("expected-object")

private fun JsonObject.requiredElement(key: String): JsonElement =
    this[key] ?: throw IllegalArgumentException("missing-$key")

private fun JsonObject.requiredObject(key: String): JsonObject =
    requiredElement(key).asObject()

private fun JsonObject.requiredArray(key: String): JsonArray =
    requiredElement(key) as? JsonArray ?: throw IllegalArgumentException("expected-array-$key")

private fun JsonObject.requiredString(key: String): String =
    requiredElement(key).jsonPrimitive.let { primitive ->\n        if (!primitive.isString) throw IllegalArgumentException("expected-string-$key")\n        primitive.contentOrNull?.takeIf { it.isNotBlank() }\n    }
        ?: throw IllegalArgumentException("missing-or-empty-$key")

private fun JsonObject.requiredInt(key: String): Int =
    requiredElement(key).jsonPrimitive.intOrNull ?: throw IllegalArgumentException("invalid-int-$key")

private fun JsonObject.requiredLong(key: String): Long =
    requiredElement(key).jsonPrimitive.longOrNull ?: throw IllegalArgumentException("invalid-long-$key")

private inline fun <reified T : Enum<T>> JsonObject.requiredEnum(key: String): T =
    enumValueOf(requiredString(key))

private inline fun <reified T : Enum<T>> JsonObject.requiredEnumSet(key: String): Set<T> =
    requiredArray(key).map { enumValueOf<T>(it.jsonPrimitive.content) }.toSet()

private fun JsonObject.optionalStringSet(key: String): Set<String> =
    (this[key] as? JsonArray)?.map { it.jsonPrimitive.content }?.toSet().orEmpty()
