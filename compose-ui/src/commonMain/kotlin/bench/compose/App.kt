package bench.compose

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.WindowInsetsSides
import androidx.compose.foundation.layout.asPaddingValues
import androidx.compose.foundation.layout.only
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshotFlow
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.TextStyle
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import bench.compose.resources.Res
import bench.compose.resources.allDrawableResources
import bench.shared.Catalog
import bench.shared.Item
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.drop
import kotlinx.coroutines.launch
import org.jetbrains.compose.resources.painterResource

/**
 * The whole of arm C's UI, with the stack's idiomatic defaults: Material 3, a `LazyColumn`,
 * JetBrains' navigation-compose with its default transitions, and the thumbnails as Compose
 * resources through `painterResource`.
 */
@Composable
fun App(catalog: Catalog, probe: Probe, autoScrolls: Int = 0) {
    MaterialTheme {
        Surface(Modifier.fillMaxSize()) {
            val items by catalog.visible.collectAsState()
            val navController = rememberNavController()
            // The item the detail screen shows; a route argument would be parsed back into the same id.
            var selected by remember { mutableStateOf<Item?>(null) }
            // Top and sides inside the safe area; the bottom is the list's, which scrolls under the home
            // indicator as a UIKit/SwiftUI list does (B-29).
            Box(Modifier.fillMaxSize().windowInsetsPadding(WindowInsets.safeDrawing.only(WindowInsetsSides.Top + WindowInsetsSides.Horizontal))) {
                NavHost(navController, startDestination = "list") {
                    composable("list") {
                        ListScreen(items, catalog::filter, onOpen = { selected = it; navController.navigate("detail") }, probe, autoScrolls)
                    }
                    composable("detail") {
                        selected?.let { DetailScreen(it, onBack = { navController.popBackStack() }, probe) }
                    }
                }
            }
        }
    }
}

