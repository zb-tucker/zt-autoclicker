# Technical Implementation Details

## Architecture Overview

```
MouseClicker.exe
├── Tkinter GUI Interface (mouse_clicker.py)
├── ClickExecutor Backend (threading)
├── Windows API Direct Calls (ctypes)
└── Profile Manager (JSON)
```

## Performance & Resource Efficiency

### Why This Is Lightweight

1. **Direct Windows API Calls via ctypes**
   - No external DLLs or dependencies
   - Direct calls to: `user32.SetCursorPos()` and `user32.mouse_event()`
   - Minimal overhead compared to high-level mouse libraries

2. **Minimal Memory Usage**
   - tkinter GUI: ~10-15 MB
   - Background threads: <1 MB each
   - Total baseline: ~25-30 MB

3. **Low CPU Usage**
   - Threads sleep between clicks
   - No busy-waiting loops
   - CPU only active during cursor movement and clicks

4. **Simple Profile Format**
   - Plain JSON files
   - No database or complex storage
   - Easy to backup and edit manually

## Threading Model

### Sequence Mode
```python
Main Thread (GUI)
    ↓
ClickExecutor Thread
    → Click 1
    → Sleep interval
    → Click 2
    → Sleep interval
    → Click 3
    → (repeat based on iterations)
```

### Independent Mode
```python
Main Thread (GUI)
    ↓
ClickExecutor Thread
    ├─ Click Handler 1 (separate thread)
    │   → Click at location 1
    │   → Sleep interval
    │   → (repeat)
    │
    ├─ Click Handler 2 (separate thread)
    │   → Click at location 2
    │   → Sleep interval
    │   → (repeat)
    │
    └─ Click Handler N (separate thread)
        → Click at location N
        → Sleep interval
        → (repeat)
```

## Windows API Direct Calls

### Mouse Position
```python
windll.user32.SetCursorPos(x, y)  # Move cursor
windll.user32.GetCursorPos(...)   # Get cursor position
```

### Mouse Events
```python
# Left click
windll.user32.mouse_event(2, 0, 0, 0, 0)  # Down
windll.user32.mouse_event(4, 0, 0, 0, 0)  # Up

# Right click
windll.user32.mouse_event(8, 0, 0, 0, 0)  # Down
windll.user32.mouse_event(16, 0, 0, 0, 0) # Up

# Double click
# (Left down + up + down + up)
```

**Constants:**
- 2 = MOUSEEVENTF_LEFTDOWN
- 4 = MOUSEEVENTF_LEFTUP
- 8 = MOUSEEVENTF_RIGHTDOWN
- 16 = MOUSEEVENTF_RIGHTUP

## Global Hotkey Detection

Uses the `keyboard` library for cross-platform hotkey detection:
- Runs in background daemon thread
- Non-blocking
- Detects hotkey press and toggles start/stop

## Profile Storage Format

Each profile is a JSON file:

```json
{
  "hotkey": ".",
  "mode": "sequence",
  "iterations": -1,
  "clicks": [
    {
      "x": 960,
      "y": 540,
      "type": "left",
      "interval": 1.0
    },
    {
      "x": 100,
      "y": 100,
      "type": "double",
      "interval": 2.5
    }
  ]
}
```

## Build Process

### PyInstaller Configuration
- **--onefile**: Single executable (no external files needed)
- **--windowed**: No console window
- **--icon=NONE**: Default Windows icon
- Result: ~11 MB standalone .exe (includes Python runtime)

### Dependencies Bundled
- Python 3.13 runtime
- tkinter (built-in with Python)
- keyboard library
- ctypes (Python standard library)

## Code Structure

### Main Components

1. **Windows API Layer** (Lines 10-40)
   - `get_cursor_position()` - Get current cursor position
   - `set_cursor_position(x, y)` - Move cursor
   - `mouse_click(type)` - Perform click action

2. **Configuration Management** (Lines 49-75)
   - `load_profile()` - Load saved profile
   - `save_profile()` - Save current settings
   - `get_default_config()` - Default settings

3. **Click Executor** (Lines 84-147)
   - Core logic for click automation
   - Handles both sequence and independent modes
   - Manages iterations and thread control

4. **Tkinter GUI** (Lines 156-430)
   - Main application window
   - Profile management UI
   - Click list editor
   - Hotkey configuration

5. **Click Dialog** (Lines 432-498)
   - Modal dialog for adding/editing clicks
   - Position capture functionality

## Performance Benchmarks

Typical resource usage while running:

| Metric | Value |
|--------|-------|
| Memory (idle) | ~25 MB |
| Memory (running) | ~28-30 MB |
| CPU (idle) | <1% |
| CPU (clicking) | 1-3% |
| Executable size | 11 MB |

## Why No Admin Rights Are Required

Mouse input automation at the API level doesn't require elevated permissions. The Windows API calls used are standard user-level operations. Admin would only be needed for:
- Registry access
- System-wide input interception (not needed here)
- Device driver level access (not needed)

## Potential Improvements

If you wanted to optimize further:

1. **Compile to Native C**
   - Replace Python GUI with native C++ UI
   - Direct WinAPI mouse control (same as current implementation)
   - Reduce executable to ~1-2 MB
   - Eliminate Python runtime dependency

2. **Reduce Executable Size**
   - Use UPX compression (PyInstaller --upx option)
   - Further compress to ~6-8 MB
   - Trade-off: slight startup delay due to decompression

3. **Reduce Memory**
   - Currently at theoretical minimum for Python-based solution
   - Native C would reduce to ~5-10 MB

4. **Custom Hotkey Library**
   - Replace `keyboard` library with custom Windows API hotkey
   - Minimal savings (~2 MB)

## Security & Safety Notes

- **No internet connectivity** - Everything is local
- **No telemetry** - Runs offline
- **No admin exploits** - Uses standard APIs only
- **Profile files are plain JSON** - Human-readable, easily auditable
- **Open source** - Review the Python source code anytime

## Modifying the Source

If you want to customize the application:

1. Edit `mouse_clicker.py`
2. Test with: `python mouse_clicker.py`
3. Rebuild .exe: `python build_exe.py`

Common customizations:
- Change default hotkey (search for `'.'`)
- Add more profiles (modify UI)
- Change UI colors/fonts (tkinter styles)
- Add new click types (modify `mouse_click()` function)

---

**Last Updated:** January 4, 2026
**Python Version:** 3.13
**Dependencies:** keyboard, PyInstaller (build-time only)
