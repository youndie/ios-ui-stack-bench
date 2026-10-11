import Foundation
import QuartzCore
import UIKit
import os

/// The study's instrumentation, compiled into every arm from this one source — not a package, so
/// that no arm pays a module boundary another does not (research D2).
///
/// What it records, into one NDJSON file per launch under `Documents/bench/`, every line carrying
/// `t`, seconds on the `CACurrentMediaTime` clock (the clock `CADisplayLink` timestamps use):
///
/// - `header` — bundle id, `hw.machine`, iOS version, the process start on the same clock, the
///   screen's maximum frame rate, the frame logger's requested range, thermal state, Low Power Mode,
///   battery level (0-1, or -1 where the system does not know it - a simulator) - what the session
///   runner's preflight reads (B-25);
/// - `mark` — the phase markers, also emitted as `os_signpost` events for `xctrace`: `launch` (this
///   object started, the earliest Swift code of the app), `firstFrame` (the first display-link
///   tick), `listPopulated` (the first display-link tick after the first row appeared — a row
///   "appears" before the frame that shows it is drawn, so the marker waits for that frame, and the
///   two markers are quantised to frames the same way in every arm), and named scenario phases:
///   `scenario:<name>` at launch when the harness passes `-benchScenario <name>`, `query` on every
///   change of the search query, `detailAppeared` / `detailDisappeared` around the detail screen;
/// - `frame` — every `CADisplayLink` callback: `t` its timestamp, `tt` its target timestamp;
/// - `footprint` — `phys_footprint` from `task_vm_info`, every 250 ms, from a utility queue;
/// - `scroll` — each transition of the list between scrolling and resting: `phase` `begin` or
///   `end`, the content offset in points where the UI knows it exactly (`offset`, SwiftUI), or the
///   first visible item and its offset in pixels (`first`, `firstOffsetPx`, Compose), and the last
///   visible item where the UI knows it (`last`). Only the transitions are logged — nothing runs per
///   frame — so the probe costs every arm two callbacks per fling;
/// - `stall` — each injected main-thread stall and its length;
/// - `thermal` — every change of `ProcessInfo.thermalState`.
///
/// Launch arguments: `-benchStallMs <n>` arms the stall injector (a stall of `n` ms on the main
/// thread every `-benchStallEverySec <s>` seconds, 1 by default); `0` runs the same path and blocks
/// for nothing — the control that must not register (B-06). Two more positive controls of RQ0 (B-28),
/// absent from every measured run: `-benchDelayListMs <n>` holds the main thread for n ms when the
/// first row appears, just before the frame that marks `listPopulated`, so launch-to-list grows by n;
/// `-benchAllocateMB <n>` allocates n MiB at launch and writes every page, so `phys_footprint` grows
/// by about n MiB and stays there.
final class Bench {
    static let shared = Bench()

    enum Marker: String { case launch, firstFrame, listPopulated }

    private let signposter = OSSignposter(subsystem: "io.github.youndie.iosbench", category: .pointsOfInterest)
    private let queue = DispatchQueue(label: "io.github.youndie.iosbench.log", qos: .utility)
    private var handle: FileHandle?
    private var started = false
    private var link: CADisplayLink?
    private var sawFirstFrame = false
    private var listPending = false
    private var reported = Set<String>()
    private var frames: [(Double, Double)] = []
    private var flushTimer: Timer?
    private var sampler: DispatchSourceTimer?
    private var stallTimer: Timer?
    private var delayedList = false
    private var ballast: UnsafeMutableRawPointer?

    /// Starts everything; call once, on the main thread, from the app's initialiser.
    func start() {
        dispatchPrecondition(condition: .onQueue(.main))
        guard !started else { return }
        started = true
        openLog()
        writeHeader()
        mark(.launch)
        if let scenario = Self.argument("benchScenario") { phase("scenario:\(scenario)") }
        startFrameLogger()
        startSampler()
        startStallInjector()
        allocateBallast()
        NotificationCenter.default.addObserver(forName: ProcessInfo.thermalStateDidChangeNotification, object: nil, queue: nil) { [weak self] _ in
            self?.write(["k": "thermal", "t": CACurrentMediaTime(), "state": Self.thermalName()])
        }
    }

