import SwiftUI

/// Arm A: the logic in Swift — `Codable`, `@Observable` — under the shared SwiftUI views.
@main
struct BenchApp: App {
    @State private var model = ListModel()
    private let catalog: SwiftCatalog

    init() {
        Bench.shared.start()
        catalog = SwiftCatalog(json: Fixture.json)
        let model = ListModel()
        model.items = catalog.visible
        model.onQuery = { [catalog, model] query in
            catalog.filter(query)
            model.items = catalog.visible
        }
        _model = State(initialValue: model)
    }

    var body: some Scene {
        WindowGroup {
            RootView(model: model)
        }
    }
}
