# Artwork pipeline

Godot normally imports an SVG as a texture. That alone does **not** provide tappable vector paths. Prism Bloom compiles closed SVG regions into polygons ahead of time, then instances `region.tscn` for each polygon. This is geometric region filling, not raster flood fill.

1. Draw in a `0 0 600 600` SVG viewBox. Use explicit flat six-digit hex fills, closed shapes, and stable unique IDs.
2. Apply transforms and convert strokes/text to supported contours in your vector editor. Split compound shapes and holes into separate simple regions. Avoid completely covered regions.
3. Run `tools/import_svg.py input.svg output.json [--cluster 8]`.
4. Inspect the generated preview and run the geometry tests in Godot. Labels are placed in the visible interior, with occlusion considered; the compiler records label clearance for zoom-aware readability.
5. Create `resources/levels/<id>.tres` using the `ArtworkData` script. Assign title, category, difficulty, time estimate, unlock threshold, JSON path, and preview texture. Add the ID to the catalog list in `autoload/progress.gd`.

## Supported SVG subset

- Closed paths using absolute/relative `M L H V C Q Z`, polygons, circles, ellipses.
- Cubic and quadratic curves are sampled into 16 segments per curve. The runtime draws antialiased polygon meshes and outlines; the original paths remain editable.
- Similar colors cluster by RGB Euclidean distance; exact colors stay distinct at the default threshold of zero.
- One closed contour per path; no holes, arcs, transforms, external styles, filters, gradients, or inherited fills in source geometry. Unsupported input fails explicitly. Presentation previews can use gradients separately.

Concave regions are supported. Intersecting/self-intersecting paths must be cleaned by the artist. Runtime triangulation and visible label tests protect the shipped library. Very thin regions may have hidden numbers at fit scale; zoom or use a hint to find them.

## Rebuilding the included assets

These tools are optional; all outputs are already committed.

```bash
python3 tools/create_content.py
python3 tools/create_previews.py
godot4 --headless --editor --import --quit
```

`create_content.py` regenerates the original illustration families, numbered data, resources, icons and synthesized audio. `create_previews.py` adds painted radial gradients to presentation SVGs without changing puzzle geometry. Stable shape IDs preserve saves only while the artwork's region topology is unchanged. Give a substantially revised puzzle a new artwork ID.

`tools/build_scenes.py` records the initial scene authoring recipe. It is **not a runtime scene builder** and is not part of setup. Prefer editing the checked-in `.tscn` scenes in Godot; rerunning that tool overwrites those layouts.

## Runtime architecture

`Gallery.art_selected` → main navigation → `Game.start(ArtworkData)` → `ColoringBoard.load_art`.

The board transforms local input into artwork coordinates, checks regions from front to back, and emits a signal only for a correct unfilled match. Game updates the palette and `Progress`. Regions own their polygon, outline, label, shade material, and fill animation. Zoom retains the point under the fingers, clamps scale/pan, and suppresses fills after dragging or pinching.

`Progress` writes JSON to `user://progress.json.tmp`, closes it, then renames it over the prior save. Save IDs are sanitized against the catalog on load. Corrupt JSON is copied to `.corrupt` for recovery. Settings and completion rewards share this data; no personal information is stored.

The reward screen replays the recorded region-fill order through the same reusable region scene. Live processes and editor caches are not required in the downloaded project.
