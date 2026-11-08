package dsh.semantic

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class HookProfileJsonCodecTest {
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
        classLoaderId = "loader-1",
        observedAtEpochMillis = 1L
    )

    private fun profileJson(schemaMajor: Int = 1, status: String = "STATIC_VERIFIED") = """
        {
          "schemaMajor": $schemaMajor,
          "profileId": "deepseek-code295",
          "revision": 1,
          "status": "$status",
          "host": {
            "packageName": "com.deepseek.chat",
            "versionName": "2.7.5",
            "versionCode": 295,
            "signingCertSha256": "${host.signingCertSha256}",
            "baseApkSha256": "${host.baseApkSha256}",
            "splitApkSha256": ["${host.splitApkSha256.single()}"],
            "dexFingerprint": "${host.dexFingerprint}"
          },
          "roles": [{
            "role": "network.route",
            "minimumEvidenceFamilies": 3,
            "requiredEvidenceFamilies": ["CALL_GRAPH", "TYPE_SHAPE"],
            "forbiddenEvidenceCodes": [],
            "candidates": [{
              "method": {
                "owner": "Lx/y/Request;",
                "name": "submit",
                "descriptor": "(Ljava/lang/String;[B)Ljava/lang/Object;"
              },
              "requiredEvidenceFamilies": ["CALL_GRAPH"],
              "forbiddenEvidenceCodes": []
            }]
          }]
        }
    """.trimIndent()

    @Test fun decodesAndValidatesExactProfile() {
        val result = HookProfileJsonCodec().decodeAndValidate(profileJson(), host)
        assertTrue(result.accepted, result.rejection.toString() + result.decodeError.orEmpty())
        assertEquals("deepseek-code295", result.profile?.profileId)
        assertEquals("network.route", result.profile?.roles?.single()?.role?.value)
    }

    @Test fun unknownSchemaDecodesButFailsClosedDuringValidation() {
        val result = HookProfileJsonCodec().decodeAndValidate(profileJson(schemaMajor = 9), host)
        assertFalse(result.accepted)
        assertTrue(ProfileRejection.UNSUPPORTED_SCHEMA in result.rejection)
    }

    @Test fun quarantinedProfileCannotBeLoaded() {
        val result = HookProfileJsonCodec().decodeAndValidate(profileJson(status = "QUARANTINED"), host)
        assertFalse(result.accepted)
        assertTrue(ProfileRejection.QUARANTINED in result.rejection)
    }

    @Test fun malformedJsonAndUnknownEnumsReturnStructuredDecodeErrors() {
        val codec = HookProfileJsonCodec()
        val malformed = codec.decode("{")
        assertFalse(malformed.decoded)
        assertEquals("INVALID_JSON", malformed.errorCode)
        val unknownStatus = codec.decode(profileJson(status = "TRUSTED_FOREVER"))
        assertFalse(unknownStatus.decoded)
        assertEquals("INVALID_PROFILE_SHAPE", unknownStatus.errorCode)
    }

    @Test fun descriptorIsValidatedAfterJsonDecode() {
        val malformed = profileJson().replace("(Ljava/lang/String;[B)Ljava/lang/Object;", "(V)V")
        val result = HookProfileJsonCodec().decodeAndValidate(malformed, host)
        assertFalse(result.accepted)
        assertTrue(ProfileRejection.INVALID_METHOD_DESCRIPTOR in result.rejection)
    }
}
