"""
AutoClicker Application - Lightweight Mouse Automation
Windows-only, minimal resource usage via ctypes Windows API
DPI-aware coordinate handling using pynput physical coordinates
"""

import tkinter as tk
from tkinter import ttk
import json
import threading
import time
from ctypes import windll, c_int, Structure, POINTER
from pathlib import Path
import keyboard
from pynput import mouse as pynput_mouse

try:
    # Try to set per-monitor DPI awareness (Windows 8.1+)
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        # Fallback to system-wide DPI awareness (Windows Vista/7)
        windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# ============================================================================
# Windows API Direct Calls (Minimal Resource Usage)
# ============================================================================

def set_cursor_position(x, y):
    """Set cursor position (physical coordinates)"""
    windll.user32.SetCursorPos(c_int(x), c_int(y))

def mouse_click(click_type='left'):
    """
    Perform mouse click
    click_type: 'left', 'right', or 'double'
    Uses physical coordinates for consistent behavior
    """
    if click_type == 'left':
        windll.user32.mouse_event(2, 0, 0, 0, 0)  # Left down
        windll.user32.mouse_event(4, 0, 0, 0, 0)  # Left up
    elif click_type == 'right':
        windll.user32.mouse_event(8, 0, 0, 0, 0)  # Right down
        windll.user32.mouse_event(16, 0, 0, 0, 0)  # Right up
    elif click_type == 'double':
        windll.user32.mouse_event(2, 0, 0, 0, 0)  # Left down
        windll.user32.mouse_event(4, 0, 0, 0, 0)  # Left up
        windll.user32.mouse_event(2, 0, 0, 0, 0)  # Left down
        windll.user32.mouse_event(4, 0, 0, 0, 0)  # Left up

# ============================================================================
# Configuration Management
# ============================================================================

CONFIG_DIR = Path.home() / '.autoclicker'
CONFIG_DIR.mkdir(exist_ok=True)

