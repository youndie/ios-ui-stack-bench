import Foundation

// Arm A's filter (SwiftCatalog) against the shared test vector, on the real fixture: the Swift half of
// what FilterVectorTest checks in Kotlin. Built for macOS from A's own source by
// scripts/check-filter-vectors.sh; exits non-zero on the first query whose ids differ.

struct Vectors: Decodable {
    struct Vector: Decodable { let query: String; let ids: [Int] }
    let vectors: [Vector]
}

let repo = CommandLine.arguments[1]
let fixture = try String(contentsOfFile: "\(repo)/apps/common/Fixture/items.json", encoding: .utf8)
let vectors = try JSONDecoder().decode(Vectors.self, from: Data(contentsOf: URL(fileURLWithPath: "\(repo)/fixtures/filter-vectors.json"))).vectors

let catalog = SwiftCatalog(json: fixture)
let total = catalog.visible.count
guard total == 2000 else { fatalError("expected 2000 items, got \(total)") }
for vector in vectors {
    catalog.filter(vector.query)
    let ids = catalog.visible.map(\.id)
    if ids != vector.ids {
        print("query '\(vector.query)': expected \(vector.ids.count) ids, got \(ids.count)")
        exit(1)
    }
}
print("arm A's filter matches all \(vectors.count) vectors on the \(total)-item fixture")
