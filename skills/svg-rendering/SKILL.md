---
name: svg-rendering
description: SVG rendering reference for producing accurate HMI display mockups. Covers coordinate systems, paths, arcs, text positioning, clipping, gradients, z-ordering, and provides ready-to-use gauge templates with computed geometry.
allowed-tools: Read, Grep
---

# SVG Rendering Reference for HMI Display Mockups

Comprehensive SVG specification reference for generating pixel-accurate gauge, arc, text, and dashboard mockups that faithfully represent LVGL display layouts.

---

## 1. Coordinate System

### Fundamentals

- **Origin (0,0)** at **top-left corner**
- **X-axis** increases **rightward**
- **Y-axis** increases **downward** (opposite of math convention -- this is critical for angle calculations)
- One user unit = one pixel when viewBox matches width/height

### viewBox

```
viewBox="min-x min-y width height"
```

For HMI mockups, always match viewBox to target display resolution:

```xml
<!-- 800x480 landscape display -->
<svg width="800" height="480" viewBox="0 0 800 480" xmlns="http://www.w3.org/2000/svg">
```

### Transform

| Function | Syntax | Notes |
|----------|--------|-------|
| `translate` | `translate(x, y)` | y defaults to 0 |
| `rotate` | `rotate(deg, cx, cy)` | cx,cy = pivot (default 0,0) |
| `scale` | `scale(x, y)` | y defaults to x |

**Transforms apply right-to-left:** `translate(100,100) rotate(45)` first rotates, then translates.

Use `<g transform="translate(cx, cy)">` to create local coordinate systems centered on gauge pivots:

```xml
<g transform="translate(240, 400)">
  <!-- (0,0) is now the gauge center -->
  <circle cx="0" cy="0" r="80" />
  <line x1="0" y1="0" x2="0" y2="-70" transform="rotate(45)" />
</g>
```

---

## 2. Path Commands

The `d` attribute uses commands. **Uppercase = absolute, lowercase = relative.**

### Essential Commands

| Command | Syntax | Description |
|---------|--------|-------------|
| `M x y` | Move to | Set cursor (no drawing) |
| `L x y` | Line to | Straight line |
| `H x` | Horizontal | Horizontal line to x |
| `V y` | Vertical | Vertical line to y |
| `A` | Arc | Elliptical arc (see below) |
| `Z` | Close | Line back to path start |

### Arc Command (Critical for Gauges)

```
A rx ry x-rotation large-arc-flag sweep-flag x y
```

| Parameter | Description |
|-----------|-------------|
| `rx ry` | Ellipse radii (equal for circles) |
| `x-rotation` | Ellipse rotation (0 for circles) |
| `large-arc-flag` | `1` = arc > 180deg, `0` = arc <= 180deg |
| `sweep-flag` | `1` = clockwise, `0` = counter-clockwise |
| `x y` | Endpoint (absolute) |

**Flag combinations:**

| large-arc | sweep | Result |
|-----------|-------|--------|
| 0 | 1 | Short arc, clockwise (most common for gauges) |
| 1 | 1 | Long arc, clockwise |
| 0 | 0 | Short arc, counter-clockwise |
| 1 | 0 | Long arc, counter-clockwise |

**A single arc cannot draw a full circle** (start = end is undefined). Use two semicircular arcs or `<circle>`.

### Semicircular Arc Recipe (opening upward)

Center `(cx, cy)`, radius `r`:

```
Start: (cx - r, cy)   [9 o'clock / left]
End:   (cx + r, cy)    [3 o'clock / right]
Flags: large-arc=0, sweep=1
```

```xml
<path d="M {cx-r} {cy} A {r} {r} 0 0 1 {cx+r} {cy}" />
```

Concrete: center (150, 100), radius 80:
```xml
<path d="M 70 100 A 80 80 0 0 1 230 100"
      fill="none" stroke="#444" stroke-width="12" stroke-linecap="round" />
```

---

## 3. Shapes

### Basic Shapes

```xml
<rect x="10" y="10" width="200" height="100" rx="8" fill="#1E1E1E" />
<circle cx="100" cy="100" r="50" fill="none" stroke="white" stroke-width="2" />
<line x1="10" y1="10" x2="200" y2="10" stroke="#333" stroke-width="1" />
```

### Stroke Properties

**stroke-linecap:**

| Value | Effect |
|-------|--------|
| `butt` (default) | Ends exactly at endpoints |
| `round` | Half-circle cap (preferred for gauge arcs) |
| `square` | Half-square cap extending past endpoint |

**stroke-dasharray** (for tick-mark simulation):

