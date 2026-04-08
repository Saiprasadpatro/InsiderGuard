import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import datetime
import pandas as pd
import os
import platform


LOG_FILE = "data/usb_logs.csv"  # USB log file


# ---------------- File Watcher ---------------- #
class WatcherHandler(FileSystemEventHandler):
    def log_event(self, event_type, path):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Cross-platform user detection
        try:
            user_id = os.getlogin()
        except OSError:
            # Fallback for headless/cloud environments
            user_id = os.environ.get("USER", os.environ.get("USERNAME", "unknown"))
        
        log_data = {
            "timestamp": timestamp,
            "user_id": user_id,
            "event": event_type,
            "path": path
        }

        # Append to CSV
        df = pd.DataFrame([log_data])
        if not os.path.exists(LOG_FILE):
            df.to_csv(LOG_FILE, index=False)
        else:
            df.to_csv(LOG_FILE, mode="a", index=False, header=False)

        print(f"[ALERT] {event_type} -> {path} by {user_id} at {timestamp}")

    def on_created(self, event):
        self.log_event("File Copied/Created", event.src_path)

    def on_modified(self, event):
        self.log_event("File Modified", event.src_path)

    def on_deleted(self, event):
        self.log_event("File Deleted", event.src_path)

    def on_moved(self, event):
        self.log_event("File Moved", f"{event.src_path} -> {event.dest_path}")


def detect_usb():
    """Detect USB drives (Windows only)"""
    if platform.system() != "Windows":
        return []  # No USB detection on Linux/macOS in Streamlit
    
    try:
        import win32file
        drive_list = []
        drivebits = win32file.GetLogicalDrives()
        for d in range(1, 26):
            mask = 1 << d
            if drivebits & mask:
                drname = '%c:\' % chr(ord('A') + d)
                t = win32file.GetDriveType(drname)
                if t == win32file.DRIVE_REMOVABLE:
                    drive_list.append(drname)
        return drive_list
    except ImportError:
        return []


def start_usb_monitor():
    """Start USB monitoring (gracefully skips on non-Windows platforms)"""
    if platform.system() != "Windows":
        print("[INFO] USB monitoring not available on this platform")
        return
    
    observers = {}
    old = set(detect_usb())

    def monitor():
        nonlocal old, observers
        while True:
            try:
                new = set(detect_usb())
                added = new - old
                removed = old - new

                if added:
                    for drive in added:
                        print(f"[USB INSERTED] {drive}")
                        event_handler = WatcherHandler()
                        observer = Observer()
                        observer.schedule(event_handler, path=drive, recursive=True)
                        observer.start()
                        observers[drive] = observer

                if removed:
                    for drive in removed:
                        print(f"[USB REMOVED] {drive}")
                        if drive in observers:
                            observers[drive].stop()
                            observers[drive].join()
                            del observers[drive]

                old = new
                time.sleep(2)
            except Exception as e:
                print(f"[ERROR] USB monitoring error: {e}")

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()