# Archive Documentation

This folder contains all historical and experimental files from the development of the lane detection driving bot. It covers four areas: early image processing experiments, performance benchmarking of screen capture libraries, iterative prototyping of the full bot, and visual calibration tools for the ROI polygon.

---

## Folder Structure

```
archive/
├── edge and blur experiment/
│   ├── gaussian_blur2.py
│   ├── gaussian_blur_cv.py
│   ├── cannymethod.py
│   └── blur.py
│
├── Screen Capture Benchmark/
│   ├── sc_pyautogui.py
│   ├── sc_mss.py
│   ├── screen_capture.py
│   ├── screen_capture_process.py
│   ├── screen_cap_mss.py
│   ├── screen_cap_mss_process.py
│   └── avg_test/
│       ├── sc_mss_avg.py
│       └── sc_pyautogui.py
│
├── Prototype/
│   ├── c-type_control.py
│   ├── template1.py
│   ├── test1.py
│   ├── test2.py
│   ├── test3.py
│   ├── test5.py
│   ├── processing.py
│   ├── roi_process.py
│   ├── main_lane_dection_process.py
│   ├── lanedetect.py
│   ├── test_driving1.py
│   └── updated_lanedetect.py
│
└── Calibration & Utilities Tools/
    ├── plot_roi_flat.py
    └── plot_roi_slope.py
```

---

## `edge and blur experiment/`

These four scripts represent the very first stage of the project — isolated experiments to understand and test image processing techniques before any game integration. No screen capture or key input is involved here; these scripts operate on static images or the live screen only.

### `gaussian_blur2.py`
The earliest experiment in the set. This script implements Gaussian blur **from scratch** using only NumPy and PIL, without OpenCV. It manually constructs a Gaussian kernel and applies it to a grayscale image via convolution. This was written to deeply understand how Gaussian blur works mathematically before relying on library functions. It loads a hardcoded image from a local path and saves the blurred output as a new file.

> **Key learning:** How a Gaussian kernel is constructed and how convolution smooths an image by averaging neighbouring pixels weighted by distance.

### `gaussian_blur_cv.py`
A direct follow-up to `gaussian_blur2.py`. Having understood the math, this script replaces the manual implementation with OpenCV's `cv2.GaussianBlur()`. It loads a static image, applies the blur with a `(5, 5)` kernel, and displays the result. This was a validation step to confirm OpenCV produces the same visual outcome far more efficiently.

> **Key learning:** Confirmed that `cv2.GaussianBlur` is the practical tool to use going forward.

### `cannymethod.py`
Experiments with Canny edge detection on a static image file. It loads a pre-blurred image (the output of `gaussian_blur2.py`), converts it to grayscale, and runs `cv2.Canny()` with thresholds of `100` and `250`. The result is displayed in an OpenCV window. This was the first test to see if road-like edges could be detected from a still image.

> **Key learning:** Canny edge detection successfully highlights structural edges, and threshold values significantly affect how much detail is retained.

### `blur.py`
The first experiment to move from static files to **live screen capture**. It uses `mss` to grab an `800x600` region of the screen in real time and applies a heavy `(9, 9)` Gaussian blur — notably, without any edge detection. The blurred output is displayed in a live window with FPS reporting. This was purely a test to confirm screen capture was working and to observe what heavy blurring does to a live game image.

> **Key learning:** Validated that `mss` could capture the game screen reliably and that real-time display with OpenCV was feasible.

---

## `Screen Capture Benchmark/`

This folder exists entirely to answer one engineering question: **is `pyautogui` or `mss` faster for screen capture?** Since the bot needs to process frames in real time, the capture method's speed directly impacts how responsive the steering can be. Every file in this folder is a controlled variation of the same loop — capture a frame, optionally apply edge detection, display it, and report FPS — with only the capture library or processing step changing between files.

