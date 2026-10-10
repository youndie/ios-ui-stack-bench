package bench.bridge

/**
 * A framework module with no source of its own links nothing (its link task is NO-SOURCE), so every
 * bridge module declares this one constant; the same in all three, so it costs them the same.
 */
const val BRIDGE: String = "swift-export"
