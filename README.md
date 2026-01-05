# Mouse Clicker - Lightweight Click Automation

A minimal-resource Windows mouse automation tool with a simple tkinter GUI. Uses direct Windows API calls via ctypes for maximum efficiency.

## Features

- ✓ **Click Sequence Mode**: Execute clicks one after another with specific intervals
- ✓ **Independent Mode**: Run multiple click locations simultaneously with independent timers
- ✓ **Flexible Click Types**: Left-click, right-click, or double-click
- ✓ **Profile Management**: Save/load 2 named profiles (no auto-save)
- ✓ **Global Hotkey**: Configurable start/stop toggle (default: `.`)
- ✓ **Iteration Control**: Run indefinitely or specify exact number of iterations
- ✓ **Minimal Resource Usage**: Direct Windows API calls, minimal memory/CPU overhead
- ✓ **No Admin Required**: Works in user mode
- ✓ **Silent Operation**: Runs without logging or notifications

## Installation & Building

### Option 1: Quick Start (Run from Python)

1. **Install dependencies:**
   ```powershell
   pip install keyboard
   ```

2. **Run the application:**
   ```powershell
   python mouse_clicker.py
   ```

### Option 2: Build Standalone Executable

1. **Install build dependencies:**
   ```powershell
   pip install PyInstaller keyboard
   ```

2. **Build the .exe:**
   ```powershell
   python build_exe.py
   ```

3. **Find the executable:**
   - Located in: `./dist/MouseClicker.exe`
   - This is a standalone file (no Python installation needed to run it)

## Usage

### Basic Workflow

1. **Add Clicks**: Click "Add Click" to define where and how to click
   - Enter X, Y coordinates
   - Choose click type (left, right, double)
   - Set interval (seconds between this click and the next)
   - Use "Get Current Position" to capture your cursor position

2. **Configure Mode**:
   - **Sequence**: Clicks execute one after another in order
   - **Independent**: Each click runs on its own timer simultaneously

3. **Set Iterations**:
   - `-1` = Run forever (until you press stop hotkey)
   - `5` = Run the sequence/timers 5 times

4. **Set Hotkey**:
   - Default: `.` (period/dot key)
   - Change by typing a new key and clicking "Set Hotkey"
   - Press the hotkey to toggle start/stop

5. **Save/Load Profiles**:
   - Switch between "Profile 1" and "Profile 2"
   - Click "Save" to save current settings (manual only)
   - Click "Load" to restore saved settings
   - Settings are NOT auto-saved

6. **Start/Stop**:
   - Click "Start" button or press your hotkey
   - Click "Stop" button or press your hotkey again

### Example Scenarios

**Auto-Clicker (Same Location):**
- Add one click with high interval (e.g., 2.0 seconds)
- Set mode to "Sequence"
- Set iterations to -1
- Press hotkey to start

**Multi-Location Automation:**
- Add multiple clicks at different coordinates
- **Sequence mode**: Each location is clicked in order with specified intervals
- **Independent mode**: Each location is clicked simultaneously with its own timer

**Limited Runs:**
- Set iterations to a specific number (e.g., 10)
- Clicker will perform 10 complete cycles then stop automatically

## Profile Storage

Profiles are saved to: `C:\Users\<YourUsername>\.mouse_clicker\`

- `Profile 1.json` - First named profile
- `Profile 2.json` - Second named profile

Format (JSON):
```json
{
  "hotkey": ".",
  "mode": "sequence",
  "iterations": -1,
  "clicks": [
    {
      "x": 500,
      "y": 300,
      "type": "left",
      "interval": 1.0
    }
  ]
}
```

## Technical Details

### Resource Efficiency

- **Direct Windows API**: Uses ctypes to call `SetCursorPos()` and `mouse_event()` directly
- **No External DLLs**: Everything is built-in to Windows
- **Minimal Memory**: tkinter GUI is lightweight, background execution threads are minimal
- **Low CPU**: Sleeping between clicks, only active during clicks

### No Admin Required

Standard mouse control doesn't require elevation. The app runs in user mode.

### Hotkey Detection

Uses the `keyboard` library to detect global hotkey presses without blocking the GUI.

## Troubleshooting

**"Build failed" when creating .exe:**
- Ensure PyInstaller is installed: `pip install PyInstaller`
- Try rebuilding: `python build_exe.py`

**Hotkey not working:**
- Ensure the `keyboard` library is installed: `pip install keyboard`
- Try using a single character hotkey
- Some special keys may not be supported; use common keys (letters, numbers, symbols)

**Clicks not happening:**
- Verify click coordinates are visible on your screen
- Check that the correct click type is selected
- Ensure the application window is not preventing mouse input

**High CPU/Memory with many clicks:**
- In independent mode, each click spawns a thread; limit to <10 simultaneous clicks
- In sequence mode, only one click happens at a time (more efficient)

## Hotkey Examples

Common keys to use:
- `.` (period) - Default, rarely used
- `;` (semicolon)
- `'` (quote)
- `` ` `` (backtick)
- `f9`, `f10`, `f11`, `f12` (function keys)
- `+` (plus)
- `-` (minus)

## Standalone Executable Size

The .exe is typically 50-80MB (includes Python runtime). This is normal for PyInstaller bundles.

To reduce size, you could compile to native C (but this project uses Python for cross-platform hotkey support).

---

**No warranty provided. Use responsibly. This tool automates mouse input - be careful with active iterations to avoid unintended actions.**
