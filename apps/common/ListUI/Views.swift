import SwiftUI

/// The list and detail screens of arms A, B1, B2 and B3 — one source, compiled into each.
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
            .searchable(text: $model.query)
            .navigationTitle("Items")
            .navigationDestination(for: RowItem.self) { DetailView(item: $0) }
        }
    }
}

struct RowView: View {
    let item: RowItem

    var body: some View {
        HStack(spacing: 12) {
            RoundedRectangle(cornerRadius: 8)
                .fill(thumbnailColor(item.thumbnail))
                .frame(width: 48, height: 48)
            VStack(alignment: .leading, spacing: 2) {
                Text(item.title).font(.headline)
                Text(item.subtitle).font(.subheadline)
                Text(item.detail).font(.footnote)
            }
            Spacer(minLength: 0)
            Text("\(item.badge)").font(.callout)
        }
    }
}

struct DetailView: View {
    let item: RowItem
    @State private var spinning = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                RoundedRectangle(cornerRadius: 12)
                    .fill(thumbnailColor(item.thumbnail))
                    .frame(height: 240)
                Text(item.title).font(.title)
                Rectangle()
                    .fill(.gray)
                    .frame(width: 40, height: 40)
                    .rotationEffect(.degrees(spinning ? 360 : 0))
                    .animation(.linear(duration: 2).repeatForever(autoreverses: false), value: spinning)
                    .onAppear { spinning = true }
                Text(item.detail).font(.body)
            }
            .padding(16)
        }
    }
}

/// A placeholder for the bundled thumbnails of the full spec (B-07): a colour per thumbnail index,
/// the same formula as arm C's.
func thumbnailColor(_ index: Int) -> Color {
    Color(hue: Double((index * 37) % 360) / 360, saturation: 0.45, brightness: 0.85)
}