@Composable
private fun ListScreen(items: List<Item>, onQuery: (String) -> Unit, onOpen: (Item) -> Unit, probe: Probe, autoScrolls: Int) {
    var query by rememberSaveable { mutableStateOf("") }
    Column(Modifier.fillMaxSize()) {
        // iOS's large title size, so the list starts where the SwiftUI arms' list starts (B-29). On the
        // iPhone XS (iOS 18, the study's device since A1.7) SwiftUI puts the search field under the
        // title and the first row 146 points below the status bar; 46 dp above the title bring C's first
        // row there, with Material's 56 dp field kept (B-11).
        Text("Items", style = TextStyle(fontSize = 34.sp, fontWeight = FontWeight.Bold), modifier = Modifier.padding(start = 16.dp, end = 16.dp, top = 46.dp))
        OutlinedTextField(
            value = query,
            onValueChange = { query = it; probe.mark("query"); onQuery(it) },
            placeholder = { Text("Search") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth().padding(start = 16.dp, end = 16.dp, top = 4.dp, bottom = 4.dp),
        )
        val listState = rememberLazyListState()
        // Logged on the transitions only (B-13): the S2 reader needs how far each fling went.
        LaunchedEffect(listState) {
            snapshotFlow { listState.isScrollInProgress }.drop(1).collect { scrolling ->
                probe.scroll(
                    if (scrolling) "begin" else "end",
                    listState.firstVisibleItemIndex,
                    listState.firstVisibleItemScrollOffset,
                    listState.layoutInfo.visibleItemsInfo.lastOrNull()?.index ?: -1,
                )
            }
        }
        // RQ0's Animation Hitches control (A1.7): the list scrolls itself, in the pattern the SwiftUI
        // arms use - 1 s after launch, every 1.5 s, a screen further down, then back up. Off in every
        // measured run.
        if (autoScrolls > 0) {
            LaunchedEffect(listState) {
                delay(1000)
                repeat(autoScrolls) { i ->
                    probe.mark("autoScroll")
                    // Bench.autoScrollTarget's formula: a screen further per step, down then back up.
                    launch { listState.animateScrollToItem(if (i < autoScrolls / 2) 8 * (i + 1) else 8 * (autoScrolls - i - 1)) }
                    delay(1500)
                }
            }
        }
        LazyColumn(Modifier.fillMaxSize(), state = listState, contentPadding = WindowInsets.safeDrawing.only(WindowInsetsSides.Bottom).asPaddingValues()) {
            items(items, key = { it.id }) { item ->
                // The first row composed is the first row on its way to the screen, as SwiftUI's
                // onAppear of the first row is in the other arms; the frame that shows it is marked.
                if (item.id == items.first().id) LaunchedEffect(Unit) { probe.mark("rowAppeared") }
                // The separator inside the row, inset to the text as a SwiftUI List separator is, so a
                // row's pitch is its height (B-29).
                Column(Modifier.clickable { onOpen(item) }) {
                    ItemRow(item)
                    HorizontalDivider(Modifier.padding(start = 76.dp))
                }
            }
        }
    }
}

/**
 * A row: a 48 dp thumbnail, the title, two lines of text, and a numeric badge.
 *
 * Laid out to the SwiftUI rows' geometry so the first screens can be compared (B-29, A1.4 I12): the
 * text sizes are iOS's own text styles in points - headline 17 semibold, subheadline 15, footnote 13,
 * caption 12 - at their natural line height, the lines 2 dp apart like the SwiftUI VStack, and the
 * vertical padding chosen so that a row is as tall as a SwiftUI List row. Material's components stay;
 * only these sizes depart from Material's defaults (docs/flags.md).
 */
@Composable
private fun ItemRow(item: Item, modifier: Modifier = Modifier) {
    Row(
        // SwiftUI's List row on the iPhone XS (iOS 18): 76.67 points, 11 above and below its content.
        // C's text block is 2.33 points shorter at the same type sizes (Skia's line heights), so the
        // padding takes the difference (B-11; 15/14 dp matched the iOS 27 simulator in B-29).
        modifier.fillMaxWidth().padding(start = 16.dp, end = 16.dp, top = 11.67.dp, bottom = 11.67.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Thumbnail(item.thumbnail, Modifier.size(48.dp).clip(RoundedCornerShape(8.dp)))
        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(item.title, style = RowText.title)
            Text(item.subtitle, style = RowText.subtitle, maxLines = 1, overflow = TextOverflow.Ellipsis)
            Text(item.detail, style = RowText.detail, color = MaterialTheme.colorScheme.onSurfaceVariant, maxLines = 1, overflow = TextOverflow.Ellipsis)
        }
        Text(
            "${item.badge}",
            style = RowText.badge,
            modifier = Modifier
                .clip(RoundedCornerShape(50))
                .background(MaterialTheme.colorScheme.primaryContainer)
                .padding(horizontal = 8.dp, vertical = 2.dp),
        )
    }
}

/** iOS's text styles at the default content size, in points, at their natural line height. */
private object RowText {
    val title = TextStyle(fontSize = 17.sp, fontWeight = FontWeight.SemiBold)
    val subtitle = TextStyle(fontSize = 15.sp)
    val detail = TextStyle(fontSize = 13.sp)
    val badge = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
}

/** The detail screen: a large image, the title, a square turning once every 2 s, the text blocks. */
@Composable
private fun DetailScreen(item: Item, onBack: () -> Unit, probe: Probe) {
    DisposableEffect(item.id) {
        probe.mark("detailAppeared")
        onDispose { probe.mark("detailDisappeared") }
    }
    val angle by rememberInfiniteTransition().animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(tween(2000, easing = LinearEasing), RepeatMode.Restart),
    )
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        TextButton(onClick = onBack) { Text("Back") }
        Thumbnail(item.thumbnail, Modifier.fillMaxWidth().height(240.dp).clip(RoundedCornerShape(12.dp)))
        Text(item.title, style = MaterialTheme.typography.headlineMedium)
        Box(Modifier.size(40.dp).rotate(angle).clip(RoundedCornerShape(6.dp)).background(MaterialTheme.colorScheme.primary))
        item.paragraphs.forEach { Text(it, style = MaterialTheme.typography.bodyLarge) }
    }
}

/** One of the 50 bundled thumbnails, `thumb-NN.png`, as a Compose resource, cropped to fill. */
@Composable
private fun Thumbnail(index: Int, modifier: Modifier) {
    val resource = Res.allDrawableResources.getValue("thumb_" + index.toString().padStart(2, '0'))
    Image(painterResource(resource), contentDescription = "Thumbnail", contentScale = ContentScale.Crop, modifier = modifier)
}
