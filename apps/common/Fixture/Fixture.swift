import Foundation

/// The bundled fixture every arm parses at launch: the same bytes in all five apps.
enum Fixture {
    static var json: String {
        guard let url = Bundle.main.url(forResource: "items", withExtension: "json"),
              let text = try? String(contentsOf: url, encoding: .utf8) else {
            fatalError("items.json is not in the bundle")
        }
        return text
    }
}
