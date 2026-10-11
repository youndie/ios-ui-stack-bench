| Arm | .app bytes | zip -9 bytes | zip - A | Main executable | Two clean builds | 1 MiB control |
|---|---|---|---|---|---|---|
| a-native | 1,597,681 | 580,227 |  | 221,408 | byte-identical | +1.000 MiB |
| b1-objc | 3,799,451 | 1,308,109 | +0.73 MB | 2,423,176 | byte-identical | +1.000 MiB |
| b2-skie | 4,025,883 | 1,370,547 | +0.79 MB | 2,649,608 | differ in bytes, same size; zip -1 bytes | +1.000 MiB |
| b3-swift-export | 3,888,403 | 1,340,235 | +0.76 MB | 2,512,128 | differ in bytes, same size; zip -1 bytes | +1.000 MiB |
| c-kmp-cmp | 30,643,412 | 10,800,084 | +10.22 MB | 29,327,992 | byte-identical | +1.000 MiB |

RQ1, one verdict per arm against A:

- **b1-objc - a-native = +0.73 MB**: green (green <= 2 MB, red > 5 MB)
- **c-kmp-cmp - a-native = +10.22 MB**: green (green <= 12 MB, red > 20 MB)
- **b2-skie - a-native = +0.79 MB**: green (green <= 2 MB, red > 5 MB)
- **b3-swift-export - a-native = +0.76 MB**: green (green <= 2 MB, red > 5 MB)

The main executable by origin, from the final link map of build 1 (bytes), classified by
analysis/linkmap.py when this report is generated:

| Arm | app | kotlin | native-in-kotlin | swift-export | linker | system | other | outside the map's symbols |
|---|---|---|---|---|---|---|---|---|
| a-native | 91,682 | 0 | 0 | 0 | 3,879 | 7,980 | 1,585 | 116,282 |
| b1-objc | 85,409 | 2,158,326 | 0 | 0 | 24,062 | 11,232 | 1,585 | 142,562 |
| b2-skie | 86,226 | 2,304,222 | 47,391 | 0 | 32,332 | 12,204 | 1,585 | 165,648 |
| b3-swift-export | 86,738 | 2,159,650 | 0 | 77,595 | 28,123 | 12,764 | 1,585 | 145,673 |
| c-kmp-cmp | 44,006 | 15,871,671 | 12,927,869 | 0 | 233,689 | 14,432 | 2,385 | 233,940 |
