// Arm B1: the shared module through the plain Objective-C export, as the KMP wizard's native-UI
// template builds it — a static framework, nothing else configured.
plugins {
    alias(libs.plugins.kotlinMultiplatform)
}

kotlin {
    listOf(iosArm64(), iosSimulatorArm64()).forEach { target ->
        target.binaries.framework {
            baseName = "Shared"
            isStatic = true
            export(project(":shared"))
        }
    }

    sourceSets {
        commonMain.dependencies {
            api(project(":shared"))
        }
    }
}
