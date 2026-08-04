# Asset size matrix

Every size a concept normally has to produce. Verify against the platform's current
spec before a build and correct this file when it drifts.

## Meta (Facebook / Instagram)

| Placement | Pixels | Ratio |
| --- | --- | --- |
| Feed square | 1080×1080 | 1:1 |
| Feed portrait | 1080×1350 | 4:5 |
| Stories / Reels | 1080×1920 | 9:16 |
| Right column | 1200×628 | 1.91:1 |
| Carousel card | 1080×1080 | 1:1 |

**Safe zones:** Stories/Reels keep text out of the top 250px and bottom 400px — UI
overlays sit there.

## LinkedIn

| Placement | Pixels | Ratio |
| --- | --- | --- |
| Single image ad | 1200×627 | 1.91:1 |
| Square | 1080×1080 | 1:1 |
| Document / carousel page | 1080×1080 or 1920×1080 | 1:1 / 16:9 |
| Company banner | 1128×191 | — |

## TikTok / Shorts / Reels

| Placement | Pixels | Ratio |
| --- | --- | --- |
| In-feed video | 1080×1920 | 9:16 |
| Cover image | 1080×1920 | 9:16 |

**Safe zone:** keep essential text within the central 1080×1420 region.

## X

| Placement | Pixels | Ratio |
| --- | --- | --- |
| Single image | 1600×900 | 16:9 |
| Card image | 1200×628 | 1.91:1 |

## YouTube

| Asset | Pixels | Note |
| --- | --- | --- |
| Thumbnail | 1280×720 | Under 2 MB; legible at 210×118 |
| Channel banner | 2560×1440 | Safe area 1546×423 |
| End screen zone | — | Keep last 20s clear bottom-right |

## Google Display

| Format | Pixels |
| --- | --- |
| Medium rectangle | 300×250 |
| Large rectangle | 336×280 |
| Leaderboard | 728×90 |
| Half page | 300×600 |
| Large mobile banner | 320×100 |
| Billboard | 970×250 |
| Responsive landscape | 1200×628 |
| Responsive square | 1200×1200 |
| Logo (square / landscape) | 1200×1200 / 1200×300 |

## Web / owned

| Asset | Pixels | Note |
| --- | --- | --- |
| Blog header | 1200×630 | Doubles as OG |
| OG / social share | 1200×630 | Text ≤ 6 words |
| Favicon | 512×512 | SVG preferred |
| Email header | 600×200 | Fixed 600px body width |
| Hero (desktop) | 1920×1080 | Under 300 KB after compression |

## Production rules

- **Design at the tallest ratio (9:16) and crop down** — upscaling a 1.91:1 crop to
  vertical always fails.
- **Text zones move per ratio.** Declare where the focal point sits in each crop.
- **Legibility test:** view the thumbnail at 25% — if the message is gone, the text
  is too long.
- **File sizes:** display ads ≤150 KB, social ≤1 MB, web hero ≤300 KB.
- **Formats:** WebP for web, PNG for transparency, JPG for photographic ads, MP4 (H.264)
  for video.
