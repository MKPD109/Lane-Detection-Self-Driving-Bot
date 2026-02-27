# GTA5 Lane Detection Self-Driving Bot

A computer vision project that turns **Grand Theft Auto V into a self-driving simulation environment**. The bot captures the GTA5 game window in real time, uses classical image processing to detect road lane markings, and autonomously steers the vehicle by simulating DirectInput keyboard presses — no machine learning required.

> Built as a simulation platform to explore and develop autonomous lane-keeping algorithms using a real-world-like driving environment.

---

## Demo

| Processed View | Original View |
|---|---|
| Edge-detected road with Hough lines (blue) | Raw GTA5 frame with detected lanes overlaid (red) |

Both views are displayed live while the bot runs.

---

## File Structure

```
/
├── main.py           # Self-driving bot — full lane detection + autonomous steering
├── debugdrive.py     # Debug mode — detection only, prints decisions, no key input
├── directkeys.py     # Windows DirectInput keyboard simulation module
└── archive/          # All development history, prototypes, and experiments
```

---

## How the Self-Driving Works

The bot operates in a continuous loop — capture → process → detect → steer — at real-time frame rates.

```
GTA5 Screen
     │
     ▼
Screen Capture (mss)
     │
     ▼
Grayscale → Canny Edge Detection → Gaussian Blur
     │
     ▼
ROI Mask (road polygon only)
     │
     ▼
Hough Line Transform (detect lane segments)
     │
     ▼
Lane Grouping & Averaging (left lane + right lane)
     │
     ▼
Slope Analysis (m1, m2)
     │
     ├── Both negative  →  Steer RIGHT (D key)
     ├── Both positive  →  Steer LEFT (A key)
     └── Mixed          →  Go STRAIGHT (W key)
```

---

### Stage 1 — Screen Capture
`mss` captures an `800x600` pixel region of GTA5's game window at position `(0, 40)` on screen. The 40px offset skips the Windows title bar. Frames are converted to NumPy arrays for OpenCV.

> `mss` was selected over `pyautogui` following benchmarking — it delivers significantly higher FPS for real-time capture. See [`archive/ARCHIVE_DOCUMENTATION.md`](archive/ARCHIVE_DOCUMENTATION.md) for benchmark results.

---

### Stage 2 — Image Processing
Each frame is processed through a pipeline specifically tuned for GTA5's road visuals at `800x600`:

| Step | Settings | Why |
|---|---|---|
| Grayscale | — | Lane markings are identifiable by contrast, not colour |
| Canny edge detection | Thresholds: `150 / 300` | Picks up GTA5's road markings and lane edges cleanly |
| Gaussian blur | Kernel: `3x3` | Suppresses noise from GTA5's road surface textures |
| ROI polygon mask | 6-point hexagon | Isolates the driveable road ahead; removes sky, buildings, and bonnet |
| Hough Line Transform | `rho=1, theta=π/180, threshold=180` | Detects straight line segments representing lane markings |

