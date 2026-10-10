plugins {
    // Loaded once here so that each module's classloader does not load them again.
    alias(libs.plugins.kotlinMultiplatform) apply false
    alias(libs.plugins.kotlinSerialization) apply false
    alias(libs.plugins.composeMultiplatform) apply false
    alias(libs.plugins.composeCompiler) apply false
    alias(libs.plugins.skie) apply false
}
