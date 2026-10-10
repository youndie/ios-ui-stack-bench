package bench.shared

import kotlin.test.Test
import kotlin.test.assertEquals

class CatalogTest {
    private val json = """
        [
          {"id": 1, "title": "Alpha", "subtitle": "s", "detail": "d", "badge": 3, "thumbnail": 0},
          {"id": 2, "title": "beta", "subtitle": "s", "detail": "d", "badge": 0, "thumbnail": 1},
          {"id": 3, "title": "Alphabet", "subtitle": "s", "detail": "d", "badge": 7, "thumbnail": 2}
        ]
    """.trimIndent()

    @Test
    fun loadShowsEveryItemInFixtureOrder() {
        val catalog = Catalog()
        catalog.load(json)
        assertEquals(listOf(1, 2, 3), catalog.visible.value.map { it.id })
        assertEquals(3, catalog.total)
    }

    @Test
    fun filterIsCaseInsensitiveSubstringOnTheTitle() {
        val catalog = Catalog()
        catalog.load(json)
        catalog.filter("ALPHA")
        assertEquals(listOf(1, 3), catalog.visible.value.map { it.id })
        catalog.filter("  ")
        assertEquals(listOf(1, 2, 3), catalog.visible.value.map { it.id })
    }
}
