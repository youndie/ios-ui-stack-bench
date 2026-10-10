package bench.compose

/**
 * How the Compose side reports its phase markers. The host implements it in Swift and forwards each
 * event to the same instrumentation every arm uses, so C's "list populated" is the same signpost, in
 * the same log, as A's.
 */
interface Probe {
    fun mark(event: String)
}
