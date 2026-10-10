# Validation record

Validated on 10 October 2026 with **Godot 4.6.3 stable**, Linux x86-64, Compatibility/OpenGL renderer, and Mesa llvmpipe under Xvfb. This record covers the source project and the running game, not a native mobile release build.

## Automated checks

- **7 Python importer tests passed.** Closed cubic/quadratic/relative paths, color clustering, visible label placement, stable IDs, duplicate rejection, hidden-region rejection, and explicit rejection of unsupported paths/transforms.
- **35,493 Godot assertions passed with zero failures** in the final rendered run and a fresh-copy headless run. The count includes individual geometry/occlusion checks, not 35,493 distinct user journeys.
- **752 regions across 14 artworks** triangulated correctly, contained their label anchor, and had an anchor unobstructed by shapes drawn above them.
- Wrong-color rejection; correct fill; duplicate-fill protection; save/reload; reopening incomplete and completed work; bounded zoom/pan; focus-preserving zoom; fit; animated hints; single-touch fill; canceled touches; pinch zoom without accidental fills.
- Three full puzzles solved through the game's hit-testing route. Progress reached 100%, celebration opened, completion persisted, and the three-art milestone unlocked. Reopening did not repeat a reward. The six-art milestone remained locked at three completions.
- Category, Daily, and My Art views; setting persistence; corrupt-save preservation; stale/duplicate/invalid saved IDs; completion recalculation.
- **Window mouse routing passed in the rendered run.** This check is explicitly skipped on the headless display backend, which does not report a GUI hover target. Headless gesture and logic checks still run.
- Fresh project copy with **no `.godot` cache** imported without script/resource errors, then completed the same headless suite. This verifies the downloaded project does not depend on the original editor cache.

## Visual review

`tests/capture_screens.tscn` runs the real application scenes and captures the viewport. The committed screenshots are not mockups.

| Screen | Capture |
|---|---|
| Library and illustrated feature | [01-gallery.png](screenshots/01-gallery.png) |
| Numbered puzzle | [02-coloring.png](screenshots/02-coloring.png) |
| Partly colored puzzle | [03-in-progress.png](screenshots/03-in-progress.png) |
| Hint focus and zoom | [04-hint-zoom.png](screenshots/04-hint-zoom.png) |
| Completed artwork / reward | [05-completion.png](screenshots/05-completion.png) |
| Saved collection | [06-my-art.png](screenshots/06-my-art.png) |
| Daily selection | [07-daily.png](screenshots/07-daily.png) |
| Settings | [08-settings.png](screenshots/08-settings.png) |
| Alternate animal puzzle | [09-fox.png](screenshots/09-fox.png) |
| Tall phone layout, 390 × 844 | [10-tall-phone.png](screenshots/10-tall-phone.png) |

Reviewed and corrected: faint variable-font weights, artwork-background overflow, contrast of icons on purple buttons, corner consistency, phone letterboxing, overly sparse flower silhouettes, and clutter from tiny labels. Text is now rendered with bundled static font weights; scenery clips within frames; intricate numbers are shown when there is sufficient screen space.

The completion screen animates the saved coloring order over roughly two seconds; still screenshots show the final frame. Fill sounds and particles are exercised by normal fill handling. Audio was routed to the dummy driver in cloud graphical tests; it was not evaluated through physical speakers.

## Remaining device checks

Native Android/iOS export and installation, physical multitouch/haptics, real-device safe areas, accessibility scaling, and mobile GPU/power performance remain to be tested on hardware. An Android preset and setup instructions are provided; no APK or store submission is claimed. Xvfb reports a harmless V-Sync limitation. The unsupported optional 2D MSAA setting was removed; the game uses polygon/line antialiasing with the Compatibility renderer.
