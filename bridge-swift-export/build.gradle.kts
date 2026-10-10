// Arm B3: the same shared module through Kotlin's Swift export (Alpha), configured as its
// documentation's starting point does; Xcode runs `embedSwiftExportForXcode` instead of
// `embedAndSignAppleFrameworkForXcode`.
plugins {
    alias(libs.plugins.kotlinMultiplatform)
}

kotlin {
    iosArm64()
    iosSimulatorArm64()

    swiftExport {
        moduleName = "Shared"
        flattenPackage = "bench.bridge"
        export(project(":shared")) {
            moduleName = "SharedLogic"
            flattenPackage = "bench.shared"
        }
    }

    sourceSets {
        commonMain.dependencies {
            api(project(":shared"))
        }
    }
}
