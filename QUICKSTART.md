# Quick Start Guide - Mouse Clicker

## What You Have

- **MouseClicker.exe** - Standalone executable (no Python installation needed)
- **mouse_clicker.py** - Source code (if you want to modify it)
- **build_exe.py** - Build script (to rebuild the .exe if you modify the source)
- **README.md** - Full documentation

## First Run

1. Double-click **MouseClicker.exe**
2. A window will appear with the click configuration interface

## Basic Usage in 5 Minutes

### 1. Add Your First Click
- Click **"Add Click"** button
- Use **"Get Current Position"** to capture where your cursor is
- Choose click type: Left, Right, or Double
- Set interval (time in seconds before next click)
- Click **"OK"**

### 2. Set Click Mode
- **Sequence**: Clicks happen one after another
- **Independent**: Each click runs on its own timer simultaneously

### 3. Configure Iterations
- `-1` = Run forever
- `5` = Run the sequence 5 times

### 4. Set Hotkey (Optional)
- Default hotkey is `.` (period key)
- Change it by typing a new key and clicking "Set Hotkey"

### 5. Start Clicking
- Click **"Start"** button or press your hotkey
- Click **"Stop"** or press hotkey again to stop

## Saving Profiles

If you want to save your configuration:
1. Set up all your clicks
2. Click **"Save"** button
3. Your settings are saved to Profile 1 or Profile 2 (whichever is selected)
4. Next time, click **"Load"** to restore your settings

**Note:** Settings are NOT auto-saved. Click "Save" only when you want to keep them.

## Common Examples

### Simple Auto-Clicker (One Location)
1. Add 1 click at your target location
2. Set interval to 1.0 seconds
3. Mode: Sequence
4. Iterations: -1
5. Click Start

### Multi-Point Clicker (A → B → C → Repeat)
1. Add Click 1 at location A, interval 1.0s
2. Add Click 2 at location B, interval 1.0s
3. Add Click 3 at location C, interval 1.0s
4. Mode: Sequence
5. Iterations: -1
6. Click Start

### Simultaneous Clicks (Multiple locations at same time)
1. Add Click 1 at location A, interval 2.0s
2. Add Click 2 at location B, interval 2.0s
3. Mode: Independent
4. Iterations: -1
5. Click Start
(Both locations click every 2 seconds, in parallel)

## File Locations

Your saved profiles are stored at:
```
C:\Users\<YourUsername>\.mouse_clicker\
```

- `Profile 1.json` - First profile
- `Profile 2.json` - Second profile

You can back these up if you want to preserve your configurations.

## Troubleshooting

**Hotkey not working?**
- Ensure the keyboard library is installed (included with the .exe)
- Try using a single character (letters, numbers, symbols work best)

**Clicks not happening?**
- Check that coordinates are on-screen
- Verify correct click type is selected
- Ensure the window is not blocking input

**CPU/Memory usage high?**
- Reduce the number of simultaneous clicks in independent mode
- Use sequence mode for many clicks (more efficient)

## Safety Tips

⚠️ **Be careful!** This tool automates mouse clicks:
- Always have a way to interrupt (your hotkey)
- Test with iterations set to a small number first (e.g., 5)
- Make sure the target application window is visible
- Don't close the MouseClicker window while it's running

---

That's it! You're ready to automate your mouse clicks. For more detailed information, see README.md.
