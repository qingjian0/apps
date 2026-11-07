package dsh.semantic

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import kotlinx.serialization.json.contentOrNull
import kotlinx.serialization.json.intOrNull
import java.io.BufferedReader
import java.io.FileInputStream
import java.io.InputStreamReader
import java.util.zip.GZIPInputStream

data class MethodGraphFacts(
    val identity: String,
    val fieldReads: Set<String>,
    val fieldWrites: Set<String>,
    val branchCount: Int,
    val labelCount: Int,
    val returnCount: Int,
    val throwCount: Int,
    val cfgBlockCount: Int = 0,
    val cfgEdgeCount: Int = 0,
    val cfgUnresolvedTargetCount: Int = 0,
    val cfgComplete: Boolean = false
)

data class ClassGraphFacts(val descriptor: String, val superDescriptor: String?, val interfaces: Set<String>)

/** Builds a bounded, metadata-only interprocedural and type graph from audit indexes. */
class StaticProgramGraph private constructor(
    private val callers: Map<String, Set<String>>,
    private val callees: Map<String, Set<String>>,
    private val readers: Map<String, Set<String>>,
    private val writers: Map<String, Set<String>>,
    private val methods: Map<String, MethodGraphFacts>,
    private val methodAnchors: Map<String, Set<String>>,
    private val methodCountsByOwner: Map<String, Int>,
    private val classes: Map<String, ClassGraphFacts>,
    private val subclasses: Map<String, Set<String>>,
    private val implementors: Map<String, Set<String>>
) {
    fun enrich(candidate: SemanticCandidate): SemanticCandidate {
        val id = candidate.method.stableIdentity
        val incoming = callers[id].orEmpty()
        val outgoing = callees[id].orEmpty()
        val facts = methods[id]
        val typeFacts = classes[candidate.method.ownerDescriptor]
        val ownerMethods = methodCountsByOwner[candidate.method.ownerDescriptor] ?: 0
        val frameworkCalls = outgoing.count { target -> FRAMEWORK_PREFIXES.any { target.startsWith(it) } }
        val linkedReads = facts?.fieldReads.orEmpty().sumOf { field -> writers[field].orEmpty().count { it != id } }
        val linkedWrites = facts?.fieldWrites.orEmpty().sumOf { field -> readers[field].orEmpty().count { it != id } }
        val rareAnchors = candidate.evidence.filter { it.family == EvidenceFamily.PROTOCOL_ANCHOR && it.weight >= 0.8 }.map { it.key }.toSet()
        val graphNeighbors = incoming + outgoing
        val neighborAnchorHits = graphNeighbors.flatMap { methodAnchors[it].orEmpty() }.filter { it in rareAnchors }.distinct()
        val fieldNeighbors = facts?.fieldReads.orEmpty().flatMap { writers[it].orEmpty() } + facts?.fieldWrites.orEmpty().flatMap { readers[it].orEmpty() }
        val fieldAnchorHits = fieldNeighbors.filter { it != id }.flatMap { methodAnchors[it].orEmpty() }.filter { it in rareAnchors }.distinct()
        val evidence = candidate.evidence.filterNot {
            it.family == EvidenceFamily.CALL_GRAPH ||
                it.family == EvidenceFamily.DATA_FLOW ||
                it.family == EvidenceFamily.CONTROL_FLOW ||
                it.family == EvidenceFamily.TYPE_SHAPE
        }.toMutableList()
        if (typeFacts != null) {
            val childCount = subclasses[typeFacts.descriptor].orEmpty().size
            val interfaceImplementorCount = typeFacts.interfaces.sumOf { implementors[it].orEmpty().size }
            val typeWeight = (0.48 + minOf(0.38, typeFacts.interfaces.size * 0.08) +
                if (childCount + interfaceImplementorCount > 0) 0.1 else 0.0).coerceAtMost(0.96)
            evidence += Evidence(
                EvidenceFamily.TYPE_SHAPE,
                "super=" + (typeFacts.superDescriptor ?: "none") + ";interfaces=" + typeFacts.interfaces.size +
                    ";subclasses=" + childCount + ";interface-implementors=" + interfaceImplementorCount +
                    ";declared-methods=" + ownerMethods,
                typeWeight
            )
        }
        if (incoming.isNotEmpty() || outgoing.isNotEmpty()) {
            val topology = "incoming=" + incoming.size + ";outgoing=" + outgoing.size + ";framework-outgoing=" + frameworkCalls +
                ";neighbor-rare-anchor-hits=" + neighborAnchorHits.size + ";anchors=" + neighborAnchorHits.sorted().joinToString(",")
            val weight = (0.42 + minOf(0.36, (incoming.size + outgoing.size).coerceAtMost(18) * 0.02) +
                (if (frameworkCalls > 0) 0.06 else 0.0) + minOf(0.14, neighborAnchorHits.size * 0.07)).coerceAtMost(0.98)
            evidence += Evidence(EvidenceFamily.CALL_GRAPH, topology, weight)
        }
        val linkedFields = linkedReads + linkedWrites
        if (linkedFields > 0) {
            evidence += Evidence(
                EvidenceFamily.DATA_FLOW,
                "cross-method-field-links=" + linkedFields + ";read-links=" + linkedReads + ";write-links=" + linkedWrites +
                    ";field-neighbor-rare-anchor-hits=" + fieldAnchorHits.size + ";anchors=" + fieldAnchorHits.sorted().joinToString(","),
                (0.52 + minOf(0.32, linkedFields.coerceAtMost(7) * 0.045) + minOf(0.11, fieldAnchorHits.size * 0.055)).coerceAtMost(0.95)
            )
        }
        // Only a resolved CFG contributes control-flow evidence. Legacy branch/label
        // counters are retained for diagnostics, never promoted into a graph claim.
        if (facts != null && facts.cfgComplete && facts.cfgBlockCount > 0) {
            val weight = (0.48 + minOf(0.30, facts.cfgEdgeCount.coerceAtMost(20) * 0.015) +
                minOf(0.12, facts.cfgBlockCount.coerceAtMost(12) * 0.01)).coerceAtMost(0.90)
            evidence += Evidence(
                EvidenceFamily.CONTROL_FLOW,
                "cfg=complete;blocks=" + facts.cfgBlockCount + ";edges=" + facts.cfgEdgeCount +
                    ";branches=" + facts.branchCount + ";returns=" + facts.returnCount + ";throws=" + facts.throwCount,
                weight
            )
        }
        return candidate.copy(evidence = evidence)
    }

    fun graphStats(): Map<String, Int> = mapOf(
        "methods" to methods.size,
        "callEdges" to callees.values.sumOf { it.size },
        "fieldReaderMethods" to readers.values.sumOf { it.size },
        "fieldWriterMethods" to writers.values.sumOf { it.size },
        "sharedFields" to readers.keys.intersect(writers.keys).size,
        "classes" to classes.size,
        "interfaceImplementors" to implementors.values.sumOf { it.size }
    )

    companion object {
        private val json = Json { ignoreUnknownKeys = true }
        private val FRAMEWORK_PREFIXES = listOf(
            "Lkotlin/", "Lkotlinx/", "Ljava/", "Landroid/", "Lio/ktor/",
            "Lokhttp3/", "Lretrofit2/", "Landroidx/"
        )

        fun load(methodsPath: String, edgesPath: String, classesPath: String): StaticProgramGraph {
            val callers = mutableMapOf<String, MutableSet<String>>()
            val callees = mutableMapOf<String, MutableSet<String>>()
            val readers = mutableMapOf<String, MutableSet<String>>()
            val writers = mutableMapOf<String, MutableSet<String>>()
            val methods = mutableMapOf<String, MethodGraphFacts>()
            val methodAnchors = mutableMapOf<String, MutableSet<String>>()
            val classes = mutableMapOf<String, ClassGraphFacts>()
            val subclasses = mutableMapOf<String, MutableSet<String>>()
            val implementors = mutableMapOf<String, MutableSet<String>>()

            BufferedReader(InputStreamReader(GZIPInputStream(FileInputStream(methodsPath)), Charsets.UTF_8)).use { input ->
                input.lineSequence().forEach { line ->
                    val obj = json.parseToJsonElement(line).jsonObject
                    val owner = obj["class"]?.jsonPrimitive?.contentOrNull ?: return@forEach
                    val name = obj["name"]?.jsonPrimitive?.contentOrNull ?: return@forEach
                    val descriptor = obj["descriptor"]?.jsonPrimitive?.contentOrNull ?: return@forEach
                    val id = owner + "->" + name + descriptor
                    obj["roles"]?.jsonArray?.forEach { role ->
                        role.jsonObject["anchors"]?.jsonArray?.mapNotNull { it.jsonPrimitive.contentOrNull }?.forEach { anchor ->
                            methodAnchors.getOrPut(id) { mutableSetOf() }.add(anchor)
                        }
                    }
                    val readFields = obj["field_reads"]?.jsonArray?.mapNotNull { it.jsonPrimitive.contentOrNull }?.toSet().orEmpty()
                    val writeFields = obj["field_writes"]?.jsonArray?.mapNotNull { it.jsonPrimitive.contentOrNull }?.toSet().orEmpty()
                    val cfg = obj["control_flow"]?.jsonObject
                    methods[id] = MethodGraphFacts(
                        id, readFields, writeFields,
                        cfg?.get("branch_count")?.jsonPrimitive?.intOrNull ?: 0,
                        cfg?.get("label_count")?.jsonPrimitive?.intOrNull ?: 0,
                        cfg?.get("return_count")?.jsonPrimitive?.intOrNull ?: 0,
                        cfg?.get("throw_count")?.jsonPrimitive?.intOrNull ?: 0,
                        cfg?.get("cfg")?.jsonObject?.get("block_count")?.jsonPrimitive?.intOrNull ?: 0,
                        cfg?.get("cfg")?.jsonObject?.get("edge_count")?.jsonPrimitive?.intOrNull ?: 0,
                        cfg?.get("cfg")?.jsonObject?.get("unresolved_target_count")?.jsonPrimitive?.intOrNull ?: 0,
                        cfg?.get("cfg")?.jsonObject?.get("complete")?.jsonPrimitive?.contentOrNull?.toBooleanStrictOrNull() ?: false
                    )
                    readFields.forEach { readers.getOrPut(it) { mutableSetOf() }.add(id) }
                    writeFields.forEach { writers.getOrPut(it) { mutableSetOf() }.add(id) }
                }
            }
            BufferedReader(InputStreamReader(GZIPInputStream(FileInputStream(classesPath)), Charsets.UTF_8)).use { input ->
                input.lineSequence().forEach { line ->
                    val obj = json.parseToJsonElement(line).jsonObject
                    val descriptor = obj["descriptor"]?.jsonPrimitive?.contentOrNull ?: return@forEach
                    val superDescriptor = obj["super"]?.jsonPrimitive?.contentOrNull
                    val interfaces = obj["interfaces"]?.jsonArray?.mapNotNull { it.jsonPrimitive.contentOrNull }?.toSet().orEmpty()
                    classes[descriptor] = ClassGraphFacts(descriptor, superDescriptor, interfaces)
                    if (superDescriptor != null) subclasses.getOrPut(superDescriptor) { mutableSetOf() }.add(descriptor)
                    interfaces.forEach { implementors.getOrPut(it) { mutableSetOf() }.add(descriptor) }
                }
            }
            BufferedReader(InputStreamReader(GZIPInputStream(FileInputStream(edgesPath)), Charsets.UTF_8)).use { input ->
                input.lineSequence().forEach { line ->
                    val obj = json.parseToJsonElement(line).jsonObject
                    val from = obj["from"]?.jsonPrimitive?.contentOrNull ?: return@forEach
                    val to = obj["to"]?.jsonPrimitive?.contentOrNull ?: return@forEach
                    callees.getOrPut(from) { mutableSetOf() }.add(to)
                    callers.getOrPut(to) { mutableSetOf() }.add(from)
                }
            }
            val methodCountsByOwner = methods.keys.groupingBy { it.substringBefore("->") }.eachCount()
            return StaticProgramGraph(callers, callees, readers, writers, methods, methodAnchors, methodCountsByOwner, classes, subclasses, implementors)
        }
    }
}
