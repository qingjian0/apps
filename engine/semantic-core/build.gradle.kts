plugins {
    kotlin("jvm") version "2.2.20"
}

repositories { mavenCentral() }

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.9.0")
    testImplementation(kotlin("test-junit5"))
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:5.12.2")
}

tasks.test { useJUnitPlatform() }

tasks.register<JavaExec>("ingestAudit") {
    group = "verification"
    description = "Map real APK audit JSONL indexes into semantic candidates"
    classpath = sourceSets["main"].runtimeClasspath
    mainClass.set("dsh.semantic.StaticAuditCliKt")
}
kotlin { jvmToolchain(21) }
