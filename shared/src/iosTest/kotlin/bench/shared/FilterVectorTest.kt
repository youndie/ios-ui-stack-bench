package bench.shared

import kotlinx.cinterop.ExperimentalForeignApi
import kotlinx.cinterop.toKString
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import platform.Foundation.NSString
import platform.Foundation.NSUTF8StringEncoding
import platform.Foundation.stringWithContentsOfFile
import platform.posix.getenv
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.fail

/**
 * The shared filter test vector (`fixtures/filter-vectors.json`) against the real fixture. Arm A's
 * Swift filter is held to the same file by `scripts/check-filter-vectors.sh`, so the two
 * implementations agree on every query the study types, not just on a handful written here.
 *
 * The files are read from the repository by path: Gradle passes it in `BENCH_REPO` (see
 * `shared/build.gradle.kts`), and a simulator test process can read the host's file system.
 */
@OptIn(ExperimentalForeignApi::class)
class FilterVectorTest {
    @Serializable
    private class Vector(val query: String, val ids: List<Int>)

    @Serializable
    private class Vectors(val filter: String, val vectors: List<Vector>)

    private fun read(relative: String): String {
        val repo = getenv("BENCH_REPO")?.toKString() ?: fail("BENCH_REPO is not set; run through Gradle")
        @Suppress("CAST_NEVER_SUCCEEDS")
        return NSString.stringWithContentsOfFile("$repo/$relative", NSUTF8StringEncoding, null) as String?
            ?: fail("cannot read $repo/$relative")
    }

    @Test
    fun everyVectorMatchesTheCatalogFilterOnTheRealFixture() {
        val catalog = Catalog()
        catalog.load(read("apps/common/Fixture/items.json"))
        assertEquals(2000, catalog.total)
        val vectors = Json.decodeFromString<Vectors>(read("fixtures/filter-vectors.json")).vectors
        assertEquals(18, vectors.size)
        for (vector in vectors) {
            catalog.filter(vector.query)
            assertEquals(vector.ids, catalog.visible.value.map { it.id }, "query '${vector.query}'")
        }
    }
}