```xml
<!-- 2px dash, 10px gap = evenly spaced tick marks -->
<path d="M 50 150 A 100 100 0 0 1 250 150"
      fill="none" stroke="white" stroke-width="8"
      stroke-dasharray="2 10" stroke-linecap="butt" />
```

Gap calculation for N ticks: `gap = (arc_length / N) - dash_width`
Semicircle arc length = PI * r

**stroke-width is centered on the path:** A stroke-width of 20 on a circle with r=50 spans from r=40 to r=60.

---

## 4. Text Rendering

### Horizontal Alignment: text-anchor

| Value | Behavior |
|-------|----------|
| `start` (default) | Text begins at x (left-aligned) |
| `middle` | Text centered on x |
| `end` | Text ends at x (right-aligned) |

### Vertical Alignment: dominant-baseline (CRITICAL)

**Default is `auto`/`alphabetic` where `y` = baseline, text body above.** This is the #1 source of mispositioned text in SVG.

| Value | y coordinate aligns to |
|-------|----------------------|
| `alphabetic` (default) | Text baseline (body above, descenders below) |
| `central` | Vertical center of text. **Use this for centering.** |
| `middle` | Middle of em box. Similar to central. |
| `hanging` | Top of text (text hangs below y) |

### Perfectly Centered Text

```xml
<text x="150" y="100"
      text-anchor="middle"
      dominant-baseline="central"
      font-family="Montserrat, sans-serif" font-size="22"
      fill="white">
  3.2
</text>
```

Both `text-anchor="middle"` (horizontal) AND `dominant-baseline="central"` (vertical) are needed.

### Inline Styling with tspan

```xml
<text x="100" y="50" text-anchor="middle" dominant-baseline="central">
  <tspan font-size="22" fill="white" font-weight="500">3.2</tspan>
  <tspan font-size="12" fill="#b0b0b0" dx="2">kW</tspan>
</text>
```

`dx`/`dy` = relative offset from current text position.

---

## 5. Z-ordering (Paint Order)

**SVG has NO z-index.** Elements paint in document order: later = on top.

### Gauge Layer Order (MANDATORY)

Structure gauge elements from back to front:

```
1. Card background (rect)
2. Gauge arc background (unfilled arc, dark color)
3. Gauge arc fill (gradient or colored arc)
4. Tick marks (if using individual lines)
5. Crop circle (background-colored filled circle, hides arc interior)
6. Needle (line from center, rotated)
7. Center cap (small filled circle, covers needle base)
8. Value text (inside cropped area)
9. Unit text (below value)
10. Min/max labels (below diameter line)
11. Name label and icon (above gauge)
```

**The crop circle (item 5) is what prevents the needle from crossing through the text.** It must come AFTER the arc but BEFORE the text. This was the primary issue in our earlier mockups.

---

## 6. Gradients

### Linear Gradient

```xml
<defs>
  <linearGradient id="solar-grad" gradientUnits="userSpaceOnUse"
                  x1="70" y1="100" x2="230" y2="100">
    <stop offset="0%" stop-color="#B8A800" />
    <stop offset="100%" stop-color="#F0E000" />
  </linearGradient>
</defs>

<path d="..." fill="none" stroke="url(#solar-grad)" stroke-width="14" />
```

**For gradient on stroke, always use `gradientUnits="userSpaceOnUse"`** with coordinates matching the arc's horizontal extent. `objectBoundingBox` produces unpredictable results on arc strokes.

### Gradient Direction Control (objectBoundingBox units)

| Direction | x1 | y1 | x2 | y2 |
|-----------|----|----|----|----|
| Left to right | 0 | 0 | 1 | 0 |
| Top to bottom | 0 | 0 | 0 | 1 |
| Right to left | 1 | 0 | 0 | 0 |

### Multi-stop (for temperature-style gauges)

```xml
<linearGradient id="temp-grad" gradientUnits="userSpaceOnUse"
                x1="46" y1="150" x2="254" y2="150">
  <stop offset="0%" stop-color="#3498DB" />     <!-- cold blue -->
  <stop offset="33%" stop-color="#3498DB" />
  <stop offset="50%" stop-color="#FFC300" />     <!-- warm amber -->
  <stop offset="75%" stop-color="#FFC300" />
  <stop offset="100%" stop-color="#FF3000" />    <!-- hot red -->
</linearGradient>
```

---

## 7. Clipping

### clipPath (for circular displays or ring shapes)

