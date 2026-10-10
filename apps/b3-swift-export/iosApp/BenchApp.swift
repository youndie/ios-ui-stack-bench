import SwiftUI
import SharedLogic

/// Arm B3: the shared Kotlin `Catalog` through Kotlin's Swift export, which hands Swift the
/// `StateFlow` as a typed `KotlinTypedStateFlow`; the adapter iterates it, as an `AsyncSequence`, into
/// the `ListModel` the shared SwiftUI views read.
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

/// The whole of B3's bridge.
final class CatalogAdapter {
    private let catalog = Catalog()
    private var task: Task<Void, Never>?

    init(json: String, model: ListModel) {
        catalog.load(json: json)
        model.onQuery = { [catalog] query in catalog.filter(query: query) }
        task = Task { @MainActor [catalog] in
            do {
                for try await items in catalog.visible.asAsyncSequence() {
                    model.items = items.map {
                        RowItem(id: Int($0.id), title: $0.title, subtitle: $0.subtitle, detail: $0.detail, paragraphs: $0.paragraphs, badge: Int($0.badge), thumbnail: Int($0.thumbnail))
                    }
                }
            } catch {
                fatalError("the visible items flow failed: \(error)")
            }
        }
    }
}
