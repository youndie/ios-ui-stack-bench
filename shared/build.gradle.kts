// The shared module of arms B1, B2, B3 and C: one compilation, one klib, whatever bridge consumes it.
// It produces no framework itself; each bridge module exports it into its own.
plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.kotlinSerialization)
}

kotlin {
    iosArm64()
    iosSimulatorArm64()

    sourceSets {
        commonMain.dependencies {
            api(libs.kotlinx.coroutines.core)
            implementation(libs.kotlinx.serialization.json)
        }
        commonTest.dependencies {
            implementation(libs.kotlin.test)
        }
    }
}

// The filter vector test reads the fixture from the repository (FilterVectorTest). A simulator test
// process gets its environment through simctl, which passes SIMCTL_CHILD_-prefixed variables on.
tasks.withType<org.jetbrains.kotlin.gradle.targets.native.tasks.KotlinNativeSimulatorTest>().configureEach {
    environment("SIMCTL_CHILD_BENCH_REPO", rootDir.absolutePath)
    environment("BENCH_REPO", rootDir.absolutePath)
}
tasks.withType<org.jetbrains.kotlin.gradle.targets.native.tasks.KotlinNativeHostTest>().configureEach {
    environment("BENCH_REPO", rootDir.absolutePath)
}
