import SwiftUI
import UIKit

/// The list and detail screens of arms A, B1, B2 and B3 — one source, compiled into each. The
/// stack's idiomatic defaults throughout: `NavigationStack`, a plain `List`, `.searchable`, and the
/// bundled PNGs through `UIImage(named:)`, which caches them by name as the system intends.
struct RootView: View {
    @Bindable var model: ListModel

    var body: some View {
        NavigationStack {
            List(model.items) { item in
                NavigationLink(value: item) {
                    RowView(item: item)
                }
                .onAppear {
                    if item.id == model.items.first?.id { Bench.shared.rowAppeared() }
                }
            }
            .listStyle(.plain)
            .onScrollPhaseChange { old, new, context in
                // Logged on the transitions only (B-13): the S2 reader needs how far each fling went.
                if old == .idle, new != .idle {
                    Bench.shared.scroll("begin", offset: context.geometry.contentOffset.y)
                } else if new == .idle, old != .idle {
                    Bench.shared.scroll("end", offset: context.geometry.contentOffset.y)
                }
            }
            .searchable(text: $model.query)
            .navigationTitle("Items")
            .navigationDestination(for: RowItem.self) { DetailView(item: $0) }
        }
    }
}

/// A row: a 48 pt thumbnail, the title, two lines of text, and a numeric badge.
struct RowView: View {
    let item: RowItem

    var body: some View {
        HStack(spacing: 12) {
            Thumbnail(index: item.thumbnail)
                .frame(width: 48, height: 48)
                .clipShape(RoundedRectangle(cornerRadius: 8))
            VStack(alignment: .leading, spacing: 2) {
                Text(item.title).font(.headline)
                Text(item.subtitle).font(.subheadline).lineLimit(1)
                Text(item.detail).font(.footnote).foregroundStyle(.secondary).lineLimit(1)
            }
            Spacer(minLength: 0)
            Text("\(item.badge)")
                .font(.caption.weight(.semibold).monospacedDigit())
                .padding(.horizontal, 8)
                .padding(.vertical, 2)
                .background(Capsule().fill(.tint.opacity(0.15)))
        }
    }
}

/// The detail screen: a large image, the title, a square that turns once every 2 s for as long as
/// the screen is shown, and the item's text blocks.
struct DetailView: View {
    let item: RowItem
    @State private var spinning = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                Thumbnail(index: item.thumbnail)
                    .frame(maxWidth: .infinity)
                    .frame(height: 240)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                Text(item.title).font(.title)
                RoundedRectangle(cornerRadius: 6)
                    .fill(.tint)
                    .frame(width: 40, height: 40)
                    .rotationEffect(.degrees(spinning ? 360 : 0))
                    .animation(.linear(duration: 2).repeatForever(autoreverses: false), value: spinning)
                    .onAppear { spinning = true }
                ForEach(Array(item.paragraphs.enumerated()), id: \.offset) { _, paragraph in
                    Text(paragraph).font(.body)
                }
            }
            .padding(16)
        }
        .navigationTitle(item.title)
        .navigationBarTitleDisplayMode(.inline)
        .onAppear { Bench.shared.phase("detailAppeared") }
        .onDisappear { Bench.shared.phase("detailDisappeared") }
    }
}

/// One of the 50 bundled thumbnails, `thumb-NN.png`, scaled to fill its frame.
struct Thumbnail: View {
    let index: Int

    var body: some View {
        Image(uiImage: UIImage(named: String(format: "thumb-%02d", index)) ?? UIImage())
            .resizable()
            .scaledToFill()
    }
}