### `sc_pyautogui.py`
The baseline `pyautogui` capture test with **no image processing**. Captures an `800x640` region, performs a BGR→RGB colour conversion (required because `pyautogui` returns RGB while OpenCV expects BGR), displays the raw frame, and prints FPS every second. This establishes the raw capture speed of `pyautogui` with minimal overhead.

> **What it measures:** Raw `pyautogui` capture FPS with colour conversion only.

### `sc_mss.py`
The equivalent baseline for `mss` — captures an `800x640` region and displays the raw frame with no processing at all (no colour conversion, no edge detection). The simplest possible capture loop. This establishes the raw ceiling speed of `mss`.

> **What it measures:** Raw `mss` capture FPS with zero processing overhead.

### `screen_capture.py` / `screen_capture_process.py`
Both files are **identical** — `pyautogui` capture with Canny edge detection (`100/200` thresholds) applied to each frame before display. They appear to be duplicates, possibly created accidentally or saved at different points in the same session. The name `screen_capture_process.py` implies it was intended to be the "with processing" version of `screen_capture.py`, but no difference exists in the code.

> **What it measures:** `pyautogui` capture FPS with edge detection overhead added. Comparing this against `sc_pyautogui.py` isolates the cost of the Canny operation itself.

### `screen_cap_mss.py`
`mss` capture with Canny edge detection, capturing a **600px tall** region (`800x600`) rather than 640px. This is the `mss` counterpart to `screen_capture.py`. The slight height difference (`600` vs `640`) suggests this was also being tuned to match the game's actual resolution.

> **What it measures:** `mss` capture FPS with edge detection at the final target resolution (`800x600`).

### `screen_cap_mss_process.py`
Virtually identical to `screen_cap_mss.py` but reverts the capture height back to `640`. Likely a transitional copy made while deciding on the final capture dimensions. No other differences exist.

> **What it measures:** Same as `screen_cap_mss.py` — `mss` + Canny — but at `800x640`.

### `avg_test/` subfolder

The scripts above only report FPS per second, which fluctuates. To get a more reliable comparison between the two libraries, a dedicated subfolder was created with scripts that run for a **fixed 90-second window** and compute a single average FPS at the end.

**`avg_test/sc_mss_avg.py`** — Runs the `mss` raw capture loop (no edge detection) for exactly 90 seconds, counting every frame. At the end it prints the average FPS calculated as `total_frames / 90`.

**`avg_test/sc_pyautogui.py`** — The `pyautogui` counterpart. Runs for 90 seconds with colour conversion applied each frame and prints an average FPS at the end. Note that its average is calculated slightly differently — it sums per-second FPS readings and divides by 90, rather than counting total frames. This is a minor methodological inconsistency but doesn't meaningfully affect the comparison.

The outcome of this benchmarking is visible in the project itself: **`mss` was chosen** for all subsequent prototype and final versions. The `pyautogui`-based scripts were abandoned after `test1.py` in the Prototype folder, confirming that `mss` delivered meaningfully higher FPS for the real-time demands of the bot.

---

## `Prototype/`

These files represent the iterative development of the full bot, progressing from basic screen capture to a working lane-aware driving system. They roughly follow a chronological order and each one builds on or refactors the previous.

### `c-type_control.py`
The simplest file in the entire archive. It contains nothing but a call to `PressKey(W)` using `directkeys.py`, with no release or loop. This was an isolated test to verify that the DirectInput keyboard simulation was working correctly and could send keystrokes to the game at all.

> **Purpose:** Proof-of-concept for Windows DirectInput key control.

### `test1.py`
The first attempt at combining screen capture with edge detection. It uses `pyautogui` (not `mss`) for screen capture and `cv2.Canny()` with thresholds of `100` and `200` to detect edges on each live frame. There is no ROI masking, no lane grouping, and no key input — just raw edge detection displayed in a window. It also uses the `keyboard` library to detect a `q` key press for exiting.

> **Notable difference from final version:** Uses `pyautogui` instead of `mss`, which is slower. No game control. No ROI.

