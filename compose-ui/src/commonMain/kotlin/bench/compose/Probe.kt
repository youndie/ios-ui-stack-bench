package bench.compose

/**
 * How the Compose side reports its phase markers. The host implements it in Swift and forwards each
 * event to the same instrumentation every arm uses, so C's "list populated" is the same signpost, in
 * the same log, as A's.
 */
interface Probe {
    fun mark(event: String)

    /**
     * The list started (`begin`) or stopped (`end`) scrolling, with the first and last visible item
     * and the first one's scroll offset in pixels — what a `LazyListState` knows exactly.
     */
    fun scroll(phase: String, first: Int, firstOffsetPx: Int, last: Int)
}
