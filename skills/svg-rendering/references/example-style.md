# Example Style

## 11. Project-Specific Style Constants

The following palette and geometry are optional example defaults. Use the target project's supplied design system when available; these constants are not a shared requirement.

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
