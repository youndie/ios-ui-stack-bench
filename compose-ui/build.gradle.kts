// Arm C: the shared module under Compose Multiplatform, one full-screen ComposeUIViewController,
// framework and dependencies as the KMP wizard's shared-UI template builds them. The framework is
// the Objective-C export, as in B1, so B1 -> C changes the UI stack and nothing else.
plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.composeMultiplatform)
    alias(libs.plugins.composeCompiler)
}

kotlin {
    listOf(iosArm64(), iosSimulatorArm64()).forEach { target ->
        target.binaries.framework {
            baseName = "ComposeApp"
            isStatic = true
        }
    }

    sourceSets {
        commonMain.dependencies {
            implementation(project(":shared"))
            implementation(libs.compose.runtime)
            implementation(libs.compose.foundation)
            implementation(libs.compose.ui)
            implementation(libs.compose.material3)
            implementation(libs.compose.components.resources)
            implementation(libs.navigation.compose)
        }
    }
}

// The thumbnails every arm bundles, read from where the generator writes them (fixtures/generate.py)
// rather than copied: one set of bytes for five apps.
compose.resources {
    packageOfResClass = "bench.compose.resources"
    customDirectory(
        sourceSetName = "commonMain",
        directoryProvider = provider { rootProject.layout.projectDirectory.dir("apps/common/Thumbnails") },
    )
}
