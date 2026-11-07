package dsh.semantic

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull
import kotlin.test.assertTrue

class FeatureContractTest {
    @Test fun promptContractKeepsMetadataAndDropsUnapprovedFields() {
        val contract = DeepSeekFeatureContracts.all.single { it.role.value == "prompt.compose" }
        val event = FeatureEventSanitizer().sanitize(contract, mapOf(
            SafeEventField.SOURCE_LABEL to "user_custom_instruction",
            SafeEventField.ENABLED to "true",
            SafeEventField.TEMPLATE_ID to "tpl-7"
        ))
        assertEquals(setOf(SafeEventField.SOURCE_LABEL, SafeEventField.ENABLED, SafeEventField.TEMPLATE_ID), event?.fields?.keys)
    }

    @Test fun freeFormPromptTextCannotMasqueradeAsSourceLabel() {
        val contract = DeepSeekFeatureContracts.all.single { it.role.value == "prompt.compose" }
        assertNull(FeatureEventSanitizer().sanitize(contract, mapOf(SafeEventField.SOURCE_LABEL to "You are a helpful assistant")))
    }

    @Test fun arbitrarySingleWordCannotMasqueradeAsPromptSource() {
        val contract = DeepSeekFeatureContracts.all.single { it.role.value == "prompt.compose" }
        assertNull(FeatureEventSanitizer().sanitize(contract, mapOf(SafeEventField.SOURCE_LABEL to "Hello")))
    }

    @Test fun contractsCoverPromptAgentLocalApiAndMultimodalDomains() {
        val roles = DeepSeekFeatureContracts.all.map { it.role.value }.toSet()
        assertTrue(roles.containsAll(setOf("prompt.compose", "prompt.instruction.apply", "agent.plan", "agent.tool.dispatch", "agent.result", "tool.registry", "local_api.server", "local_api.request", "local_api.stream", "multimodal.image", "multimodal.audio", "attachment.file")))
    }

    @Test fun missingRequiredMetadataRejectsEvent() {
        val contract = DeepSeekFeatureContracts.all.single { it.role.value == "agent.tool.dispatch" }
        assertNull(FeatureEventSanitizer().sanitize(contract, mapOf(SafeEventField.TOOL_KIND to "search")))
    }

    @Test fun oversizedOrMultilineFieldIsDroppedAndRequiredFieldFailsClosed() {
        val contract = DeepSeekFeatureContracts.all.single { it.role.value == "prompt.compose" }
        assertNull(FeatureEventSanitizer().sanitize(contract, mapOf(SafeEventField.SOURCE_LABEL to "raw\ncontent")))
        assertNull(FeatureEventSanitizer().sanitize(contract, mapOf(SafeEventField.SOURCE_LABEL to "x".repeat(161))))
    }
}