### `test2.py`
Switches from `pyautogui` to `mss` for screen capture and introduces the full classic processing pipeline: grayscale → Canny (`200/300`) → Gaussian blur `(5,5)` → ROI masking → Hough transform → `draw_lines()`. However, it draws **all detected Hough lines** directly onto the processed image without any grouping or lane averaging. It also begins holding `W` via `PressKey(KeyCodes.W.value)` on every frame, making it the first script that actually interacts with the game while running. Uses the older `directkey` (enum-based) import style.

> **Purpose:** First version with a real pipeline and live game interaction.

### `test3.py`
Nearly identical to `test2.py` but with one meaningful change: the Gaussian blur kernel is reduced from `(5,5)` to `(3,3)`. The `draw_lines()` function also gains a `try/except` wrapper to silently handle missing lines. This suggests a tuning pass to test whether a smaller blur kernel improved edge quality.

> **Key difference from test2:** Smaller blur kernel; more robust error handling in line drawing.

### `template1.py`
A significant step forward. This is the first prototype to include the full `draw_lanes()` function with slope grouping and lane averaging — the core algorithm that eventually made it into the final bot. It uses `PIL.ImageGrab` instead of `mss` for screen capture and draws the two averaged lanes in **green** on the original image. There is no key input. The lane grouping tolerance here uses `1.2x / 0.8x` for both slope and intercept comparisons.

> **Purpose:** First working demo of the full lane detection algorithm. No game control yet.

### `test5.py`
Effectively a cleaned-up copy of `template1.py` with no functional changes — same `PIL.ImageGrab` capture, same `draw_lanes()` logic, same green lane rendering. The main difference is stylistic tidying and the removal of some comments. Likely created as a cleaner working copy to build on.

> **Relation to template1:** Functionally identical; cosmetic cleanup only.

### `processing.py`
Reverts the lane detection to a simpler approach — no `draw_lanes()`, just raw Hough lines drawn in blue onto the original frame. It uses `mss` for capture and holds `W` continuously via `PressKey(KeyCodes.W.value)`. This appears to be a side branch — possibly created to isolate and debug the raw line output without the lane averaging logic getting in the way.

> **Purpose:** Debugging / regression — strip back to raw Hough lines while keeping game input active.

### `roi_process.py`
Focuses specifically on refining the **Region of Interest polygon**. The `process_img()` function applies the full pipeline but returns after the ROI masking step — it does **not** run the Hough transform or draw any lanes. The ROI vertices here are slightly different from other prototypes: `[[10,500],[60,360],[350,320],[450,320],[740,360],[800,500]]`, indicating active experimentation with the mask shape. The `draw_lanes()` function is present but unused in the main loop.

> **Purpose:** Visual tuning of the ROI polygon shape before reintegrating lane detection.

### `main_lane_dection_process.py`
Combines the `mss`-based capture with the full Canny → blur → ROI → Hough pipeline and draws raw Hough lines in blue on the original frame. No `directkeys` import and no game control at all. This is essentially a **pure computer vision sandbox** — the most self-contained script for testing detection quality without any bot behaviour getting in the way.

> **Purpose:** Clean visual debugging of the full image processing pipeline with no control side effects.

### `lanedetect.py`
The first prototype to combine the full `draw_lanes()` lane grouping algorithm with `mss` live capture. It imports from `directkey` (the older enum-based version) and calls `PressKey(KeyCodes.W.value)` continuously, but does **not** make any steering decisions — it just holds W. The lane grouping tolerance is wider here (`1.5x / 0.5x`) compared to the final version (`1.2x / 0.2x`), meaning more lines were allowed into the same group. The two main lanes are drawn in red.

> **Notable difference from final:** Wider grouping tolerance; no left/right steering logic yet; uses old `directkey` import.

