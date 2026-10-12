package bench.compose

import androidx.compose.ui.window.ComposeUIViewController
import bench.shared.Catalog
import platform.UIKit.UIViewController

/**
 * The one full-screen controller arm C's SwiftUI host shows. [json] is the bundled fixture, read by the
 * host; [autoScrolls] and [autoNavigates] are the host's `-benchAutoScroll` and `-benchAutoNavigate`
 * (A1.7, A2.2), 0 unless a self-driven scenario asks for them.
 */
@Suppress("FunctionName")
fun MainViewController(json: String, probe: Probe, autoScrolls: Int, autoNavigates: Int): UIViewController {
    val catalog = Catalog().apply { load(json) }
    return ComposeUIViewController { App(catalog, probe, autoScrolls, autoNavigates) }
}
