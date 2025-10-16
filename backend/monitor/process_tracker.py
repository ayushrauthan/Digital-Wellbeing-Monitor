# backend/monitor/process_tracker.py
import psutil
import pygetwindow as gw
import os

# --- We only need these for Windows ---
if os.name == 'nt':
    import win32process
    import win32gui

def get_active_process_info():
    """
    Gets information about the currently active window's process.
    This version is more robust for Windows.
    """
    try:
        active_window = gw.getActiveWindow()
        if not active_window:
            return None

        pid = None
        # --- On Windows, get the PID from the window handle ---
        if os.name == 'nt':
            try:
                hwnd = active_window._hWnd
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
            except Exception:
                # Fallback if we can't get PID
                pass
        
        if pid:
            p = psutil.Process(pid)
            return {
                'pid': pid,
                'name': p.name(),
                'path': p.exe(),
                'title': active_window.title
            }
        else: # Fallback for non-Windows or if PID lookup fails
             return {
                'pid': None,
                'name': "Unknown Application",
                'path': None,
                'title': active_window.title
            }

    except (psutil.NoSuchProcess, psutil.AccessDenied, gw.PyGetWindowException):
        return None