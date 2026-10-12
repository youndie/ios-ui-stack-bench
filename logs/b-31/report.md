| Arm | Apple's download estimate | minus A | Installed | Encrypted worst case | minus A | zip -9 of the same bytes | Executable's encrypted range | Second build, Apple's estimate |
|---|---|---|---|---|---|---|---|---|
| A | 0.61 MB |  | 1.66 MB | 0.67 MB |  | 0.60 MB | 0.11 MB | +5 bytes |
| B1 | 1.35 MB | +0.74 MB | 3.85 MB | 2.52 MB | +1.85 MB | 1.33 MB | 1.85 MB | -1 bytes |
| B2 | 1.41 MB | +0.80 MB | 4.10 MB | 2.70 MB | +2.03 MB | 1.40 MB | 2.02 MB | -1 bytes |
| B3 | 1.38 MB | +0.77 MB | 3.96 MB | 2.59 MB | +1.93 MB | 1.37 MB | 1.92 MB | +4 bytes |
| C | 10.91 MB | +10.30 MB | 30.76 MB | 27.24 MB | +26.57 MB | 10.88 MB | 25.95 MB | +6 bytes |

RQ1 on Apple's download estimate (decides RQ1):

- b1-objc - a-native = **+0.74 MB**: green (green <= 2 MB, red > 5 MB)
- b2-skie - a-native = **+0.80 MB**: green (green <= 2 MB, red > 5 MB)
- b3-swift-export - a-native = **+0.77 MB**: green (green <= 2 MB, red > 5 MB)
- c-kmp-cmp - a-native = **+10.30 MB**: green (green <= 12 MB, red > 20 MB)

RQ1 on encrypted worst case (printed beside, decides nothing):

- b1-objc - a-native = **+1.85 MB**: green (green <= 2 MB, red > 5 MB)
- b2-skie - a-native = **+2.03 MB**: inconclusive (green <= 2 MB, red > 5 MB)
- b3-swift-export - a-native = **+1.93 MB**: green (green <= 2 MB, red > 5 MB)
- c-kmp-cmp - a-native = **+26.57 MB**: red (green <= 12 MB, red > 20 MB)
