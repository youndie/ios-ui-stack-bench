package bench.shared

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.serialization.json.Json

/**
 * The logic every Kotlin arm shares: parse the fixture, hold the items, filter them on every
 * keystroke. Arm A implements the same contract in Swift; the filter semantics are the same in both,
 * and the shared test vector holds them to it (B-07).
 *
 * The state is a [StateFlow] on purpose: it is what the bridges differ in carrying to Swift — a
 * collector and casts over the Objective-C export (B1), an `AsyncSequence` through SKIE (B2) or
 * through Swift export (B3), a `collectAsState` in Compose (C).
 */
class Catalog {
    private var all: List<Item> = emptyList()
    private val _visible = MutableStateFlow<List<Item>>(emptyList())

    /** The items that match the current query, in fixture order. */
    val visible: StateFlow<List<Item>> = _visible.asStateFlow()

    /** Parses the fixture and shows every item. Throws on malformed JSON: a broken fixture is a build defect, not a state. */
    fun load(json: String) {
        all = format.decodeFromString<List<ItemDto>>(json).map { it.toItem() }
        _visible.value = all
    }

    /** Case-insensitive substring match on the title; a blank query shows everything. */
    fun filter(query: String) {
        val q = query.trim()
        _visible.value = if (q.isEmpty()) all else all.filter { it.title.contains(q, ignoreCase = true) }
    }

    /** The number of items loaded, whatever the filter. */
    val total: Int get() = all.size

    private companion object {
        val format = Json { ignoreUnknownKeys = false }
    }
}
