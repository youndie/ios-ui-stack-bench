// A stand-in for the app's instrumentation (apps/common/Instrumentation/Bench.swift), which needs
// UIKit: ListModel marks every query change, and this macOS check compiles ListModel but measures
// nothing.
final class Bench {
    static let shared = Bench()
    func phase(_ name: String) {}
}