def load_profile(profile_name):
    """Load a profile from disk"""
    profile_path = CONFIG_DIR / f'{profile_name}.json'
    if profile_path.exists():
        try:
            with open(profile_path, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    return None

def save_profile(profile_name, data):
    """Save a profile to disk"""
    profile_path = CONFIG_DIR / f'{profile_name}.json'
    try:
        with open(profile_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False

# ============================================================================
# Click Executor
# ============================================================================

class ClickExecutor:
    def __init__(self):
        self.running = False
        self.thread = None
        self.clicks = []
        self.repeat_count = 1
        self.repeat_until_stopped = False
    
    def execute_sequence(self):
        """Execute clicks in sequence"""
        repeat_num = 0
        
        while self.running:
            if not self.repeat_until_stopped and repeat_num >= self.repeat_count:
                self.running = False
                break
            
            for click in self.clicks:
                if not self.running:
                    break
                
                x, y = click['x'], click['y']
                click_type = click['type']
                
                # Calculate total interval in seconds
                minutes = click.get('minutes', 0)
                seconds = click.get('seconds', 0)
                milliseconds = click.get('milliseconds', 100)
                interval = minutes * 60 + seconds + milliseconds / 1000.0
                
                # Move cursor and click
                set_cursor_position(x, y)
                mouse_click(click_type)
                
                # Wait for interval
                time.sleep(interval)
            
            repeat_num += 1
    
    def run(self):
        """Execute clicks"""
        if not self.clicks:
            return
        self.execute_sequence()
    
    def start(self):
        """Start clicking in background thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop clicking immediately"""
        self.running = False

# ============================================================================
# Tkinter GUI Application
# ============================================================================

class AutoClickerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('AutoClicker')
        self.geometry('540x540')
        self.resizable(False, False)
        
        self.executor = ClickExecutor()
        self.hotkey_thread = None
        self.start_hotkey = '\\'
        self.stop_hotkey = '`'
        self.current_click_index = -1
        self.listening_for_position = False
        
        self.setup_ui()
        self.start_hotkey_listener()
    
    def setup_ui(self):
        """Build the UI"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # ---- TOP: Profile Management ----
        profile_frame = ttk.Frame(main_frame)
        profile_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Load Profile
        load_frame = ttk.Frame(profile_frame)
        load_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(load_frame, text='Load Profile:', font=('', 9)).pack(anchor=tk.W)
        btn_frame = ttk.Frame(load_frame)
        btn_frame.pack(anchor=tk.W, pady=(2, 0))
        ttk.Button(btn_frame, text='Profile 1', width=13, command=lambda: self.load_profile('Profile 1')).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text='Profile 2', width=13, command=lambda: self.load_profile('Profile 2')).pack(side=tk.LEFT, padx=3)
        
        # Save Profile
        save_frame = ttk.Frame(profile_frame)
        save_frame.pack(side=tk.LEFT, padx=(20, 0))
        ttk.Label(save_frame, text='Save Profile:', font=('', 9)).pack(anchor=tk.W)
        btn_frame = ttk.Frame(save_frame)
        btn_frame.pack(anchor=tk.W, pady=(2, 0))
        ttk.Button(btn_frame, text='Profile 1', width=13, command=lambda: self.save_profile('Profile 1')).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text='Profile 2', width=13, command=lambda: self.save_profile('Profile 2')).pack(side=tk.LEFT, padx=2)
        
        # ---- Hotkey + Repeat Settings ----
        hotkey_frame = ttk.LabelFrame(main_frame, text='Settings', padding=6)
        hotkey_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Hotkey row
        hotkey_inner = ttk.Frame(hotkey_frame)
        hotkey_inner.pack(fill=tk.X, pady=(0, 6))
        
        ttk.Label(hotkey_inner, text='Start/Stop Hotkey:').pack(side=tk.LEFT)
        self.hotkey_var = tk.StringVar(value='`')
        hotkey_entry = ttk.Entry(hotkey_inner, textvariable=self.hotkey_var, width=4)
        hotkey_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(hotkey_inner, text='Set', width=4, command=self.set_hotkey).pack(side=tk.LEFT)
        
        # Repeat options row
        repeat_frame = ttk.Frame(hotkey_frame)
        repeat_frame.pack(fill=tk.X)
        
        # "Repeat:" label
        ttk.Label(repeat_frame, text='Repeat:', font=('', 9)).pack(side=tk.LEFT)

        self.repeat_mode_var = tk.StringVar(value='repeat')
        ttk.Radiobutton(repeat_frame, variable=self.repeat_mode_var, value='repeat', command=self.on_repeat_mode_change).pack(side=tk.LEFT, padx=(20, 10))
        
        self.repeat_var = tk.StringVar(value='1')
        self.repeat_entry = ttk.Entry(repeat_frame, textvariable=self.repeat_var, width=3)
        self.repeat_entry.pack(side=tk.LEFT)
        ttk.Label(repeat_frame, text='times').pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(repeat_frame, text='until stopped', variable=self.repeat_mode_var, value='until_stopped', command=self.on_repeat_mode_change).pack(side=tk.LEFT, padx=20)
        
        # ---- TWO-PANEL LAYOUT ----
        panels_frame = ttk.Frame(main_frame)
        panels_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left Panel - Click Details
        left_panel = ttk.LabelFrame(panels_frame, text='Click Details', padding=6)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 4))
        
        # Position
        ttk.Label(left_panel, text='Position:', font=('', 9, 'bold')).pack(anchor=tk.W)
        pos_frame = ttk.Frame(left_panel)
        pos_frame.pack(fill=tk.X, pady=(2, 6))
        ttk.Label(pos_frame, text='X:').pack(side=tk.LEFT)
        self.x_var = tk.StringVar(value='0')
        ttk.Entry(pos_frame, textvariable=self.x_var, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Label(pos_frame, text='Y:').pack(side=tk.LEFT, padx=(10, 0))
        self.y_var = tk.StringVar(value='0')
        ttk.Entry(pos_frame, textvariable=self.y_var, width=6).pack(side=tk.LEFT, padx=2)
        
        # Click Type
        ttk.Label(left_panel, text='Click Type:', font=('', 9, 'bold')).pack(anchor=tk.W)
        self.type_var = tk.StringVar(value='left')
        type_menu = ttk.Combobox(left_panel, textvariable=self.type_var, values=['left', 'right', 'double'], state='readonly', width=15)
        type_menu.pack(fill=tk.X, pady=(2, 6))
        
        # Interval
        ttk.Label(left_panel, text='Interval:', font=('', 9, 'bold')).pack(anchor=tk.W)
        interval_frame = ttk.Frame(left_panel)
        interval_frame.pack(fill=tk.X, pady=(2, 6))
        
        ttk.Label(interval_frame, text='Min:').pack(side=tk.LEFT)
        self.min_var = tk.StringVar(value='0')
        ttk.Entry(interval_frame, textvariable=self.min_var, width=3).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(interval_frame, text='Sec:').pack(side=tk.LEFT, padx=(10, 0))
        self.sec_var = tk.StringVar(value='0')
        ttk.Entry(interval_frame, textvariable=self.sec_var, width=3).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(interval_frame, text='Ms:').pack(side=tk.LEFT, padx=(10, 0))
        self.ms_var = tk.StringVar(value='0')
        ttk.Entry(interval_frame, textvariable=self.ms_var, width=3).pack(side=tk.LEFT, padx=2)
        
        # Get Current Position Button
        ttk.Button(left_panel, text='Get Current Position', width=22, command=self.get_position).pack(fill=tk.X, pady=(6, 6))
        
        # Add/Update buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=(0, 6))
        ttk.Button(button_frame, text='Add Click', width=13, command=self.add_click).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(button_frame, text='Update', width=13, command=self.update_click).pack(side=tk.LEFT)
        
        # Help text
        ttk.Label(left_panel, text='Click "Get Current Position"\nthen click anywhere on screen\nto capture coordinates.', 
                  font=('', 8), foreground='gray', justify=tk.LEFT).pack(fill=tk.X, pady=(0, 0))
        
        # Right Panel - Click List + Controls
        right_panel = ttk.LabelFrame(panels_frame, text='Clicks & Control', padding=6)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Click List (Top)
        list_frame = ttk.Frame(right_panel)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        
        scroll = ttk.Scrollbar(list_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.clicks_listbox = tk.Listbox(list_frame, yscrollcommand=scroll.set, font=('Courier', 8), height=12)
        self.clicks_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.clicks_listbox.bind('<<ListboxSelect>>', self.on_click_select)
        scroll.config(command=self.clicks_listbox.yview)
        
        # Control Buttons (Bottom)
        control_frame = ttk.Frame(right_panel)
        control_frame.pack(fill=tk.X)
        
        self.start_btn = ttk.Button(control_frame, text=f'Start ({self.start_hotkey})', command=self.start_clicking)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 4), fill=tk.X, expand=True)
        
        self.stop_btn = ttk.Button(control_frame, text=f'Stop ({self.stop_hotkey})', command=self.stop_clicking)
        self.stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.status_label = ttk.Label(right_panel, text='Ready', foreground='green', font=('', 9))
        self.status_label.pack(pady=(4, 0))
    
    def set_hotkey(self):
        """Set the hotkey"""
        key = self.hotkey_var.get().strip()
        if not key:
            return
        
        self.start_hotkey = key
        self.stop_hotkey = key
        self.start_btn.config(text=f'Start ({key})')
        self.stop_btn.config(text=f'Stop ({key})')
    
    def on_repeat_mode_change(self):
        """Handle repeat mode radio button change"""
        if self.repeat_mode_var.get() == 'until_stopped':
            self.repeat_entry.config(state='disabled')
        else:
            self.repeat_entry.config(state='normal')
    
    def add_click(self):
        """Add a new click from the left panel"""
        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            minutes = int(self.min_var.get())
            seconds = int(self.sec_var.get())
            milliseconds = int(self.ms_var.get())
            
            click = {
                'x': x,
                'y': y,
                'type': self.type_var.get(),
                'minutes': minutes,
                'seconds': seconds,
                'milliseconds': milliseconds
            }
            
            self.executor.clicks.append(click)
            self.refresh_clicks_display()
        except ValueError:
            pass
    
    def update_click(self):
        """Update the currently selected click"""
        if self.current_click_index < 0:
            return
        
        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            minutes = int(self.min_var.get())
            seconds = int(self.sec_var.get())
            milliseconds = int(self.ms_var.get())
            
            click = self.executor.clicks[self.current_click_index]
            click['x'] = x
            click['y'] = y
            click['type'] = self.type_var.get()
            click['minutes'] = minutes
            click['seconds'] = seconds
            click['milliseconds'] = milliseconds
            
            self.refresh_clicks_display()
        except ValueError:
            pass
    
    def on_click_select(self, event):
        """Load selected click into the editor"""
        selection = self.clicks_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        self.current_click_index = idx
        click = self.executor.clicks[idx]
        
        self.x_var.set(str(click['x']))
        self.y_var.set(str(click['y']))
        self.type_var.set(click['type'])
        self.min_var.set(str(click.get('minutes', 0)))
        self.sec_var.set(str(click.get('seconds', 0)))
        self.ms_var.set(str(click.get('milliseconds', 100)))
    
    def refresh_clicks_display(self):
        """Refresh the listbox display"""
        self.clicks_listbox.delete(0, tk.END)
        for idx, click in enumerate(self.executor.clicks):
            minutes = click.get('minutes', 0)
            seconds = click.get('seconds', 0)
            milliseconds = click.get('milliseconds', 100)
            interval = f"{minutes}m {seconds}s {milliseconds}ms"
            text = f"{idx+1}. ({click['x']},{click['y']}) {click['type'].upper()} {interval}"
            self.clicks_listbox.insert(tk.END, text)
        
        self.current_click_index = -1
        self.clear_click_editor()
    
    def clear_click_editor(self):
        """Clear the left panel editor"""
        self.x_var.set('0')
        self.y_var.set('0')
        self.type_var.set('left')
        self.min_var.set('0')
        self.sec_var.set('0')
        self.ms_var.set('100')
    
    def get_position(self):
        """Wait for user to click and capture position (physical coordinates)"""
        if self.listening_for_position:
            return
        
        self.listening_for_position = True
        
        def on_click(x, y, button, pressed):
            """Capture mouse click position"""
            if pressed and self.listening_for_position:
                self.x_var.set(str(int(x)))
                self.y_var.set(str(int(y)))
                self.listening_for_position = False
                return False  # Stop listener
            return True
        
        # Create listener in background thread and clean it up immediately after capture
        def listen():
            with pynput_mouse.Listener(on_click=on_click) as listener:
                listener.join()
        
        thread = threading.Thread(target=listen, daemon=True)
        thread.start()
    
    def on_mouse_click(self, x, y, pressed):
        """Capture mouse click position"""
        if pressed and self.listening_for_position:
            self.x_var.set(str(x))
            self.y_var.set(str(y))
            self.listening_for_position = False
            messagebox.showinfo('Position', f'Captured: ({x}, {y})')
            return False
    
    def start_clicking(self):
        """Start the autoclick"""
        if self.executor.running:
            return
        
        if not self.executor.clicks:
            return
        
        try:
            if self.repeat_mode_var.get() == 'until_stopped':
                self.executor.repeat_until_stopped = True
                self.executor.repeat_count = 1
            else:
                self.executor.repeat_until_stopped = False
                self.executor.repeat_count = int(self.repeat_var.get())
        except ValueError:
            return
        
        self.executor.start()
        self.status_label.config(text='Running', foreground='red')
    
    def stop_clicking(self):
        """Stop the autoclick"""
        self.executor.stop()
        self.status_label.config(text='Stopped', foreground='orange')
    
    def start_hotkey_listener(self):
        """Start listening for hotkey presses"""
        def listen():
            previous_state = {}
            
            while True:
                try:
                    # Check if the hotkey is pressed
                    if keyboard.is_pressed(self.start_hotkey):
                        if not previous_state.get(self.start_hotkey, False):
                            # Key just pressed (transition from not pressed to pressed)
                            previous_state[self.start_hotkey] = True
                            
                            # Toggle start/stop
                            if self.executor.running:
                                self.stop_clicking()
                            else:
                                self.start_clicking()
                    else:
                        # Key released
                        previous_state[self.start_hotkey] = False
                    
                    time.sleep(0.05)  # Small delay to avoid busy-waiting
                except Exception:
                    time.sleep(0.1)
        
        self.hotkey_thread = threading.Thread(target=listen, daemon=True)
        self.hotkey_thread.start()
    
    def save_profile(self, profile_name):
        """Save current configuration to a profile"""
        data = {
            'hotkey': self.start_hotkey,
            'repeat_mode': self.repeat_mode_var.get(),
            'repeat_count': int(self.repeat_var.get()),
            'clicks': self.executor.clicks
        }
        save_profile(profile_name, data)
    
    def load_profile(self, profile_name):
        """Load a profile"""
        data = load_profile(profile_name)
        if data:
            self.executor.clicks = data.get('clicks', [])
            self.hotkey_var.set(data.get('hotkey', '`'))
            self.set_hotkey()
            self.repeat_mode_var.set(data.get('repeat_mode', 'repeat'))
            self.repeat_var.set(str(data.get('repeat_count', 1)))
            self.on_repeat_mode_change()
            self.refresh_clicks_display()

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    app = AutoClickerApp()
    app.mainloop()
