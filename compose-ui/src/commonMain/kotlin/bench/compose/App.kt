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
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import bench.compose.resources.Res
import bench.compose.resources.allDrawableResources
import bench.shared.Catalog
import bench.shared.Item
import org.jetbrains.compose.resources.painterResource

/**
 * The whole of arm C's UI, with the stack's idiomatic defaults: Material 3, a `LazyColumn`,
 * JetBrains' navigation-compose with its default transitions, and the thumbnails as Compose
 * resources through `painterResource`.
 */
@Composable
fun App(catalog: Catalog, probe: Probe) {
    MaterialTheme {
        Surface(Modifier.fillMaxSize()) {
            val items by catalog.visible.collectAsState()
            val navController = rememberNavController()
            // The item the detail screen shows; a route argument would be parsed back into the same id.
            var selected by remember { mutableStateOf<Item?>(null) }
            Box(Modifier.fillMaxSize().safeDrawingPadding()) {
                NavHost(navController, startDestination = "list") {
                    composable("list") {
                        ListScreen(items, catalog::filter, onOpen = { selected = it; navController.navigate("detail") }, probe)
                    }
                    composable("detail") {
                        selected?.let { DetailScreen(it, onBack = { navController.popBackStack() }) }
                    }
                }
            }
        }
    }
}

@Composable
private fun ListScreen(items: List<Item>, onQuery: (String) -> Unit, onOpen: (Item) -> Unit, probe: Probe) {
    var query by rememberSaveable { mutableStateOf("") }
    Column(Modifier.fillMaxSize()) {
        Text("Items", style = MaterialTheme.typography.headlineLarge, modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp))
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

/** A row: a 48 dp thumbnail, the title, two lines of text, and a numeric badge. */
@Composable
private fun ItemRow(item: Item, modifier: Modifier = Modifier) {
    Row(
        modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Thumbnail(item.thumbnail, Modifier.size(48.dp).clip(RoundedCornerShape(8.dp)))
        Column(Modifier.weight(1f)) {
            Text(item.title, style = MaterialTheme.typography.titleMedium)
            Text(item.subtitle, style = MaterialTheme.typography.bodyMedium, maxLines = 1, overflow = TextOverflow.Ellipsis)
            Text(item.detail, style = MaterialTheme.typography.bodySmall, maxLines = 1, overflow = TextOverflow.Ellipsis)
        }
        Text(
            "${item.badge}",
            style = MaterialTheme.typography.labelMedium,
            modifier = Modifier
                .clip(RoundedCornerShape(50))
                .background(MaterialTheme.colorScheme.primaryContainer)
                .padding(horizontal = 8.dp, vertical = 2.dp),
        )
    }
}

/** The detail screen: a large image, the title, a square turning once every 2 s, the text blocks. */
@Composable
private fun DetailScreen(item: Item, onBack: () -> Unit) {
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
    Image(painterResource(resource), contentDescription = null, contentScale = ContentScale.Crop, modifier = modifier)
}