    /// The first row is on its way to the screen; `listPopulated` is marked on the next frame.
    func rowAppeared() {
        dispatchPrecondition(condition: .onQueue(.main))
        if !delayedList, let ms = Self.argument("benchDelayListMs").flatMap(Int.init), ms > 0 {
            delayedList = true
            usleep(useconds_t(ms * 1000))
            write(["k": "control", "t": CACurrentMediaTime(), "delayListMs": ms])
        }
        listPending = true
    }

    /// A phase marker, once per launch for the three fixed ones.
    func mark(_ marker: Marker) {
        let now = CACurrentMediaTime()
        guard reported.insert(marker.rawValue).inserted else { return }
        switch marker {
        case .launch: signposter.emitEvent("launch")
        case .firstFrame: signposter.emitEvent("firstFrame")
        case .listPopulated: signposter.emitEvent("listPopulated")
        }
        write(["k": "mark", "t": now, "name": marker.rawValue])
    }

    /// A marker by name, as the Compose side of arm C reports it; an unknown name is a scenario phase.
    func mark(named name: String) {
        if name == "rowAppeared" { rowAppeared() } else if let marker = Marker(rawValue: name) { mark(marker) } else { phase(name) }
    }

    /// A scenario phase marker; may repeat.
    func phase(_ name: String) {
        let now = CACurrentMediaTime()
        signposter.emitEvent("phase", "\(name, privacy: .public)")
        write(["k": "mark", "t": now, "name": name])
    }

    /// The list started (`begin`) or stopped (`end`) scrolling. Fields the UI cannot know exactly are
    /// left out rather than estimated; the reader derives them from the row height.
    func scroll(_ phase: String, offset: Double? = nil, first: Int? = nil, firstOffsetPx: Double? = nil, last: Int? = nil) {
        let now = CACurrentMediaTime()
        if phase == "begin" { signposter.emitEvent("scrollBegin") } else { signposter.emitEvent("scrollEnd") }
        var line: [String: Any] = ["k": "scroll", "t": now, "phase": phase]
        if let offset { line["offset"] = offset }
        if let first { line["first"] = first }
        if let firstOffsetPx { line["firstOffsetPx"] = firstOffsetPx }
        if let last { line["last"] = last }
        write(line)
    }

    // MARK: - log

    private func openLog() {
        let fm = FileManager.default
        let dir = fm.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent("bench", isDirectory: true)
        try? fm.createDirectory(at: dir, withIntermediateDirectories: true)
        let url = dir.appendingPathComponent("\(Int(Date().timeIntervalSince1970))-\(getpid()).ndjson")
        fm.createFile(atPath: url.path, contents: nil)
        handle = try? FileHandle(forWritingTo: url)
    }

    private func write(_ object: [String: Any]) {
        queue.async { [handle] in
            guard let handle, let data = try? JSONSerialization.data(withJSONObject: object, options: [.sortedKeys]) else { return }
            handle.write(data)
            handle.write(Data([0x0A]))
        }
    }

    private func writeHeader() {
        UIDevice.current.isBatteryMonitoringEnabled = true
        let now = CACurrentMediaTime()
        let wallNow = Date().timeIntervalSince1970
        write([
            "k": "header",
            "t": now,
            "bundle": Bundle.main.bundleIdentifier ?? "",
            "machine": Self.sysctlString("hw.machine"),
            "os": UIDevice.current.systemVersion,
            "processStart": now - (wallNow - Self.processStartEpoch()),
            "maxFps": UIScreen.main.maximumFramesPerSecond,
            "requestedFps": UIScreen.main.maximumFramesPerSecond,
            "thermal": Self.thermalName(),
            "lowPower": ProcessInfo.processInfo.isLowPowerModeEnabled,
            "battery": Double(UIDevice.current.batteryLevel),
            "stallMs": Self.argument("benchStallMs").flatMap(Int.init) ?? -1,
        ])
    }

    // MARK: - frames

    private func startFrameLogger() {
        let link = CADisplayLink(target: self, selector: #selector(tick(_:)))
        let fps = Float(UIScreen.main.maximumFramesPerSecond)
        link.preferredFrameRateRange = CAFrameRateRange(minimum: fps, maximum: fps, preferred: fps)
        link.add(to: .main, forMode: .common)
        self.link = link
        frames.reserveCapacity(512)
        flushTimer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in self?.flushFrames() }
        RunLoop.main.add(flushTimer!, forMode: .common)
    }

