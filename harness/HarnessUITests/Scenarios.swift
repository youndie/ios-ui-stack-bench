import XCTest

/// The study's scenarios, S1–S4 of the brief, driving one arm at a time by bundle id.
///
/// Which arm, and its extra launch arguments, come from the environment, set by `harness/run.sh`
/// through `TEST_RUNNER_`-prefixed variables: `BENCH_BUNDLE` (e.g. `io.github.youndie.iosbench.c`)
/// and `BENCH_LAUNCH_ARGS` (e.g. `-benchStallMs 50`). Every launch also passes
/// `-benchScenario <name>`, which the app records as a phase marker: the timing is the app's own
/// log, never this runner's clock, which belongs to another process (B-13).
///
/// The elements are found by the fixture's text, which is the same in every arm: the first item's
/// title and its first paragraph. Nothing here knows which UI stack it is driving, apart from where
/// the search field and the back button live.
final class Scenarios: XCTestCase {
    /// The first item of the fixture, its title on the list and its first paragraph on the detail.
    private let firstTitle = "Lunar island 1"
    private let firstParagraph = "No look use she some than."
    /// The S3 query, typed one key at a time (fixtures/generate.py, S3_QUERY).
    private let query = "amber harbor"

    private var environment: [String: String] { ProcessInfo.processInfo.environment }

    override func setUp() {
        continueAfterFailure = false
    }

    /// Every scenario ends with the arm terminated, so nothing after the run can append to its log:
    /// a C run left alive once logged two push/pop cycles a quarter of an hour after its test had
    /// passed, and the reader rightly called the run invalid (B-14).
    override func tearDown() {
        if let bundle = environment["BENCH_BUNDLE"], !bundle.isEmpty {
            XCUIApplication(bundleIdentifier: bundle).terminate()
        }
        super.tearDown()
    }

    // MARK: - scenarios

    /// S1: terminate, wait 10 s, launch, until the list is populated. One launch per invocation;
    /// the session runs it as many times as the protocol says.
    func testS1ColdStart() throws {
        let app = try arm()
        app.terminate()
        Thread.sleep(forTimeInterval: 10)
        launch(app, scenario: "S1")
    }

    /// S2: 20 flings down and 20 up at a fixed velocity, each left to settle before the next.
    ///
    /// The pause after each fling is fixed and longer than any arm's deceleration, because the runner
    /// cannot see the app settle: XCUITest waits for SwiftUI's animations to go idle, but not for
    /// Compose's, so with a short pause C's flings ran into each other and the list never stopped
    /// (found on the simulator, B-13). Every fling must log its own `scroll` begin and end.
    private let flingPause: TimeInterval = 5

    func testS2Fling() throws {
        let app = try arm()
        launch(app, scenario: "S2")
        let window = app.windows.firstMatch
        let high = window.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.3))
        let low = window.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.75))
        for (from, to) in [(low, high), (high, low)] {
            for _ in 0..<20 {
                from.press(forDuration: 0.05, thenDragTo: to, withVelocity: XCUIGestureVelocity(2500), thenHoldForDuration: 0)
                Thread.sleep(forTimeInterval: flingPause)
            }
        }
    }

    /// S3: type the query one key at a time with fixed delays, then delete it the same way.
    func testS3Filter() throws {
        let app = try arm()
        launch(app, scenario: "S3")
        let field = searchField(app)
        field.tap()
        Thread.sleep(forTimeInterval: 1)
        for character in query {
            field.typeText(String(character))
            Thread.sleep(forTimeInterval: 0.3)
        }
        for _ in query {
            field.typeText(XCUIKeyboardKey.delete.rawValue)
            Thread.sleep(forTimeInterval: 0.3)
        }
        // The field is empty again. Not "the first item is back": Compose's keyed LazyColumn keeps the
        // row that was on top when the list grows again, where SwiftUI's List does not (B-13).
        // An empty field reports either nothing or its placeholder, depending on the stack.
        let typed = (field.value as? String) ?? ""
        XCTAssertTrue(typed.isEmpty || typed == "Search", "the query was not cleared: '\(typed)'")
    }

    /// S4: 50 push/pop cycles on the detail screen of the first item.
    func testS4NavigationChurn() throws {
        let app = try arm()
        launch(app, scenario: "S4")
        for cycle in 1...50 {
            app.staticTexts[firstTitle].firstMatch.tap()
            XCTAssertTrue(app.staticTexts[firstParagraph].waitForExistence(timeout: 10), "cycle \(cycle): no detail")
            back(app)
            XCTAssertTrue(app.staticTexts[firstTitle].firstMatch.waitForExistence(timeout: 10), "cycle \(cycle): no list")
            Thread.sleep(forTimeInterval: 0.5)
        }
    }

    // MARK: - the arm

    private func arm() throws -> XCUIApplication {
        guard let bundle = environment["BENCH_BUNDLE"], !bundle.isEmpty else {
            throw XCTSkip("BENCH_BUNDLE is not set; run the scenarios through harness/run.sh")
        }
        return XCUIApplication(bundleIdentifier: bundle)
    }

    private func launch(_ app: XCUIApplication, scenario: String) {
        let extra = (environment["BENCH_LAUNCH_ARGS"] ?? "").split(separator: " ").map(String.init)
        app.launchArguments = ["-benchScenario", scenario] + extra
        app.launch()
        XCTAssertTrue(app.staticTexts[firstTitle].firstMatch.waitForExistence(timeout: 30), "the list never showed the first item")
    }

    /// SwiftUI's `.searchable` field, or the Compose text field — which Compose Multiplatform exposes
    /// to accessibility as a text view, not a text field (its tree, printed on the simulator, B-13).
    private func searchField(_ app: XCUIApplication) -> XCUIElement {
        let search = app.searchFields.firstMatch
        return search.exists ? search : app.textViews.firstMatch
    }

    /// The Compose detail screen's Back button, or the navigation bar's back button in SwiftUI.
    private func back(_ app: XCUIApplication) {
        let compose = app.buttons["Back"]
        if compose.exists { compose.tap() } else { app.navigationBars.buttons.element(boundBy: 0).tap() }
    }
}