**ROI Polygon** (tuned for GTA5's road perspective at `800x600`):
```python
vertices = [[10,500], [28,360], [350,320], [450,320], [750,360], [800,500]]
```
This mask focuses exclusively on the stretch of road immediately ahead of the vehicle, ignoring everything above the vanishing point and outside the lane area.

---

### Stage 3 — Lane Detection (`draw_lanes`)
Raw Hough line segments are noisy — GTA5's road textures produce many short fragments. The algorithm consolidates them into two clean lane lines:

1. **Slope & intercept calculation** — Each line segment's equation (`y = mx + c`) is computed using least squares regression.
2. **Line grouping** — Segments with slopes and intercepts within ~20% of each other are merged into a single group. This clusters the fragments of one lane line together.
3. **Dominant lane selection** — The two groups with the most members are chosen as the left and right lane.
4. **Averaging** — All segments in each group are averaged into a single smooth, continuous line drawn in red on the GTA5 frame.
5. **Slope export** — The slope values `m1` and `m2` are passed to the steering controller.

---

### Stage 4 — Autonomous Steering
The self-driving decision is made purely from the slope signs of the two detected lanes:

| Left Lane Slope (`m1`) | Right Lane Slope (`m2`) | Decision | Steering Input |
|---|---|---|---|
| Negative | Negative | Car drifting **left** — correct right | Press **D** |
| Positive | Positive | Car drifting **right** — correct left | Press **A** |
| Mixed (one each) | Mixed (one each) | Car is **centred** — hold straight | Press **W** |

When both lane slopes point the same direction, the car has drifted off-centre and the bot corrects. When they diverge as expected (left lane leaning left, right lane leaning right), the car is centred in the lane and the bot holds forward.

---

### Stage 5 — DirectInput Keyboard Simulation (`directkeys.py`)
Steering inputs are injected into GTA5 using the **Windows DirectInput API** via `ctypes.windll.user32.SendInput`. Standard Windows `keybd_event` calls are **silently ignored by GTA5** — DirectInput scan codes are mandatory for the game to register keyboard input from external programs.

| GTA5 Control | Key | DirectInput Scan Code |
|---|---|---|
| Accelerate / hold straight | `W` | `0x11` |
| Steer left | `A` | `0x1E` |
| Steer right | `D` | `0x20` |

---

## GTA5 Configuration

For reliable self-driving performance, configure GTA5 as follows before running the bot:

| Setting | Required Value |
|---|---|
| Display mode | **Windowed** (not exclusive fullscreen — `mss` cannot capture it) |
| Resolution | **800 x 600** |
| Window position | **Top-left corner** of screen (no offset) |
| Camera angle | **Default forward-facing** (hood or bumper cam) |
| Weather | **Clear / sunny** for best lane visibility |
| Time of day | **Daytime** recommended |
| Controls | **Keyboard** — W/A/S/D driving enabled |

---

## Requirements

- **OS:** Windows only (`ctypes.windll` and DirectInput are Windows-specific)
- **GTA5:** PC version (Steam / Rockstar Launcher)
- **Python:** 3.x

Install dependencies:
```bash
pip install opencv-python numpy mss
```

---

## Running the Bot

### Step 1 — Validate with Debug Mode First
Always start with `debugdrive.py`. This runs the full lane detection pipeline and prints what the bot *would* do, without pressing any keys in GTA5:

```bash
python debugdrive.py
```

Console output example:
```
-0.823 0.651 straight
-1.204 -0.934 right
0.712 0.889 left
FPS: 28.4
```

Watch the OpenCV windows to verify the red lane lines are correctly tracking the road. Only proceed to the full bot once detection looks stable.

### Step 2 — Run the Self-Driving Bot
```bash
python main.py
```

The bot will now autonomously steer the GTA5 vehicle in real time. Press **ESC** in the OpenCV window to stop.

---

## Display Windows

| Window | Content | Use For |
|---|---|---|
| **"Processed"** | Edge-detected, ROI-masked image with Hough line segments in blue | Diagnosing detection issues — too many/few lines, ROI shape |
| **"Original"** | Raw GTA5 frame with two averaged lane lines in red | Confirming correct lane tracking on the road |

---

## Performance & Road Type Compatibility

| Road Type | Performance | Notes |
|---|---|---|
| Highway / motorway | Excellent | Clear lane markings, straight stretches — ideal |
| Urban main roads | Good | Works on most roads with visible white markings |
| Tight bends | Moderate | Fixed ROI may partially miss heavily curved lanes |
| Intersections | Poor | Multiple crossing lines confuse lane grouping |
| Night / rain | Reduced | Lower visibility; try reducing Canny thresholds to `100/200` |
| Dirt tracks / off-road | Not supported | No lane markings to detect |

---

## Tuning Parameters

All tunable values are in `process_img()` inside `main.py` and `debugdrive.py`:

| Parameter | Location | Effect |
|---|---|---|
| Canny thresholds `(150, 300)` | `cv2.Canny(...)` | Lower values detect more edges (noisier); higher values detect fewer (cleaner) |
| Blur kernel `(3, 3)` | `cv2.GaussianBlur(...)` | Larger kernel smooths more noise but may blur real edges |
| ROI vertices | `vertices = np.array(...)` | Reshape the detection zone for different camera angles or resolutions |
| Hough threshold `180` | `cv2.HoughLinesP(...)` | Higher value requires more votes per line (fewer, stronger detections) |

After any change, validate with `debugdrive.py` before running `main.py`.

---

## Known Limitations
- The ROI and capture coordinates are hardcoded for **800x600**. A different resolution requires full recalibration.
- Steering is **binary per frame** — there is no proportional or PID control, so the bot may oscillate slightly on very straight roads.
- The bot detects **lane lines only** — it has no awareness of traffic, obstacles, or road signs.
- `directkeys.py` is **Windows-only** and will not run on macOS or Linux.

---

## Development History
All prototypes, benchmarking experiments, ROI calibration tools, and development notes are documented in:

📁 [`archive/ARCHIVE_DOCUMENTATION.md`](archive/ARCHIVE_DOCUMENTATION.md)
