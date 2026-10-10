import SwiftUI
import Shared

/// Arm B1: the shared Kotlin `Catalog` through the plain Objective-C export, and a hand-written
/// adapter that collects its `StateFlow` into the `ListModel` the shared SwiftUI views read.
@main
struct BenchApp: App {
    @State private var model: ListModel
    private let adapter: CatalogAdapter

    init() {
        Bench.shared.start()
        let model = ListModel()
        adapter = CatalogAdapter(json: Fixture.json, model: model)
        _model = State(initialValue: model)
    }

    var body: some Scene {
        WindowGroup {
            RootView(model: model)
        }
    }
}

/// The whole of B1's bridge. Over the Objective-C export `StateFlow<List<Item>>` is a non-generic
/// protocol: its values arrive as `Any?` through a `FlowCollector`, and the suspend `collect` is a
/// completion-handler call that never completes while the app lives.
final class CatalogAdapter {
    private let catalog = Catalog()
    private let collector: Collector

    init(json: String, model: ListModel) {
        catalog.load(json: json)
        collector = Collector(model: model)
        model.onQuery = { [catalog] query in catalog.filter(query: query) }
        catalog.visible.collect(collector: collector) { _ in }
    }

    private final class Collector: Kotlinx_coroutines_coreFlowCollector {
        private let model: ListModel

        init(model: ListModel) { self.model = model }

        func emit(value: Any?, completionHandler: @escaping (Error?) -> Void) {
            let items = (value as? [Item]) ?? []
            model.items = items.map {
                RowItem(id: Int($0.id), title: $0.title, subtitle: $0.subtitle, detail: $0.detail, badge: Int($0.badge), thumbnail: Int($0.thumbnail))
            }
            completionHandler(nil)
        }
    }
}
