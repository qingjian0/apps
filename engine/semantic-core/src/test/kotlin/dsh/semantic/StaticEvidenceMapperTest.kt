package dsh.semantic

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class StaticEvidenceMapperTest {
    @Test fun obfuscatedClassAndMethodNamesDoNotDefineSemanticRole() {
        val host = HostFingerprint("com.deepseek.chat", 301, "future", "cert", "dex-new", "loader-new")
        val record = StaticMethodRecord(
            ownerDescriptor = "Lq/a/z;", methodName = "m_91", descriptor = "(Ljava/lang/String;)V",
            parameterTypes = listOf("Ljava/lang/String;"), returnType = "V",
            invokes = listOf("Lkotlinx/coroutines/flow/Flow;->emit(Ljava/lang/Object;)V", "Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;"),
            opcodeCount = 42,
            roles = listOf(StaticRoleEvidence("prompt_pipeline", listOf("custom_instructions", "prompt_template")))
        )
        val candidate = StaticEvidenceMapper().map(host, record).single()
        assertEquals("prompt.compose", candidate.role.value)
        assertEquals("m_91", candidate.method.name)
        assertTrue(candidate.evidence.map { it.family }.toSet().size >= 4)
        val resolution = SemanticResolver().resolve(host, RolePolicy(candidate.role, minimumScore = 2.0), listOf(candidate))
        assertTrue(resolution.accepted)
    }
    @Test fun rareAnchorsReceiveHigherSpecificityThanCommonAnchors() {
        val host = HostFingerprint("com.deepseek.chat", 301, "future", "cert", "dex-new", "loader-new")
        val record = StaticMethodRecord(
            "Lq/a;", "m", "()V", emptyList(), "V", emptyList(), 8,
            listOf(StaticRoleEvidence("prompt_pipeline", listOf("custom_instructions", "prompt")))
        )
        val candidate = StaticEvidenceMapper().map(host, record, mapOf("custom_instructions" to 1, "prompt" to 400)).single()
        val weights = candidate.evidence.filter { it.family == EvidenceFamily.PROTOCOL_ANCHOR }.associate { it.key to it.weight }
        assertTrue(weights.getValue("custom_instructions") > weights.getValue("prompt"))
    }
    @Test fun moduleOwnedLocalApiGatewayIsNotResolvedFromHostApk() {
        val host = HostFingerprint("com.deepseek.chat", null, "2.7.3", null, "dex", "static-audit")
        val record = StaticMethodRecord(
            "Lx/Gateway;", "route", "(Ljava/lang/String;)V", listOf("Ljava/lang/String;"), "V",
            listOf("Ljava/net/ServerSocket;->accept()Ljava/net/Socket;"), 24,
            listOf(StaticRoleEvidence("local_api_gateway", listOf("local_api_gateway", "chat_completions")))
        )
        assertTrue(StaticEvidenceMapper().map(host, record).isEmpty())
    }

    @Test fun frameworkAndThirdPartySdkOwnersCarryNegativeEvidence() {
        val host = HostFingerprint("com.deepseek.chat", 289, "2.7.2", "cert", "dex", "loader")
        val record = StaticMethodRecord(
            "Lcn/fly/verify/bq;", "o", "(Z)Ljava/lang/String;", listOf("Z"), "Ljava/lang/String;",
            listOf("Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;"), 18,
            listOf(StaticRoleEvidence("request_route", listOf("/api/v0/chat/completion")))
        )
        val candidate = StaticEvidenceMapper().map(host, record).single()
        assertTrue("third-party-sdk-owner" in candidate.negativeEvidence)
    }


}
