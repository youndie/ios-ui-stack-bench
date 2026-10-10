package bench.shared

import kotlinx.serialization.Serializable

/**
 * One item of the fixture: a row of the list and its detail screen. Arm A decodes the same JSON
 * into its own Swift type.
 *
 * Deliberately not `@Serializable`: Swift export on stable Kotlin cannot compile
 * kotlinx-serialization's API once it is reachable from this module's public API (KT-87791, fixed in
 * 2.5.0), so the fixture is decoded into [ItemDto] and mapped — the same in every Kotlin arm
 * (research §1.11, D8).
 */
data class Item(
    val id: Int,
    val title: String,
    val subtitle: String,
    val detail: String,
    /** The detail screen's text blocks, about ten. */
    val paragraphs: List<String>,
    val badge: Int,
    /** Index of the bundled thumbnail, `thumb-NN.png`. */
    val thumbnail: Int,
)

@Serializable
internal class ItemDto(
    val id: Int,
    val title: String,
    val subtitle: String,
    val detail: String,
    val paragraphs: List<String>,
    val badge: Int,
    val thumbnail: Int,
) {
    fun toItem() = Item(id, title, subtitle, detail, paragraphs, badge, thumbnail)
}
