package bench.shared

/** One row of the list, as the bundled fixture describes it. The Swift arm A decodes the same JSON. */
data class Item(
    val id: Int,
    val title: String,
    val subtitle: String,
    val detail: String,
    val badge: Int,
    val thumbnail: Int,
)

@kotlinx.serialization.Serializable
internal class ItemDto(val id: Int, val title: String, val subtitle: String, val detail: String, val badge: Int, val thumbnail: Int) {
    fun toItem() = Item(id, title, subtitle, detail, badge, thumbnail)
}
