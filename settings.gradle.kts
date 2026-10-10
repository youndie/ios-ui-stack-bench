rootProject.name = "ios-ui-stack-bench"

pluginManagement {
    repositories {
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositories {
        mavenCentral()
        google {
            mavenContent {
                includeGroupAndSubgroups("androidx")
                includeGroupAndSubgroups("com.google")
            }
        }
    }
}

// The shared Kotlin module, compiled once, and the four ways it reaches an app: one framework module
// per bridge arm (B1 Objective-C export, B2 SKIE, B3 Swift export) and the Compose UI of arm C.
include(":shared")
include(":bridge-objc")
include(":bridge-skie")
include(":bridge-swift-export")
include(":compose-ui")
