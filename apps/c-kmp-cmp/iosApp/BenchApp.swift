import SwiftUI
import UIKit
import ComposeApp

/// Arm C: one full-screen `ComposeUIViewController` hosted by SwiftUI, as the KMP wizard's
/// shared-UI template hosts it. Everything on screen is Compose; Swift only starts the
/// instrumentation and forwards Compose's phase markers to it.
@main
struct BenchApp: App {
    init() {
        Bench.shared.start()
    }

    var body: some Scene {
        WindowGroup {
            ComposeView().ignoresSafeArea()
        }
    }
}

struct ComposeView: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        MainViewControllerKt.MainViewController(json: Fixture.json, probe: BenchProbe(), autoScrolls: Int32(Bench.autoScrolls), autoNavigates: Int32(Bench.autoNavigates))
    }

    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}

/// Compose's markers, into the instrumentation every arm shares.
final class BenchProbe: Probe {
    func mark(event: String) {
        Bench.shared.mark(named: event)
    }

    func scroll(phase: String, first: Int32, firstOffsetPx: Int32, last: Int32) {
        Bench.shared.scroll(phase, first: Int(first), firstOffsetPx: Double(firstOffsetPx), last: last >= 0 ? Int(last) : nil)
    }
}