    @objc private func tick(_ link: CADisplayLink) {
        if !sawFirstFrame {
            sawFirstFrame = true
            mark(.firstFrame)
        } else if listPending {
            listPending = false
            mark(.listPopulated)
        }
        frames.append((link.timestamp, link.targetTimestamp))
    }

    private func flushFrames() {
        guard !frames.isEmpty else { return }
        let batch = frames
        frames.removeAll(keepingCapacity: true)
        queue.async { [handle] in
            guard let handle else { return }
            var text = ""
            for (t, tt) in batch { text += "{\"k\":\"frame\",\"t\":\(t),\"tt\":\(tt)}\n" }
            handle.write(Data(text.utf8))
        }
    }

    // MARK: - memory

    private func startSampler() {
        let timer = DispatchSource.makeTimerSource(queue: queue)
        timer.schedule(deadline: .now(), repeating: .milliseconds(250), leeway: .milliseconds(5))
        timer.setEventHandler { [weak self] in
            self?.write(["k": "footprint", "t": CACurrentMediaTime(), "bytes": Self.physFootprint()])
        }
        timer.resume()
        sampler = timer
    }

    static func physFootprint() -> UInt64 {
        var info = task_vm_info_data_t()
        var count = mach_msg_type_number_t(MemoryLayout<task_vm_info_data_t>.size / MemoryLayout<integer_t>.size)
        let result = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: Int(count)) {
                task_info(mach_task_self_, task_flavor_t(TASK_VM_INFO), $0, &count)
            }
        }
        return result == KERN_SUCCESS ? info.phys_footprint : 0
    }

    // MARK: - stall

    private func startStallInjector() {
        guard let ms = Self.argument("benchStallMs").flatMap(Int.init), ms >= 0 else { return }
        let every = Self.argument("benchStallEverySec").flatMap(Double.init) ?? 1
        let timer = Timer(timeInterval: every, repeats: true) { [weak self] _ in
            let begin = CACurrentMediaTime()
            if ms > 0 { usleep(useconds_t(ms * 1000)) }
            self?.write(["k": "stall", "t": begin, "ms": ms, "actual": (CACurrentMediaTime() - begin) * 1000])
        }
        RunLoop.main.add(timer, forMode: .common)
        stallTimer = timer
    }

    // MARK: - controls

    /// RQ0's memory control: n MiB, every 4 KiB of it written so the pages are dirty and count in
    /// `phys_footprint`; held until the process ends.
    private func allocateBallast() {
        guard let mib = Self.argument("benchAllocateMB").flatMap(Int.init), mib > 0 else { return }
        let bytes = mib << 20
        let memory = UnsafeMutableRawPointer.allocate(byteCount: bytes, alignment: 16_384)
        for offset in stride(from: 0, to: bytes, by: 4096) {
            memory.storeBytes(of: UInt8(truncatingIfNeeded: offset >> 12) | 1, toByteOffset: offset, as: UInt8.self)
        }
        ballast = memory
        write(["k": "control", "t": CACurrentMediaTime(), "allocatedMiB": mib])
    }

    // MARK: - system

    /// A launch argument `-<name> <value>`, as the argument domain of `UserDefaults` holds it: a string.
    private static func argument(_ name: String) -> String? {
        UserDefaults.standard.string(forKey: name)
    }

    private static func sysctlString(_ name: String) -> String {
        var size = 0
        sysctlbyname(name, nil, &size, nil, 0)
        var buffer = [CChar](repeating: 0, count: size)
        sysctlbyname(name, &buffer, &size, nil, 0)
        return String(cString: buffer)
    }

    private static func processStartEpoch() -> Double {
        var info = kinfo_proc()
        var size = MemoryLayout<kinfo_proc>.stride
        var mib: [Int32] = [CTL_KERN, KERN_PROC, KERN_PROC_PID, getpid()]
        guard sysctl(&mib, 4, &info, &size, nil, 0) == 0 else { return 0 }
        let start = info.kp_proc.p_un.__p_starttime
        return Double(start.tv_sec) + Double(start.tv_usec) / 1_000_000
    }

    private static func thermalName() -> String {
        switch ProcessInfo.processInfo.thermalState {
        case .nominal: "nominal"
        case .fair: "fair"
        case .serious: "serious"
        case .critical: "critical"
        @unknown default: "unknown"
        }
    }
}
