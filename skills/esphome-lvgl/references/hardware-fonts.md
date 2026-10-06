# Hardware Fonts

## Contents

- [Hardware Configuration](#hardware-configuration)
- [ESP32-S3 with PSRAM](#esp32-s3-with-psram)
- [ESP32-P4 with MIPI-DSI](#esp32-p4-with-mipi-dsi)
- [Display Drivers](#display-drivers)
- [Touchscreen Controllers](#touchscreen-controllers)
- [Touch Calibration (Portrait / Rotated Displays)](#touch-calibration-portrait--rotated-displays)
- [Circular SPI Display (GC9A01A)](#circular-spi-display-gc9a01a)
- [Rotary Encoder Input](#rotary-encoder-input)
- [Display Configuration Pattern](#display-configuration-pattern)
- [Backlight Control Pattern](#backlight-control-pattern)
- [Fonts](#fonts)

## Hardware Configuration

### ESP32-S3 with PSRAM

```yaml
esphome:
  platformio_options:
    build_flags: "-DBOARD_HAS_PSRAM"
    board_build.esp-idf.memory_type: qio_opi
    board_build.flash_mode: dio

esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf
    sdkconfig_options:
      CONFIG_ESP32S3_DEFAULT_CPU_FREQ_240: y
      CONFIG_ESP32S3_DATA_CACHE_64KB: y
      CONFIG_SPIRAM_FETCH_INSTRUCTIONS: y
      CONFIG_SPIRAM_RODATA: y

psram:
  mode: octal
  speed: 80MHz
```

### ESP32-P4 with MIPI-DSI

Newer boards (e.g. CrowPanel/Waveshare 7" P4) use the ESP32-P4 with a built-in MIPI-DSI
interface and a separate ESP32-C6 co-processor for Wi-Fi. Config differs substantially from S3
— these keys are the non-obvious, load-bearing ones (pin numbers are board-specific):

```yaml
esp32:
  variant: esp32p4              # NOT `board:` — P4 uses `variant:`
  engineering_sample: true      # required for pre-rev3 P4 silicon
  cpu_frequency: 360MHZ
  flash_size: 16MB
  framework:
    type: esp-idf
    advanced:
      execute_from_psram: true              # REQUIRED (keep true; false overflows flash)
      enable_idf_experimental_features: true
  # Do NOT use the old `sdkconfig_options:` block — replaced by `advanced:`

psram:
  speed: 200MHz                 # no `mode:` key on P4

esp_ldo:                        # P4 needs TWO LDO channels (3 AND 4), both 2.5V
  - channel: 3
    voltage: 2.5V
  - channel: 4
    voltage: 2.5V

esp32_hosted:                   # Wi-Fi runs on a C6 co-processor over SDIO
  variant: esp32c6
  # ...reset/cmd/clk/d0–d3 pins per board...
  # sdio_frequency: 10MHz       # stability fix: default 40MHz causes
                                # `sdmmc_io_rw_extended ... 0x109` timeouts/reboots (ESPHome #14313)

display:
  - platform: mipi_dsi          # built into ESPHome — no external_components needed
    model: WAVESHARE-ESP32-P4-WIFI6-TOUCH-LCD-7B   # or CUSTOM with explicit timings
    reset_pin: { number: 41 }
    update_interval: never
    auto_clear_enabled: false
    dimensions: { width: 1024, height: 600 }
    color_order: RGB
    color_depth: 16
```

**RGB565 images need explicit byte order on P4 MIPI-DSI** — set `byte_order: little_endian` on
the `lvgl:` block *and* on every `rgb565`/`RGB565` image, or images render with corrupted
colours. (Not needed on S3 RPI-DPI-RGB.)

```yaml
image:
  - file: foo.png
    type: RGB565
    byte_order: little_endian
lvgl:
  byte_order: little_endian
```

**Backlight + power pins:** backlight is LEDC PWM (e.g. GPIO31); a separate inverted GPIO
"power_light" (e.g. GPIO29) must be turned **off** shortly after boot (`on_boot`). **Flashing (only after config/compile and explicit target/action authorization):**
native USB — hold BOOT, tap RESET, release; command-line `esphome run` is more reliable than
WebSerial. **Legacy display-level rotation route:** put `rotation:` on `display:` and add
`swap_xy`/`mirror_y` to the touchscreen — see "Touch Calibration" below.

### Display Drivers

| Driver | Type | Common Displays |
|--------|------|-----------------|
| `rpi_dpi_rgb` | Parallel RGB | CrowPanel, Sunton, and other larger displays |
| `ili9xxx` | SPI | ILI9341, ILI9488, ST7789, etc. |
| `ssd1306` | I2C/SPI | Small OLED displays |
| `st7920` | LCD | Character displays |

### Touchscreen Controllers

| Controller | Interface | Common Usage |
|------------|-----------|-------------|
| `gt911` | I2C | Larger RGB displays |
| `cst816` | I2C | Small round displays |
| `xpt2046` | SPI | Resistive touch |
| `ft5x06` | I2C | Capacitive touch |

### Touch Calibration (Portrait / Rotated Displays)

For the legacy display-level rotation route, when using `rotation: 90` (or other rotations) on the display, the touchscreen coordinates must be transformed to match. Use `swap_xy` and `mirror_x`/`mirror_y` on the touchscreen component.

```yaml
touchscreen:
  platform: gt911         # or cst816, etc.
  id: my_touch
  swap_xy: true           # Swap X/Y axes to match rotated display
  mirror_y: true          # Mirror Y axis (common for CrowPanel portrait)
```

**WARNING:** Without correct touch transforms, ALL touch events will silently miss their target widgets -- no errors in the log, but no buttons work. Debug with:
```yaml
touchscreen:
  on_touch:
    - lambda: 'ESP_LOGI("touch", "x=%d y=%d", touch.x, touch.y);'
```
Verify that reported coordinates match the positions of your LVGL widgets.

### Circular SPI Display (GC9A01A)

Round 240x240 displays (common on rotary knob boards) use the ILI9XXX platform:

```yaml
display:
  - platform: ili9xxx
    model: GC9A01A
    id: my_display
    cs_pin: GPIOxx
    dc_pin: GPIOxx
    reset_pin: GPIOxx
    invert_colors: true         # Usually required
    update_interval: never
    auto_clear_enabled: false
    dimensions:
      width: 240
      height: 240
```

- Pixels outside the inscribed circle are not visible (hardware clips) -- no LVGL masking needed
- No `rotation` needed for round displays
- Very small resolution: use arcs and labels primarily, avoid complex grids/panels

### Rotary Encoder Input

For rotary encoders connected via GPIO, use `on_clockwise`/`on_anticlockwise` triggers. They fire once per detent, clean and simple.

```yaml
sensor:
  - platform: rotary_encoder
    id: rotary
    pin_a: GPIOxx
    pin_b: GPIOxx
    on_clockwise:
      - lambda: |-
          // Increment value, switch to next item, etc.
    on_anticlockwise:
      - lambda: |-
          // Decrement value, switch to previous item, etc.

binary_sensor:
  - platform: gpio
    id: rotary_button
    pin:
      number: GPIOxx
      mode: INPUT_PULLUP
      inverted: true
    on_click:
      - lambda: |-
          // Confirm selection, toggle mode, etc.
```

Prefer `on_clockwise`/`on_anticlockwise` for per-detent navigation. Use `on_value` for absolute position or accumulated movement; validate bounds/debounce.

### Display Configuration Pattern

A typical display setup includes the display driver, I2C bus (for touchscreen), and touchscreen controller. Adjust pins and driver for your specific board.

```yaml
display:
  - platform: <driver>        # rpi_dpi_rgb, ili9xxx, ssd1306, etc.
    id: my_display
    update_interval: never     # Required for LVGL
    auto_clear_enabled: false  # Required for LVGL
    dimensions:
      width: <width>
      height: <height>
    # Driver-specific pin configuration...

i2c:
  sda: <sda_pin>
  scl: <scl_pin>

touchscreen:
  platform: <controller>      # gt911, cst816, xpt2046, ft5x06
  id: my_touch
```

### Backlight Control Pattern

```yaml
output:
  - platform: ledc
    pin: <backlight_pin>       # Board-specific GPIO
    frequency: 1220
    id: gpio_backlight_pwm

light:
  - platform: monochromatic
    output: gpio_backlight_pwm
    name: Display Backlight
    id: back_light
    restore_mode: ALWAYS_ON
```

---

## Fonts

**Built-in Montserrat (Medium weight, basic Latin + degree + bullet + FontAwesome subset):**
`montserrat_8`, `montserrat_10`, `montserrat_12`, `montserrat_14` (default), `montserrat_16`, `montserrat_18`, `montserrat_20`, `montserrat_22`, `montserrat_24`, `montserrat_26`, `montserrat_28`, `montserrat_30`, `montserrat_32`, `montserrat_34`, `montserrat_36`, `montserrat_38`, `montserrat_40`, `montserrat_42`, `montserrat_44`, `montserrat_46`, `montserrat_48`

In YAML these are referenced as uppercase: `MONTSERRAT_14`, `MONTSERRAT_16`, etc.

**Built-in Montserrat Unicode limitations:** The built-in fonts contain only ASCII + degree + bullet + a small FontAwesome subset. Any non-ASCII Unicode symbols will render as rectangles:
- Unicode triangles (U+25C0, U+25B6) -- use plain ASCII `<` `>` instead
- Lightning bolt (U+26A1) -- use text like "CHG" instead
- Diacritics (ě, ř, č, ž, š, ú, etc.) -- need custom font (see below)
- **Rule:** Assume any non-Latin symbol is missing from built-in fonts. Test or use ASCII fallbacks.

**Special fonts:**
- `unscii_8` / `unscii_16` -- Pixel-perfect ASCII monospace
- `simsun_16_cjk` -- CJK Radicals
- `dejavu_16_persian_hebrew` -- Persian/Hebrew

**Custom fonts via ESPHome font component:**
```yaml
font:
  - file: "gfonts://Roboto"
    id: roboto_20
    size: 20
    bpp: 4            # Use bpp: 4 for LVGL anti-aliasing
    extras:
      - file: "fonts/materialdesignicons-webfont.ttf"
        glyphs: ["\U000F02D1"]
```

**Extended Latin (diacritics) font pattern:**
For languages with diacritics (Czech, Polish, French, etc.), use a custom font with `GF_Latin_Core` glyphset:
```yaml
font:
  - file: "gfonts://Montserrat@500"    # @500 = Medium weight (matches built-in)
    id: montserrat_ext_16
    size: 16
    bpp: 4                              # Required for LVGL anti-aliasing
    glyphsets:
      - GF_Latin_Core                   # Covers most European diacritics
    # For specific missing chars (e.g. ď, ť, ň), add:
    # glyphs: "ďťň"
```
Each custom font size adds ~42-80KB to flash. Fine on 16MB ESP32-S3.
