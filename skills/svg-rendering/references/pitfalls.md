# Pitfalls

## 9. Common Pitfalls

1. **Y-axis is inverted.** `cy - r` is ABOVE center, `cy + r` is BELOW. Every trigonometric result involving y needs this awareness.

2. **Text baseline trap.** Default `dominant-baseline` is `alphabetic` -- y is the baseline, text body is ABOVE y. For centered gauge text, use a renderer-supported baseline or a tested font-metric offset; verify visible alignment.

3. **Arc flag confusion.** For CW arcs: use `sweep=1`. For arcs <= 180deg: use `large-arc=0`. If the arc goes the wrong way, flip sweep. If it takes the long route, flip large-arc.

4. **No full circle with one arc.** Start and end must differ. Use `<circle>` or two semicircular arcs.

5. **Gradient on stroke.** Use `gradientUnits="userSpaceOnUse"` with absolute coordinates. `objectBoundingBox` on stroked paths produces unpredictable mapping.

6. **XML comments cannot contain `--`.** `<!-- This is -- invalid -->` breaks parsing. Rephrase or use alternatives.

7. **fill defaults to black.** Always set `fill="none"` on shapes that should be outline-only.

8. **stroke-width centered on path.** A 20px stroke on r=50 circle renders from r=40 to r=60.

9. **Transform order.** `translate(100,100) rotate(45)` first rotates around (0,0), then translates. To rotate around a point, use `rotate(45, cx, cy)`.

10. **Needle through text.** Use the two crop/needle routes described in the entrypoint acceptance checks; a crop cannot mask a needle painted later.