```xml
<defs>
  <clipPath id="ring-clip" clipPathUnits="userSpaceOnUse">
    <path d="M 150 50 A 100 100 0 1 1 149.99 50 Z
             M 150 80 A 70 70 0 1 0 150.01 80 Z"
          fill-rule="evenodd" />
  </clipPath>
</defs>

<g clip-path="url(#ring-clip)">
  <!-- Only ring between r=70 and r=100 is visible -->
</g>
```

For HMI mockups, use `clipPathUnits="userSpaceOnUse"` (absolute pixel coordinates).

### Simpler Alternative: Paint-Order Crop

For most gauge mockups, a filled circle on top is simpler than clipPath:

```xml
<!-- Arc renders first -->
<path d="..." stroke="url(#gradient)" stroke-width="14" fill="none" />
<!-- Background-colored circle covers the interior -->
<circle cx="150" cy="150" r="60" fill="#1E1E1E" />
```

---

## 8. Mathematics

### Point on Circle

```
x = cx + r * cos(angle_radians)
y = cy + r * sin(angle_radians)
```

Convert degrees to radians: `radians = degrees * PI / 180`

### SVG Angle Convention

- 0deg = right (3 o'clock)
- 90deg = down (6 o'clock) -- because Y increases downward
- 180deg = left (9 o'clock)
- 270deg / -90deg = up (12 o'clock)

Angles increase **clockwise**.

### Clock-to-SVG Conversion

```
svg_degrees = clock_degrees - 90
```

| Position | Clock deg | SVG deg |
|----------|-----------|---------|
| Top (12:00) | 0 | -90 |
| Right (3:00) | 90 | 0 |
| Bottom (6:00) | 180 | 90 |
| Left (9:00) | 270 | 180 |

### Value-to-Angle Mapping (Semicircular Gauge)

For a semicircle gauge (left=min, right=max):

```
SVG angle = 180 - (value - min_val) / (max_val - min_val) * 180
```

- value=min: angle=180deg (pointing left)
- value=max: angle=0deg (pointing right)
- value=mid: angle=90deg (pointing up, but in SVG = -90 from top)

### Needle Rotation

For a needle drawn pointing straight up (0, -length) from origin, then rotated:

```
rotation_degrees = -90 + (value - min_val) / (max_val - min_val) * 180
```

- value=min: -90deg (pointing left)
- value=mid: 0deg (pointing up)
- value=max: +90deg (pointing right)

### Tick Mark Positions

For N ticks along a semicircular arc (180deg to 0deg SVG):

```
for i in 0..N:
    angle_deg = 180 - i * 180 / N
    angle_rad = angle_deg * PI / 180
    inner_x = cx + inner_r * cos(angle_rad)
    inner_y = cy + inner_r * sin(angle_rad)
    outer_x = cx + outer_r * cos(angle_rad)
    outer_y = cy + outer_r * sin(angle_rad)
```

### Arc Length

- Full circle: `2 * PI * r`
- Semicircle: `PI * r`
- Arbitrary angle: `r * angle_radians`

---

## 9. Common Pitfalls

1. **Y-axis is inverted.** `cy - r` is ABOVE center, `cy + r` is BELOW. Every trigonometric result involving y needs this awareness.

2. **Text baseline trap.** Default `dominant-baseline` is `alphabetic` -- y is the baseline, text body is ABOVE y. Always set `dominant-baseline="central"` for centered text in gauges.

3. **Arc flag confusion.** For CW arcs: use `sweep=1`. For arcs <= 180deg: use `large-arc=0`. If the arc goes the wrong way, flip sweep. If it takes the long route, flip large-arc.

4. **No full circle with one arc.** Start and end must differ. Use `<circle>` or two semicircular arcs.

5. **Gradient on stroke.** Use `gradientUnits="userSpaceOnUse"` with absolute coordinates. `objectBoundingBox` on stroked paths produces unpredictable mapping.

6. **XML comments cannot contain `--`.** `<!-- This is -- invalid -->` breaks parsing. Rephrase or use alternatives.

7. **fill defaults to black.** Always set `fill="none"` on shapes that should be outline-only.

8. **stroke-width centered on path.** A 20px stroke on r=50 circle renders from r=40 to r=60.

9. **Transform order.** `translate(100,100) rotate(45)` first rotates around (0,0), then translates. To rotate around a point, use `rotate(45, cx, cy)`.

10. **Needle through text.** If the crop circle is missing or placed after the text in document order, the needle will visually cross through label text. Always follow the layer order in Section 5.

---

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
         x1="{cx-65}" y1="{cy}" x2="{cx+65}" y2="{cy}" -->
    <path d="M -65 0 A 65 65 0 0 1 65 0"
          fill="none" stroke="url(#gradient-id)" stroke-width="14" />

    <!-- Layer 2b: Major tick marks ONLY (no dasharray — the gradient arc provides the colored band) -->
    <!-- Draw individual lines from outer radius inward. Use Section 8 math for positions. -->
    <!-- Example: 5 major ticks at 180°, 135°, 90°, 45°, 0° (left to right) -->
    <!-- For angle θ (SVG): outer=(r·cosθ, r·sinθ), inner=(inner_r·cosθ, inner_r·sinθ) -->
    <!-- Large gauge: r=65, inner_r=49 (tick length=16). Small gauge: r=52.5, inner_r=40.5 (tick length=12) -->
    <line x1="-65" y1="0" x2="-49" y2="0" stroke="#444" stroke-width="2" />
    <line x1="-45.96" y1="-45.96" x2="-34.65" y2="-34.65" stroke="#444" stroke-width="2" />
    <line x1="0" y1="-65" x2="0" y2="-49" stroke="#444" stroke-width="2" />
    <line x1="45.96" y1="-45.96" x2="34.65" y2="-34.65" stroke="#444" stroke-width="2" />
    <line x1="65" y1="0" x2="49" y2="0" stroke="#444" stroke-width="2" />

    <!-- Layer 4: Crop circle (CRITICAL: hides arc interior + needle base) -->
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
<!-- Two gradients: one for negative half, one for positive half -->
<defs>
  <linearGradient id="neg-grad" gradientUnits="userSpaceOnUse"
                  x1="{cx-65}" y1="{cy}" x2="{cx}" y2="{cy}">
    <stop offset="0%" stop-color="#FF3000" />
    <stop offset="100%" stop-color="#1E1E1E" />
  </linearGradient>
  <linearGradient id="pos-grad" gradientUnits="userSpaceOnUse"
                  x1="{cx}" y1="{cy}" x2="{cx+65}" y2="{cy}">
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

---

## 11. Project-Specific Style Constants

These match the design system defined in `docs/architecture.md`:

### Colors

```
Background:      #111111
Card background:  #1e1e1e (rx=8)
Primary text:     #ffffff
Secondary text:   #b0b0b0
Min/max labels:   #909090
Muted text:       #666666
Inactive:         #404040
Card border:      #333333 (subtle, optional)

Solar:    #B8A800 to #F0E000
House:    #505050 to #A0A0A0
Grid neg: #FF3000 to #1E1E1E
Grid pos: #1E1E1E to #00E000
EV:       #6A2C91 to #9B59B6
Water:    #505050 to #3498DB
Temp cold: #3498DB
Temp warm: #FFC300
Temp hot:  #FF3000
```

### Font Sizes (Montserrat)

| Element | Size | Weight |
|---------|------|--------|
| Gauge value | 22px | 500 |
| Button text | 20px | 500 |
| Slider title | 24px | 500 |
| Labels, units, names | 12px | 500 |
| Min/max endpoints | 10px | 400 |
| Wind gust, secondary values | 16px | 500 |

### Gauge Geometry (computed, not guessed)

| Property | Large gauge | Small gauge |
|----------|------------|-------------|
| Meter diameter | 130 | 105 |
| Arc radius | 65 | 52.5 |
| Crop radius | 42 | 33 |
| Tick length | 16 | 12 |
| Major tick length | 20 | 16 |
| Needle r_mod equivalent | extends to r+5 | extends to r+5 |
| Center cap radius | 5 | 4 |
| Min/max y (below diameter) | +6 | +6 |
| Min/max x (from center) | +/-58 | +/-48 |

---

## 12. Rendering Checklist

Before finalizing any SVG mockup, verify each item:

- [ ] **Layer order correct:** background -> arc -> ticks -> crop circle -> needle -> cap -> text -> min/max -> name/icon
- [ ] **Crop circle present:** Filled circle matching card background color, placed AFTER arc but BEFORE needle and text
- [ ] **Text uses dominant-baseline="central":** All centered text must have this
- [ ] **Gradient uses userSpaceOnUse:** All stroke gradients use absolute coordinates
- [ ] **No `--` in XML comments**
- [ ] **Name/icon above arc:** Clear vertical space between label and arc top
- [ ] **Value text inside cropped area:** Positioned at gauge center, vertically within crop circle bounds
- [ ] **Min/max below diameter line:** y = cy + gap (6px), not overlapping the arc
- [ ] **Arc flags correct:** Semicircle = large-arc:0, sweep:1
- [ ] **fill="none" on all arcs:** Arcs are stroked paths, not filled
- [ ] **Needle does not cross text:** Crop circle radius > distance from center to text
