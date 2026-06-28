# Cathode Reliquary

*An algorithmic movement where impossible objects are resurrected as living wireframe, rendered not in pixels but in the trembling glyphs of a phosphor screen.*

---

## Manifesto

**Cathode Reliquary** is the art of preserving an impossible thing inside two nested vessels: a glass bottle that could never admit the ship it holds, and a character grid that could never truly hold three dimensions — yet does, through the patient deceit of projection. The movement takes the oldest maritime conceit, the ship folded flat and raised inside a bottle by a steady hand, and re-stages it on the most nostalgic surface in computing: the green-glowing vector terminal, where ships were once nothing but glowing edges and the whole cosmos was a lattice of lines. This is not nostalgia for its own sake. It is the recognition that a wireframe *is* a kind of impossible object — all skeleton, no skin, a body you can see straight through — and so the wireframe and the bottle-ship were always the same idea waiting to meet.

The computational soul of this work is the **reduction of solid form to luminous edge, and edge to glyph.** A true low-polygon body is generated in three dimensions — a bottle as a surface of revolution with deliberately few radial facets, a ship as a coarse hull of planks and masts and taut sails — and then *every solid intention is discarded.* Only the edges survive the projection. Those edges are walked, sampled, and quantized onto a monospace lattice, where each cell must choose a single character to represent the angle of the line passing through it: a vertical stroke becomes `|`, a shallow rise becomes `-`, the steep diagonals resolve to `/` and `\`. The glyph is not decoration; it is the lowest honest unit of direction the grid can speak. This is the meticulously crafted heart of the movement, and it must feel like the product of deep computational expertise — the kind of slope-aware rasterizer that only emerges after countless iterations of a master who refused to let a single line read as noise.

Depth is the second devotion. A phosphor screen has no color, only brightness, and so distance must be *spoken in light.* Each edge carries its averaged depth out of the projection, and that depth is binned into luminance tiers — the near gunwale of the ship burns at full phosphor saturation while the far wall of the bottle recedes into a dim, ghosted halftone. The result is a composition that reads as genuinely volumetric despite being assembled entirely from characters, because the algorithm has been painstakingly optimized to let brightness do the work that perspective alone never could. Nothing here is a flat trick. The whole scene rotates as one rigid body, and as it turns, the glyphs reshuffle continuously — `/` becoming `|` becoming `\` — a living evidence that real geometry, not a looping animation, sits behind the screen.

Seeded variation is what saves this from being a single museum piece. The seed is the **invisible hand of the bottle-maker.** It decides the proportions of the hull, the number and rake of the masts, the billow of each sail, the slosh and phase of the liquid sea-line trapped at the bottle's base, the scatter of distant pin-prick stars beyond the glass, the exact taper of the shoulder where the bottle narrows to its neck. Two seeds are two different impossible ships, each one feeling inevitable, each one feeling as though a different patient craftsman sat down for a different long evening. The randomness is never loud. It is constrained by the rules of things that float and the rules of things that are blown from glass, so that every variation remains believably *built* rather than scattered.

What must never be lost is the sense of **craftsmanship rendered in code.** This is a master-level implementation or it is nothing: the projection math clean, the line-walk anti-fracturing, the glyph selection so carefully tuned that the eye reconstructs curved glass from straight characters without ever being told to. The phosphor glow, the faint scanlines, the gentle vignette of a curved tube — these are applied with restraint, the marks of someone at the absolute top of their field who knows that the retro surface should *flatter* the geometry, never bury it. The reward is a quiet, hypnotic object: a tiny wireframe ship turning forever inside a bottle of light, drawn in a thousand small letters, looking for all the world like it took an obsessive hand many long hours to coax into being — which, in the algorithm's own compressed way, it did.

---

## Conceptual Seed (woven, not announced)

The hidden thread is the **1980s wireframe vector game** — the era when a spacecraft was a Cobra of bright edges hanging in a black void, drawn on phosphor, rotating on a docking computer's scanner. The ship-in-a-bottle is recast as *a vessel on a vector display:* the bottle is the scanner bubble / cockpit canopy, the rotation is the radar sweep, the green glow and scanlines are the cathode tube. Those who grew up on glowing wireframe ships will feel the reference in their chest without being able to name the frame; everyone else simply sees a beautiful impossible bottle made of letters. The jazz-quote is the *edge-only ship turning in a glass dome of light.*

## Algorithmic Commitments

- **Real 3D, discarded to edges.** Genuine vertex geometry, genuine rotation matrices, genuine perspective projection — then only the wireframe edges are kept and quantized to glyphs.
- **Slope-aware glyph selection.** Each lattice cell picks `| - / \ . ` by the true angle of the line crossing it. No bitmap font tricks; direction is honest.
- **Depth as luminance.** Averaged edge depth bins into phosphor brightness tiers, drawn in layered passes so the scene reads volumetric.
- **Surface-of-revolution bottle.** Low radial segment count makes the glass faceted and unmistakably *low-poly*, the facets catching the light as it turns.
- **Generative ship & sea.** Seed governs hull proportion, mast count, sail billow, the trapped liquid line's wave phase, and the field of distant stars.
- **Restrained retro surface.** Phosphor hue, bloom, scanlines, vignette — tuned to flatter the lattice, never to drown it.