### `test_driving1.py`
The first prototype to attempt **active steering** based on lane slopes. It returns `lane1_id` and `lane2_id` (the slope values `m1`, `m2`) from `draw_lanes()` and defines `straight()`, `left()`, `right()`, and `slow_ya_roll()` control functions. However, the script has a **syntax error** — a duplicate `except` block and a second nested `average_lane` definition inside the exception handler — meaning it never ran successfully in this state. It also still uses the older `directkey` enum-based imports.

> **Purpose:** First attempt at slope-based steering — broken/experimental, never fully functional.

### `updated_lanedetect.py`
The most complete prototype before the final version. It switches back to `directkeys` (the scan-code based imports matching the final `directkeys.py`) and defines the full set of control functions: `straight()`, `left()`, `right()`, and `Break()`. However, the steering logic in `main()` is **commented out**, and `draw_lanes()` returns coordinates before slopes (wrong unpacking order: `m1, m2, l1, l2` instead of `l1, l2, m1, m2`), which would cause a runtime error if the steering block were uncommented. A placeholder comment at the bottom notes the steering logic still needs to be properly integrated.

> **Purpose:** Near-final prototype with the correct architecture but with steering intentionally disabled pending a bug fix — which was resolved in the final `main.py`.

---

## `Calibration & Utilities Tools/`

These two scripts are **visual debugging tools** for the ROI polygon, not part of the bot's runtime. Their purpose is to let you load a real screenshot from the game and overlay the ROI polygon on top of it using Matplotlib, so you can verify the mask is correctly positioned over the road before committing the coordinates to the bot code.

Both scripts use the same final ROI vertices that appear in the main bot:
```
[[10, 500], [28, 360], [350, 320], [450, 320], [750, 360], [800, 500]]
```

### `plot_roi_flat.py`
Loads a screenshot taken on a **flat road section** (`Flat.png`) and renders the ROI polygon as a red outlined shape over the image using `matplotlib.patches.Polygon`. The polygon is drawn with no fill so the road underneath remains visible. This lets you check that the hexagonal mask correctly frames the flat road ahead without clipping the lanes or including too much sky and scenery.

> **Purpose:** Visually confirm the ROI polygon is correctly positioned on flat terrain.

### `plot_roi_slope.py`
Identical in structure to `plot_roi_flat.py` but loads a screenshot taken on a **sloped or hilly road section** (`Slope.png`). The same ROI vertices are applied, allowing a side-by-side comparison of how well a single fixed polygon covers both road geometries. Since the ROI is hardcoded and cannot adapt dynamically, this check was important to ensure the mask was not missing the lanes when the road curves upward.

> **Purpose:** Verify the ROI polygon still captures lane markings correctly on non-flat terrain.

> **Note:** Both scripts use hardcoded local Windows paths (`E:\Downloads\...`) and will need the image path updated to run on any other machine.

---

## Full Development Timeline

| Phase | Files | What Was Being Solved |
|---|---|---|
| Image processing fundamentals | `gaussian_blur2.py`, `gaussian_blur_cv.py`, `cannymethod.py` | Understanding blur and edge detection on static images |
| Live capture validation | `blur.py` | Can we capture and display the game screen in real time? |
| Capture library benchmarking | `Screen Capture Benchmark/` | Is `pyautogui` or `mss` faster? |
| Confirmed benchmark results | `avg_test/` | 90-second averaged FPS — `mss` wins |
| Pipeline construction | `test1.py` → `test3.py` | Building grayscale → Canny → blur → ROI → Hough |
| Lane algorithm development | `template1.py`, `test5.py` | Slope grouping and lane averaging |
| Debugging branches | `processing.py`, `roi_process.py`, `main_lane_dection_process.py` | Isolating individual pipeline components |
| ROI calibration | `plot_roi_flat.py`, `plot_roi_slope.py` | Visually validating the ROI polygon on real game screenshots |
| Steering integration | `lanedetect.py`, `test_driving1.py`, `updated_lanedetect.py` | Wiring slope signs to W/A/D key inputs |
| Final bot | `main.py` *(in root)* | Bug fixes, tightened tolerances, working steering |
