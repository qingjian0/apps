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
            .filterValues { value -> value.length <= 160 && value.none { it == '\n' || it == '\r' } }
        if (!accepted.keys.containsAll(contract.requiredFields)) return null
        return SafeFeatureEvent(contract.role, accepted)
    }
}

object DeepSeekFeatureContracts {
    val all: List<FeatureContract> = listOf(
        FeatureContract(RoleId("prompt.compose"), setOf(SafeEventField.SOURCE_LABEL), setOf(SafeEventField.TEMPLATE_ID, SafeEventField.TEMPLATE_HASH, SafeEventField.ENABLED, SafeEventField.CHARACTER_COUNT_BUCKET), "Prompt assembly metadata only; never prompt text"),
        FeatureContract(RoleId("agent.tool.dispatch"), setOf(SafeEventField.TOOL_KIND, SafeEventField.STEP_STATE), setOf(SafeEventField.TOOL_ID, SafeEventField.STEP_INDEX, SafeEventField.MODEL_ID), "Agent tool dispatch metadata"),
        FeatureContract(RoleId("agent.result"), setOf(SafeEventField.RESULT_KIND), setOf(SafeEventField.TOOL_KIND, SafeEventField.STEP_INDEX, SafeEventField.STEP_STATE), "Agent result type and state only"),
        FeatureContract(RoleId("local_api.request"), setOf(SafeEventField.ROUTE_ID, SafeEventField.STREAMING), setOf(SafeEventField.MODEL_ID, SafeEventField.HTTP_STATUS_CLASS, SafeEventField.DURATION_BUCKET), "Local API routing metadata; no request body or API key"),
        FeatureContract(RoleId("conversation.submit"), setOf(SafeEventField.EVENT_KIND), setOf(SafeEventField.SESSION_PSEUDONYM, SafeEventField.MODEL_ID, SafeEventField.DURATION_BUCKET), "Conversation lifecycle metadata; no message content"),
        FeatureContract(RoleId("sse.dispatch"), setOf(SafeEventField.EVENT_KIND), setOf(SafeEventField.STEP_STATE, SafeEventField.ERROR_KIND, SafeEventField.DURATION_BUCKET), "Stream event metadata; no delta payload")
    )
}
