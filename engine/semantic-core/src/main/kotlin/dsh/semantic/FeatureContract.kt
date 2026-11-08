package dsh.semantic

/** Metadata-only event contract. Raw user content and credentials are never accepted. */
enum class SafeEventField {
    ROLE_ID, TEMPLATE_ID, TEMPLATE_HASH, SOURCE_LABEL, ENABLED, CHARACTER_COUNT_BUCKET,
    MODEL_ID, TOOL_ID, TOOL_KIND, STEP_INDEX, STEP_STATE, RESULT_KIND, ROUTE_ID,
    STREAMING, HTTP_STATUS_CLASS, EVENT_KIND, DURATION_BUCKET, ERROR_KIND,
    SESSION_PSEUDONYM, THREAD_KIND
}

data class FeatureContract(
    val role: RoleId,
    val requiredFields: Set<SafeEventField>,
    val optionalFields: Set<SafeEventField> = emptySet(),
    val description: String
) {
    init { require(requiredFields.intersect(optionalFields).isEmpty()) }
    val allowedFields: Set<SafeEventField> get() = requiredFields + optionalFields
}

data class SafeFeatureEvent(val role: RoleId, val fields: Map<SafeEventField, String>)

class FeatureEventSanitizer {
    fun sanitize(contract: FeatureContract, supplied: Map<SafeEventField, String>): SafeFeatureEvent? {
        if (!supplied.keys.containsAll(contract.requiredFields)) return null
        val accepted = supplied.filterKeys { it in contract.allowedFields }
            .filter { (field, value) -> isSafeValue(field, value) }
        if (!accepted.keys.containsAll(contract.requiredFields)) return null
        return SafeFeatureEvent(contract.role, accepted)
    }

    private fun isSafeValue(field: SafeEventField, value: String): Boolean {
        if (value.length !in 1..96 || value.any { it.isISOControl() }) return false
        val token = Regex("[A-Za-z0-9_.:-]{1,96}")
        return when (field) {
            SafeEventField.ENABLED, SafeEventField.STREAMING -> value == "true" || value == "false"
            SafeEventField.SOURCE_LABEL -> value in setOf("system_default", "user_custom_instruction", "agent_instruction", "conversation_context", "developer_template", "tool_schema", "unknown")
            SafeEventField.CHARACTER_COUNT_BUCKET -> value in setOf("0", "1-32", "33-128", "129-512", "513-2048", "2049+")
            SafeEventField.HTTP_STATUS_CLASS -> value in setOf("1xx", "2xx", "3xx", "4xx", "5xx")
            SafeEventField.SESSION_PSEUDONYM, SafeEventField.TEMPLATE_HASH -> value.matches(Regex("[a-fA-F0-9]{16,96}"))
            SafeEventField.DURATION_BUCKET -> value in setOf("<10ms", "10-50ms", "50-200ms", "200ms-1s", "1-5s", "5s+")
            else -> token.matches(value)
        }
    }
}

object DeepSeekFeatureContracts {
    val all: List<FeatureContract> = listOf(
        FeatureContract(RoleId("prompt.compose"), setOf(SafeEventField.SOURCE_LABEL), setOf(SafeEventField.TEMPLATE_ID, SafeEventField.TEMPLATE_HASH, SafeEventField.ENABLED, SafeEventField.CHARACTER_COUNT_BUCKET), "Prompt assembly metadata only; never prompt text"),
        FeatureContract(RoleId("agent.tool.dispatch"), setOf(SafeEventField.TOOL_KIND, SafeEventField.STEP_STATE), setOf(SafeEventField.TOOL_ID, SafeEventField.STEP_INDEX, SafeEventField.MODEL_ID), "Agent tool dispatch metadata"),
        FeatureContract(RoleId("agent.result"), setOf(SafeEventField.RESULT_KIND), setOf(SafeEventField.TOOL_KIND, SafeEventField.STEP_INDEX, SafeEventField.STEP_STATE), "Agent result type and state only"),
        FeatureContract(RoleId("local_api.request"), setOf(SafeEventField.ROUTE_ID, SafeEventField.STREAMING), setOf(SafeEventField.MODEL_ID, SafeEventField.HTTP_STATUS_CLASS, SafeEventField.DURATION_BUCKET), "Local API routing metadata; no request body or API key"),
        FeatureContract(RoleId("conversation.submit"), setOf(SafeEventField.EVENT_KIND), setOf(SafeEventField.SESSION_PSEUDONYM, SafeEventField.MODEL_ID, SafeEventField.DURATION_BUCKET), "Conversation lifecycle metadata; no message content"),
        FeatureContract(RoleId("sse.dispatch"), setOf(SafeEventField.EVENT_KIND), setOf(SafeEventField.STEP_STATE, SafeEventField.ERROR_KIND, SafeEventField.DURATION_BUCKET), "Stream event metadata; no delta payload"),
        FeatureContract(RoleId("prompt.instruction.apply"), setOf(SafeEventField.SOURCE_LABEL, SafeEventField.ENABLED), setOf(SafeEventField.TEMPLATE_ID, SafeEventField.TEMPLATE_HASH), "Instruction source and toggle metadata only"),
        FeatureContract(RoleId("agent.plan"), setOf(SafeEventField.STEP_STATE), setOf(SafeEventField.STEP_INDEX, SafeEventField.MODEL_ID), "Agent planning state; no plan text"),
        FeatureContract(RoleId("tool.registry"), setOf(SafeEventField.TOOL_KIND), setOf(SafeEventField.TOOL_ID), "Tool capability registration metadata"),
        FeatureContract(RoleId("local_api.server"), setOf(SafeEventField.ROUTE_ID), setOf(SafeEventField.STREAMING), "Local API listener and route metadata; no bind secret"),
        FeatureContract(RoleId("local_api.stream"), setOf(SafeEventField.ROUTE_ID, SafeEventField.STREAMING), setOf(SafeEventField.EVENT_KIND, SafeEventField.DURATION_BUCKET), "Local API stream lifecycle metadata"),
        FeatureContract(RoleId("conversation.history"), setOf(SafeEventField.EVENT_KIND), setOf(SafeEventField.SESSION_PSEUDONYM), "Conversation history metadata only"),
        FeatureContract(RoleId("multimodal.image"), setOf(SafeEventField.EVENT_KIND), setOf(SafeEventField.MODEL_ID), "Image pipeline stage metadata; no image bytes or OCR text"),
        FeatureContract(RoleId("multimodal.audio"), setOf(SafeEventField.EVENT_KIND), setOf(SafeEventField.MODEL_ID), "Audio pipeline stage metadata; no transcript or audio bytes"),
        FeatureContract(RoleId("attachment.file"), setOf(SafeEventField.EVENT_KIND), setOf(SafeEventField.DURATION_BUCKET), "Attachment stage metadata; no filename or file content"),
        FeatureContract(RoleId("search.query"), setOf(SafeEventField.EVENT_KIND), setOf(SafeEventField.TOOL_KIND, SafeEventField.DURATION_BUCKET), "Search stage metadata; no query or result text"),
        FeatureContract(RoleId("storage.preference"), setOf(SafeEventField.EVENT_KIND), setOf(SafeEventField.ENABLED), "Preference change metadata; no stored values"),
        FeatureContract(RoleId("settings.toggle"), setOf(SafeEventField.EVENT_KIND, SafeEventField.ENABLED), emptySet(), "Settings toggle metadata only")
    )
}
