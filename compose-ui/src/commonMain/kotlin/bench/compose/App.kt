package bench.compose

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import bench.shared.Catalog
import bench.shared.Item

/** The whole of arm C's UI: the list with its search field, and the detail screen pushed from a row. */
@Composable
fun App(catalog: Catalog, probe: Probe) {
    MaterialTheme {
        val items by catalog.visible.collectAsState()
        var selected by remember { mutableStateOf<Item?>(null) }
        Box(Modifier.fillMaxSize().safeDrawingPadding()) {
            when (val item = selected) {
                null -> ListScreen(items, catalog::filter, onOpen = { selected = it }, probe)
                else -> DetailScreen(item, onBack = { selected = null })
            }
        }
    }
}

@Composable
private fun ListScreen(items: List<Item>, onQuery: (String) -> Unit, onOpen: (Item) -> Unit, probe: Probe) {
    var query by remember { mutableStateOf("") }
    Column(Modifier.fillMaxSize()) {
        OutlinedTextField(
            value = query,
            onValueChange = { query = it; onQuery(it) },
            placeholder = { Text("Search") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
        )
        LazyColumn(Modifier.fillMaxSize()) {
            items(items, key = { it.id }) { item ->
                // The first row composed is the first row on its way to the screen, as SwiftUI's
                // onAppear of the first row is in the other arms; the frame that shows it is marked.
                if (item.id == items.first().id) LaunchedEffect(Unit) { probe.mark("rowAppeared") }
                ItemRow(item, Modifier.clickable { onOpen(item) })
                HorizontalDivider()
            }
        }
    }
}

@Composable
private fun ItemRow(item: Item, modifier: Modifier = Modifier) {
    Row(
        modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Box(Modifier.size(48.dp).clip(RoundedCornerShape(8.dp)).background(thumbnailColor(item.thumbnail)))
        Column(Modifier.weight(1f)) {
            Text(item.title, style = MaterialTheme.typography.titleMedium)
            Text(item.subtitle, style = MaterialTheme.typography.bodyMedium)
            Text(item.detail, style = MaterialTheme.typography.bodySmall)
        }
        Text("${item.badge}", style = MaterialTheme.typography.labelLarge)
    }
}

@Composable
private fun DetailScreen(item: Item, onBack: () -> Unit) {
    val angle by rememberInfiniteTransition().animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(tween(2000, easing = LinearEasing), RepeatMode.Restart),
    )
    Column(Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        TextButton(onClick = onBack) { Text("Back") }
        Box(Modifier.fillMaxWidth().size(240.dp).clip(RoundedCornerShape(12.dp)).background(thumbnailColor(item.thumbnail)))
        Text(item.title, style = MaterialTheme.typography.headlineMedium)
        Box(Modifier.size(40.dp).rotate(angle).background(Color.Gray))
        Text(item.detail, style = MaterialTheme.typography.bodyLarge)
    }
}

/** A placeholder for the bundled thumbnails of the full spec (B-07): a colour per thumbnail index. */
private fun thumbnailColor(index: Int): Color = Color.hsv(((index * 37) % 360).toFloat(), 0.45f, 0.85f)
