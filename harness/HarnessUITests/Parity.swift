import XCTest

/// The first screen of an arm, as B-11's parity check needs it (B-27): geometry read from the
/// accessibility tree, and a screenshot kept as an attachment of the test result, which works the
/// same on a simulator and on a device. `harness/parity.sh` runs it and pulls both out.
///
/// Geometry lines are printed as `PARITY key=value`, in points:
///     rows        how many rows of the list are on screen, whole or in part
///     row_height  the first row's height
///     row_top     the first row's top edge, and list_bottom the last visible row's bottom edge -
///                 the region the pixel diff is taken over
///     thumb       the first row's thumbnail width x height, where the tree exposes it
///     title_h     the first row's title text height
///     scale       the screen's scale, to turn points into the screenshot's pixels
final class Parity: XCTestCase {
    private let firstTitle = "Lunar island 1"

    func testFirstScreen() throws {
        guard let bundle = ProcessInfo.processInfo.environment["BENCH_BUNDLE"], !bundle.isEmpty else {
            throw XCTSkip("BENCH_BUNDLE is not set; run through harness/parity.sh")
        }
        let app = XCUIApplication(bundleIdentifier: bundle)
        app.launchArguments = ["-benchScenario", "parity"]
        app.launch()
        let title = app.staticTexts[firstTitle].firstMatch
        XCTAssertTrue(title.waitForExistence(timeout: 30))
        Thread.sleep(forTimeInterval: 2)

        // A row is a SwiftUI cell, or the Compose button whose label starts with the title.
        let rows: [XCUIElement] = {
            let cells = app.cells.allElementsBoundByIndex.filter { $0.frame.height > 0 }
            if !cells.isEmpty { return cells }
            return app.buttons.allElementsBoundByIndex.filter { $0.label.hasPrefix(firstTitle) || $0.label.contains(", ") }
        }()
        let screen = app.windows.firstMatch.frame
        let visible = rows.filter { $0.frame.intersects(screen) && $0.frame.minY >= 0 }
        let first = visible.first { $0.staticTexts[firstTitle].exists || $0.label.hasPrefix(firstTitle) } ?? visible.first
        let thumb = first?.images.firstMatch
        print("PARITY rows=\(visible.count)")
        print("PARITY row_height=\(first?.frame.height ?? -1)")
        print("PARITY row_top=\(first?.frame.minY ?? -1)")
        print("PARITY list_bottom=\(min(visible.map(\.frame.maxY).max() ?? -1, screen.maxY))")
        print("PARITY thumb=\(thumb?.exists == true ? "\(thumb!.frame.width)x\(thumb!.frame.height)" : "not exposed")")
        print("PARITY title_h=\(title.frame.height)")
        // Diagnostics for matching a layout by hand, not read by any check: every text and image of the
        // first row, the search field and the navigation title, each with its frame in points.
        for e in (first?.staticTexts.allElementsBoundByIndex ?? []) + (first?.images.allElementsBoundByIndex ?? []) {
            print("PARITY_TREE row \(e.elementType.rawValue) '\(e.label.prefix(24))' \(e.frame)")
        }
        for e in app.searchFields.allElementsBoundByIndex + app.textFields.allElementsBoundByIndex + app.textViews.allElementsBoundByIndex {
            print("PARITY_TREE field \(e.elementType.rawValue) \(e.frame)")
        }
        for e in app.staticTexts.matching(identifier: "Items").allElementsBoundByIndex + app.navigationBars.allElementsBoundByIndex {
            print("PARITY_TREE title \(e.elementType.rawValue) '\(e.label)' \(e.frame)")
        }
        let screenshot = XCUIScreen.main.screenshot()
        print("PARITY scale=\(screenshot.image.scale)")

        let shot = XCTAttachment(screenshot: screenshot)
        shot.name = "first-screen"
        shot.lifetime = .keepAlways
        add(shot)
        app.terminate()
    }
}
