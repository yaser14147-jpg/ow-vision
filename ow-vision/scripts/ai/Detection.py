from mss import mss
import cv2
import numpy as np
import time
import pandas as pd
from ultralytics import YOLO
import pyautogui
import win32api
import win32con
import win32process
import math
import torch
import json
import os
import ctypes

# --- [v3.4 SUPREME ENGINE - THE MASTER CONFIG] ---

# 1. IMMEDIATE DPI AWARENESS
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    ctypes.windll.user32.SetProcessDPIAware()

class Detection:
    def __init__(self):
        # Use absolute path for config to avoid any confusion
        self.base_scripts = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.base_scripts, 'config.json')
        
        # Absolute Defaults
        self.AIM_FOV = 75
        self.CONFIDENCE = 0.30
        self.trigger_key = 0x06
        self.SENS_COMP = 2.6
        self.SMOOTH_IN = 1.3
        self.SMOOTH_OUT = 3.8
        self.visualize = False
        self.enable_aim = False
        
        self.last_config_check = 0
        self.load_settings()

    def load_settings(self):
        """Polls config.json for real-time changes from UI."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.AIM_FOV = float(config.get("aim_fov", 75))
                    self.CONFIDENCE = float(config.get("confidence", 0.30))
                    self.trigger_key = int(config.get("trigger_key_hex", "0x06"), 0)
                    self.SENS_COMP = float(config.get("sens_comp", 2.6))
                    self.SMOOTH_IN = float(config.get("smooth_in", 1.3))
                    self.SMOOTH_OUT = float(config.get("smooth_out", 3.8))
                    self.visualize = config.get("visualize", False)
                    self.enable_aim = config.get("enable_aim", False)
        except: pass

    def start(self):
        # 2. BOOST PRIORITY TO THE MAX
        process = win32process.GetCurrentProcess()
        win32process.SetPriorityClass(process, win32process.HIGH_PRIORITY_CLASS)

        # 3. Screen Resolution Calibration
        # Get REAL physical pixels regardless of scaling
        SCREEN_W = ctypes.windll.user32.GetSystemMetrics(0)
        SCREEN_H = ctypes.windll.user32.GetSystemMetrics(1)
        scale_factor = SCREEN_H / 1080.0 
        
        # Capture Region (400x400 virtual area)
        CAPTURE_SIZE = int(400 * scale_factor)
        left = (SCREEN_W - CAPTURE_SIZE) // 2
        top = (SCREEN_H - CAPTURE_SIZE) // 2
        
        region = {"top": top, "left": left, "width": CAPTURE_SIZE, "height": CAPTURE_SIZE}
        capture_center = CAPTURE_SIZE // 2
        
        # 4. Hardware Acceleration Check
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Diagnostics log to help the USER troubleshoot friends' PCs
        with open("gpu_report.txt", "w") as f:
            f.write(f"V3.4 MASTER ENGINE REPORT\n")
            f.write(f"PHYSICAL RESOLUTION: {SCREEN_W}x{SCREEN_H}\n")
            f.write(f"DEVICE DETECTED: {device.upper()}\n")
            if device == "cuda":
                f.write(f"GPU NAME: {torch.cuda.get_device_name(0)}\n")
            f.write(f"SYNC STATUS: ACTIVE\n")

        base_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_path = os.path.join(base_root, 'models', 'v2.pt')
        
        try:
            # Load model with high performance settings
            model = YOLO(model_path)
            model.to(device)
            if device == "cuda": 
                model.model.half() # Instant GPU Speedup
        except Exception as e:
            with open("engine_fatal_error.txt", "w") as f: f.write(str(e))
            return

        self.vision_window_open = False
        
        with mss() as stc:
            while True:
                # Polling for UI changes (Fast 0.2s check for instant 'Eye' feedback)
                if time.time() - self.last_config_check > 0.2:
                    self.load_settings()
                    model.conf = self.CONFIDENCE
                    self.last_config_check = time.time()

                # Optimization: Zero CPU usage when idle
                if not self.enable_aim and not self.visualize:
                    if self.vision_window_open:
                        cv2.destroyAllWindows()
                        self.vision_window_open = False
                    time.sleep(0.1)
                    continue

                # Capture
                img = np.array(stc.grab(region))
                screenshot = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                # Predict
                results = model.predict(screenshot, save=False, verbose=False, device=device, half=(device=="cuda"))
                
                boxes = []
                if len(results[0].boxes) > 0:
                    boxes = results[0].boxes.data.cpu().numpy()

                closest_dist = 100000
                target = None
                normalized_fov = self.AIM_FOV * scale_factor

                for box in boxes:
                    x1, y1, x2, y2, conf, cls = box
                    if cls != 1: continue 
                    
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    dist = math.dist([cx, cy], [capture_center, capture_center])

                    if dist < closest_dist and dist <= normalized_fov:
                        closest_dist = dist
                        target = (cx, cy, x1, y1, x2, y2)
                    
                    # DRAW ONLY IF VISION (EYE) IS ACTIVE
                    if self.visualize:
                        color = (0, 0, 255) if target and target[0] == cx else (0, 255, 0)
                        cv2.rectangle(screenshot, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        cv2.putText(screenshot, f"AI: {int(conf*100)}%", (int(x1), int(y1)-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

                # AIMING EXECUTION
                trigger = (win32api.GetAsyncKeyState(self.trigger_key) < 0)
                
                if target and trigger and self.enable_aim:
                    tx, ty, x1, y1, x2, y2 = target
                    dx = tx - capture_center
                    dy = ty - capture_center
                    
                    is_on = (x1 <= capture_center <= x2) and (y1 <= capture_center <= y2)
                    smooth = self.SMOOTH_IN if is_on else self.SMOOTH_OUT
                    
                    # [v3.4]: SUPREME PRECISION SCALING
                    move_x = (dx * self.SENS_COMP * scale_factor) / smooth
                    move_y = (dy * self.SENS_COMP * scale_factor) / smooth
                    
                    if int(move_x) != 0 or int(move_y) != 0:
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(move_x), int(move_y), 0, 0)

                # VISION UI (THE "EYE" FEATURE)
                if self.visualize:
                    # Draw FOV Circle
                    cv2.circle(screenshot, (capture_center, capture_center), int(normalized_fov), (255, 255, 0), 1)
                    window_name = 'AI VISION - MASTER PERSPECTIVE v3.4'
                    cv2.imshow(window_name, screenshot)
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
                    cv2.waitKey(1)
                    self.vision_window_open = True
                else:
                    if self.vision_window_open:
                        cv2.destroyAllWindows()
                        self.vision_window_open = False
                    # Minimal wait to keep UI alive
                    cv2.waitKey(1)