package dsh.semantic

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class StaticAuditJsonReaderTest {
    @Test fun consumesActualAuditJsonlSchemaAndMapsRole() {
        val host = HostFingerprint("com.deepseek.chat", 301, "future", "cert", "dex-future", "loader")
        val line = """{"class":"Lx/y;","name":"m_91","descriptor":"(Ljava/lang/String;I)V","access":"public static","invokes":["Lkotlinx/coroutines/flow/Flow;->emit(Ljava/lang/Object;)V"],"opcode_count":33,"strings":["custom_instructions","prompt_template"],"roles":[{"role":"prompt_pipeline","anchors":["custom_instructions","prompt_template"]}]}"""
        val candidate = StaticAuditJsonReader().readLine(line, host).single()
        assertEquals("prompt.compose", candidate.role.value)
        assertEquals(listOf("Ljava/lang/String;", "I"), candidate.method.parameterTypes)
        assertEquals("V", candidate.method.returnType)
        assertEquals(true, candidate.method.isStatic)
        assertTrue(SemanticResolver().resolve(host, RolePolicy(candidate.role), listOf(candidate)).accepted)
    }

    @Test fun malformedDescriptorProducesNoCandidate() {
        val host = HostFingerprint("com.deepseek.chat", 301, "future", "cert", "dex-future", "loader")
        val line = """{"class":"Lx/y;","name":"m","descriptor":"not-a-method","strings":["prompt_template"],"roles":[{"role":"prompt_pipeline","anchors":["prompt_template"]}]}"""
        assertTrue(StaticAuditJsonReader().readLine(line, host).isEmpty())
    }
}
