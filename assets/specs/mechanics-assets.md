# BLACK MARKET Phase 1 mechanics asset specifications

These are production asset requirements, not final artwork. Author at 2× display size, keep safe content inside 90% of each canvas, and export premultiplied-alpha-friendly files for PixiJS. Use local files only.

| Purpose | Filename | Dimensions | Format / transparency | Animation states | PixiJS usage |
| --- | --- | ---: | --- | --- | --- |
| Expanding Wild | `symbol-wild-expand.webp` plus `symbol-wild-expand.json` | 1024×1024 sheet; 256×256 frames | WebP RGBA, transparent | idle, anticipation, expand-start, expand-loop, settle | AnimatedSprite centered per reel; scale vertically to four cells during `expandingWild` and replace with normal Wild textures at settle. |
| Free Spins Scatter | `symbol-scatter-freespins.webp` plus JSON | 1536×512 sheet; 256×256 frames | WebP RGBA, transparent | idle, land, trigger, retrigger, glow-loop | AnimatedSprite in a symbol container; trigger state plays before `freeSpinsStart`. |
| Multiplier badge | `ui-freespins-multiplier.webp` plus JSON | 1024×512 sheet; 256×256 frames | WebP RGBA, transparent | 1×, 2×, 3×, 5×, 10×, pulse | Sprite above reel frame; select configured tier after `multiplierIncrease`, then play pulse. |
| Hold-and-spin locked symbol | `symbol-hold-lock.webp` plus JSON | 1536×768 sheet; 256×256 frames | WebP RGBA, transparent | idle values, land, lock, value-update, multiplier-update, collect | AnimatedSprite at locked cell; preserve instance and metadata across `holdSpinRespins`. |
| Hold-and-spin frame | `frame-hold-spin.webp` plus JSON | 2048×1024 sheet; 512×512 frames | WebP RGBA, transparent | enter, idle-loop, new-lock, final-respin, exit | Nine-slice outer frame plus optional AnimatedSprite accents while Hold & Spin state is active. |
| Cascade/remove effect | `fx-cascade-remove.webp` plus JSON | 2048×1024 sheet; 256×256 frames | WebP RGBA, transparent additive-safe | mark, fracture, dissolve, clear | One pooled AnimatedSprite per winning cell during `removeSymbols`; release before `collapse`. |
| Refill/drop effect | `fx-reel-refill.webp` plus JSON | 2048×1024 sheet; 256×256 frames | WebP RGBA, transparent | drop-start, trail, impact, settle | Pooled overlay following each entering symbol during `refill`; timing derives from the event player. |
| Multiplier increase effect | `fx-multiplier-increase.webp` plus JSON | 2048×1024 sheet; 256×256 frames | WebP RGBA, transparent additive-safe | charge, burst, tier-change, settle | Full-board Container overlay during `multiplierIncrease`; update badge only at the tier-change frame. |

JSON sprite data should use TexturePacker-compatible frame rectangles, anchors, durations in milliseconds, and named animation arrays. Provide a static first-frame PNG fallback for review tooling. Do not bake win values, multiplier numbers, or localized text into effects; PixiJS renders those from event data.
