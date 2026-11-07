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
kotlin { jvmToolchain(21) }
