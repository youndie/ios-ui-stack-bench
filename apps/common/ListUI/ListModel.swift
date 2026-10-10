import Observation

/// One row as the SwiftUI views draw it. Arm A fills it from Swift, the B arms from Kotlin.
struct RowItem: Identifiable, Hashable {
    let id: Int
    let title: String
    let subtitle: String
    let detail: String
    let paragraphs: [String]
    let badge: Int
    let thumbnail: Int
}

/// What the views of arms A, B1, B2 and B3 read: the visible rows, and the query the search field
/// writes. Where the rows come from — Swift, or Kotlin through one of three bridges — is each arm's
/// adapter, set through [onQuery] and by assigning [items]; the views are the same files everywhere.
@Observable
final class ListModel {
    var items: [RowItem] = []
    var query: String = "" {
        didSet {
            guard query != oldValue else { return }
            Bench.shared.phase("query")
            onQuery?(query)
        }
    }
    @ObservationIgnored var onQuery: ((String) -> Void)?
}
