# Svg Geometry

## Contents

- [1. Coordinate System](#1-coordinate-system)
- [Fundamentals](#fundamentals)
- [viewBox](#viewbox)
- [Transform](#transform)
- [2. Path Commands](#2-path-commands)
- [Essential Commands](#essential-commands)
- [Arc Command (Critical for Gauges)](#arc-command-critical-for-gauges)
- [Semicircular Arc Recipe (opening upward)](#semicircular-arc-recipe-opening-upward)
- [3. Shapes](#3-shapes)
- [Basic Shapes](#basic-shapes)
- [Stroke Properties](#stroke-properties)
- [4. Text Rendering](#4-text-rendering)
- [Horizontal Alignment: text-anchor](#horizontal-alignment-text-anchor)
- [Vertical Alignment: dominant-baseline (CRITICAL)](#vertical-alignment-dominant-baseline-critical)
- [Perfectly Centered Text](#perfectly-centered-text)
- [Inline Styling with tspan](#inline-styling-with-tspan)
- [5. Z-ordering (Paint Order)](#5-z-ordering-paint-order)
- [Layer Order for the Crop-and-Segment-Needle Pattern](#layer-order-for-the-crop-and-segment-needle-pattern)
- [6. Gradients](#6-gradients)
- [Linear Gradient](#linear-gradient)
- [Gradient Direction Control (objectBoundingBox units)](#gradient-direction-control-objectboundingbox-units)
- [Multi-stop (for temperature-style gauges)](#multi-stop-for-temperature-style-gauges)
- [7. Clipping](#7-clipping)
- [clipPath (for circular displays or ring shapes)](#clippath-for-circular-displays-or-ring-shapes)
- [Simpler Alternative: Paint-Order Crop](#simpler-alternative-paint-order-crop)
- [8. Mathematics](#8-mathematics)
- [Point on Circle](#point-on-circle)
- [SVG Angle Convention](#svg-angle-convention)
- [Clock-to-SVG Conversion](#clock-to-svg-conversion)
- [Value-to-Angle Mapping (Semicircular Gauge)](#value-to-angle-mapping-semicircular-gauge)
- [Needle Rotation](#needle-rotation)
- [Tick Mark Positions](#tick-mark-positions)
- [Arc Length](#arc-length)

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

### Layer Order for the Crop-and-Segment-Needle Pattern

Structure gauge elements from back to front:

```
1. Card background (rect)
2. Gauge arc background (unfilled arc, dark color)
3. Gauge arc fill (gradient or colored arc)
4. Tick marks (if using individual lines)
5. Crop circle (background-colored filled circle, hides arc interior)
6. Needle (segment from crop boundary outward, rotated)
7. Center cap (small filled circle, covers needle base)
8. Value text (inside cropped area)
9. Unit text (below value)
10. Min/max labels (below diameter line)
11. Name label and icon (above gauge)
```

With this layer order the crop circle hides the arc interior, not a needle drawn later. Draw the needle from the crop boundary outward, or paint a center-to-edge needle before the crop. Keep text above overlapping graphics.

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
SVG angle = 180 + (value - min_val) / (max_val - min_val) * 180
```

- value=min: angle=180deg (pointing left)
- value=max: angle=360deg (pointing right)
- value=mid: angle=270deg (pointing up)

### Needle Rotation

For a needle drawn pointing straight up (0, -length) from origin, then rotated:

```
rotation_degrees = -90 + (value - min_val) / (max_val - min_val) * 180
```

- value=min: -90deg (pointing left)
- value=mid: 0deg (pointing up)
- value=max: +90deg (pointing right)

### Tick Mark Positions

For N ticks along a semicircular arc (180deg to 360deg SVG):

```
for i in 0..N:
    angle_deg = 180 + i * 180 / N
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

Gradient coordinate reference: https://www.w3.org/TR/SVG2/pservers.html#LinearGradientElement (gradientUnits and user space).
