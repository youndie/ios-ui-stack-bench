package bench.compose

import androidx.compose.ui.window.ComposeUIViewController
import bench.shared.Catalog
import platform.UIKit.UIViewController

/** The one full-screen controller arm C's SwiftUI host shows. [json] is the bundled fixture, read by the host. */
@Suppress("FunctionName")
fun MainViewController(json: String, probe: Probe): UIViewController {
    val catalog = Catalog().apply { load(json) }
    return ComposeUIViewController { App(catalog, probe) }
}
