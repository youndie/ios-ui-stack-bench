import SwiftUI
import Shared

/// Arm B2: the shared Kotlin `Catalog` through SKIE, which hands Swift the `StateFlow` as a typed
/// `AsyncSequence`; the adapter iterates it into the `ListModel` the shared SwiftUI views read.
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

/// The whole of B2's bridge.
final class CatalogAdapter {
    private let catalog = Catalog()
    private var task: Task<Void, Never>?

    init(json: String, model: ListModel) {
        catalog.load(json: json)
        model.onQuery = { [catalog] query in catalog.filter(query: query) }
        task = Task { @MainActor [catalog] in
            for await items in catalog.visible {
                model.items = items.map {
                    RowItem(id: Int($0.id), title: $0.title, subtitle: $0.subtitle, detail: $0.detail, badge: Int($0.badge), thumbnail: Int($0.thumbnail))
                }
            }
        }
    }
}
