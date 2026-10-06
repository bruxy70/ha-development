# Templates

## Contents

- [10. HMI Gauge Templates](#10-hmi-gauge-templates)
- [Template A: Semicircular Gauge (Large, in card)](#template-a-semicircular-gauge-large-in-card)
- [Template B: Semicircular Gauge (Small, in card)](#template-b-semicircular-gauge-small-in-card)
- [Template C: Bidirectional Gauge (e.g., Grid power)](#template-c-bidirectional-gauge-eg-grid-power)
- [Template D: 360-degree Compass](#template-d-360-degree-compass)
- [Template E: Forecast Card (non-gauge)](#template-e-forecast-card-non-gauge)

Geometry placeholders, ranges, dimensions, palette and typography are adaptable. Preserve valid XML and the selected coordinate/layer relationship; resolve a complete svg wrapper before rendering. Each gauge instance needs unique IDs.

## 10. HMI Gauge Templates

These are ready-to-use, copy-paste templates with computed geometry matching the LVGL gauge design standard. They solve all the rendering issues encountered in previous mockups.

### Template A: Semicircular Gauge (Large, in card)

Matches LVGL large gauge: 130x130 meter, 84x84 crop, meter_y_offset=40.

**Parameters:**
- Card position: `(card_x, card_y)`, size `card_w x card_h`
- Gauge center: `(card_x + card_w/2, card_y + 88)` (name label above, value below)
- Arc radius: 65 (half of 130)
- Crop radius: 42 (half of 84)
- Tick inner radius: 49 (65 - 16 tick length)
- Tick outer radius: 65

```xml
<g id="gauge-name">
  <!-- Card background -->
  <rect x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h}" rx="8" fill="#1e1e1e" />

  <!-- Icon (top-left of card) -->
  <!-- Use <image> or text placeholder for MDI icon -->

  <!-- Name label (above gauge arc, clear space) -->
  <text x="{cx}" y="{card_y + 34}"
        text-anchor="middle" dominant-baseline="central"
        font-family="Montserrat, sans-serif" font-size="12" fill="#b0b0b0">
    GAUGE NAME
  </text>

  <!-- Gauge group centered at pivot point -->
  <g transform="translate({cx}, {cy})">
    <!-- Layer 1: Background arc (full semicircle) -->
    <path d="M -65 0 A 65 65 0 0 1 65 0"
          fill="none" stroke="#252525" stroke-width="14" stroke-linecap="round" />

    <!-- Layer 2: Gradient arc (full range, using stroke gradient) -->
    <!-- Define gradient in <defs> with gradientUnits="userSpaceOnUse"
         x1="-65" y1="0" x2="65" y2="0" -->
    <path d="M -65 0 A 65 65 0 0 1 65 0"
          fill="none" stroke="url(#gradient-id)" stroke-width="14" />

    <!-- Layer 2b: Major tick marks ONLY (no dasharray — the gradient arc provides the colored band) -->
    <!-- Draw individual lines from outer radius inward. Use Section 8 math for positions. -->
    <!-- Example: 5 major ticks at 180°, 225°, 270°, 315°, 360° (left to right) -->
    <!-- For angle θ (SVG): outer=(r·cosθ, r·sinθ), inner=(inner_r·cosθ, inner_r·sinθ) -->
    <!-- Large gauge: r=65, inner_r=49 (tick length=16). Small gauge: r=52.5, inner_r=40.5 (tick length=12) -->
    <line x1="-65" y1="0" x2="-49" y2="0" stroke="#444" stroke-width="2" />
    <line x1="-45.96" y1="-45.96" x2="-34.65" y2="-34.65" stroke="#444" stroke-width="2" />
    <line x1="0" y1="-65" x2="0" y2="-49" stroke="#444" stroke-width="2" />
    <line x1="45.96" y1="-45.96" x2="34.65" y2="-34.65" stroke="#444" stroke-width="2" />
    <line x1="65" y1="0" x2="49" y2="0" stroke="#444" stroke-width="2" />

    <!-- Layer 4: Crop circle (CRITICAL: hides arc interior; later needle is segmented) -->
    <circle cx="0" cy="0" r="42" fill="#1e1e1e" />

    <!-- Layer 5: Needle (starts at crop radius, extends to r + r_mod) -->
    <!-- rotation = -90 + fraction * 180, where fraction = (value - min) / (max - min) -->
    <!-- Needle drawn from crop_r to (r + r_mod), then rotated. This leaves a gap for text. -->
    <!-- Large: crop_r=42, r+5=70. Small: crop_r=33, r+5=57.5 -->
    <line x1="0" y1="-42" x2="0" y2="-70"
          stroke="#ffffff" stroke-width="3" stroke-linecap="round"
          transform="rotate({rotation})" />

    <!-- Layer 6: Center cap (covers needle pivot) -->
    <circle cx="0" cy="0" r="5" fill="#333333" />
  </g>

  <!-- Layer 7: Value text (below crop circle center, inside cropped area) -->
  <text x="{cx}" y="{cy - 8}"
        text-anchor="middle" dominant-baseline="central"
        font-family="Montserrat, sans-serif" font-size="22" font-weight="500"
        fill="#ffffff">
    3.2
  </text>

  <!-- Layer 8: Unit text -->
  <text x="{cx}" y="{cy + 12}"
        text-anchor="middle" dominant-baseline="central"
        font-family="Montserrat, sans-serif" font-size="12" fill="#b0b0b0">
    kW
  </text>

  <!-- Layer 9: Min/max labels (below diameter line) -->
  <!-- y = cy + 6 (gap below diameter), x = cx +/- 58 -->
  <text x="{cx - 58}" y="{cy + 6}"
        text-anchor="middle" dominant-baseline="hanging"
        font-family="Montserrat, sans-serif" font-size="10" fill="#909090">
    0
  </text>
  <text x="{cx + 58}" y="{cy + 6}"
        text-anchor="middle" dominant-baseline="hanging"
        font-family="Montserrat, sans-serif" font-size="10" fill="#909090">
    10
  </text>
</g>
```

### Template B: Semicircular Gauge (Small, in card)

Matches LVGL small gauge: 105x105 meter, 66x66 crop, meter_y_offset=34.

Differences from Template A:
- Arc radius: 52.5 (half of 105)
- Crop radius: 33 (half of 66)
- Min/max y = cy + 6, x = cx +/- 48
- Tick inner radius: 40.5 (52.5 - 12 tick length)

Same layer structure, same z-order, just smaller dimensions.

### Template C: Bidirectional Gauge (e.g., Grid power)

Same structure as Template A but with two gradient arcs meeting at center:

```xml
<g transform="translate({cx}, {cy})">
<!-- Give every rendered gauge unique gradient IDs. Defs and paths share this local coordinate space. -->
<!-- Two gradients: one for negative half, one for positive half -->
<defs>
  <linearGradient id="neg-grad" gradientUnits="userSpaceOnUse"
                  x1="-65" y1="0" x2="0" y2="0">
    <stop offset="0%" stop-color="#FF3000" />
    <stop offset="100%" stop-color="#1E1E1E" />
  </linearGradient>
  <linearGradient id="pos-grad" gradientUnits="userSpaceOnUse"
                  x1="0" y1="0" x2="65" y2="0">
    <stop offset="0%" stop-color="#1E1E1E" />
    <stop offset="100%" stop-color="#00E000" />
  </linearGradient>
</defs>

<!-- Left half (negative/import) -->
<path d="M -65 0 A 65 65 0 0 1 0 -65"
      fill="none" stroke="url(#neg-grad)" stroke-width="14" />

<!-- Right half (positive/export) -->
<path d="M 0 -65 A 65 65 0 0 1 65 0"
      fill="none" stroke="url(#pos-grad)" stroke-width="14" />

<!-- Min/max labels use colored text -->
<!-- Min (left): fill="#FF3000", Max (right): fill="#00E000" -->
</g>
```

### Template D: 360-degree Compass

```xml
<g transform="translate({cx}, {cy})">
  <!-- Outer ring -->
  <circle cx="0" cy="0" r="100" fill="none" stroke="#333" stroke-width="1" />

  <!-- Tick marks at 30-degree intervals -->
  <!-- Major (N/E/S/W): longer, brighter -->
  <!-- Minor (NE/SE/SW/NW): shorter, dimmer -->
  <!-- Cardinal: from r=85 to r=100 -->
  <line x1="0" y1="-85" x2="0" y2="-100" stroke="#666" stroke-width="2" />
  <line x1="85" y1="0" x2="100" y2="0" stroke="#666" stroke-width="2" />
  <line x1="0" y1="85" x2="0" y2="100" stroke="#666" stroke-width="2" />
  <line x1="-85" y1="0" x2="-100" y2="0" stroke="#666" stroke-width="2" />

  <!-- Cardinal labels (outside ring) -->
  <text x="0" y="-108" text-anchor="middle" dominant-baseline="central"
        font-size="14" fill="white">N</text>
  <text x="110" y="0" text-anchor="middle" dominant-baseline="central"
        font-size="12" fill="#b0b0b0">E</text>
  <text x="0" y="112" text-anchor="middle" dominant-baseline="central"
        font-size="12" fill="#b0b0b0">S</text>
  <text x="-110" y="0" text-anchor="middle" dominant-baseline="central"
        font-size="12" fill="#b0b0b0">W</text>

  <!-- Crop circle (hides center) -->
  <circle cx="0" cy="0" r="70" fill="#1e1e1e" />

  <!-- Direction needle (starts at crop radius, extends to outer - r_mod) -->
  <!-- angle_svg = wind_direction_degrees (0=North=up in SVG after translate) -->
  <line x1="0" y1="-70" x2="0" y2="-98"
        stroke="#ffffff" stroke-width="3" stroke-linecap="round"
        transform="rotate({wind_dir_degrees})" />

  <!-- Center cap -->
  <circle cx="0" cy="0" r="6" fill="#333" />
</g>
```

### Template E: Forecast Card (non-gauge)

```xml
<g id="forecast-card">
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#1e1e1e" />

  <!-- Title -->
  <text x="{cx}" y="{y + 24}" text-anchor="middle" dominant-baseline="central"
        font-size="12" fill="#b0b0b0">TODAY'S FORECAST</text>

  <!-- Weather icon area (centered, leave room for 40x40 icon) -->
  <!-- Icon placeholder at (cx, y + 60) -->

  <!-- Condition text -->
  <text x="{cx}" y="{y + 90}" text-anchor="middle" dominant-baseline="central"
        font-size="12" fill="#b0b0b0">Sunny</text>

  <!-- Min/Max row (horizontally centered) -->
  <text x="{cx - 40}" y="{y + 120}" text-anchor="middle" dominant-baseline="central"
        font-size="10" fill="#3498db">MIN</text>
  <text x="{cx - 15}" y="{y + 120}" text-anchor="middle" dominant-baseline="central"
        font-size="16" fill="#3498db" font-weight="500">8&#176;</text>

  <text x="{cx + 15}" y="{y + 120}" text-anchor="middle" dominant-baseline="central"
        font-size="10" fill="#FFC300">MAX</text>
  <text x="{cx + 40}" y="{y + 120}" text-anchor="middle" dominant-baseline="central"
        font-size="16" fill="#FFC300" font-weight="500">18&#176;</text>

  <!-- Precipitation -->
  <text x="{cx - 20}" y="{y + 150}" text-anchor="end" dominant-baseline="central"
        font-size="10" fill="#b0b0b0">Precip</text>
  <text x="{cx - 15}" y="{y + 150}" text-anchor="start" dominant-baseline="central"
        font-size="14" fill="#3498db" font-weight="500">2 mm</text>
</g>
```
