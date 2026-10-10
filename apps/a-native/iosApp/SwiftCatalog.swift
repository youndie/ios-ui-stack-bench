import Foundation

/// Arm A's counterpart of the shared Kotlin `Catalog`: the same fixture, the same filter semantics —
/// a case-insensitive substring of the title, a blank query showing everything.
final class SwiftCatalog {
    private struct Item: Decodable {
        let id: Int
        let title: String
        let subtitle: String
        let detail: String
        let paragraphs: [String]
        let badge: Int
        let thumbnail: Int
    }

    private let all: [RowItem]
    private(set) var visible: [RowItem]

    init(json: String) {
        do {
            let items = try JSONDecoder().decode([Item].self, from: Data(json.utf8))
            all = items.map {
                RowItem(id: $0.id, title: $0.title, subtitle: $0.subtitle, detail: $0.detail, paragraphs: $0.paragraphs, badge: $0.badge, thumbnail: $0.thumbnail)
            }
        } catch {
            fatalError("the fixture does not decode: \(error)")
        }
        visible = all
    }

    func filter(_ query: String) {
        let q = query.trimmingCharacters(in: .whitespacesAndNewlines)
        visible = q.isEmpty ? all : all.filter { $0.title.range(of: q, options: .caseInsensitive) != nil }
    }
}
