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

# --- [v16.7 HEADSHOT ENGINE - ELITE PRECISION] ---

# 1. IMMEDIATE DPI AWARENESS
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    ctypes.windll.user32.SetProcessDPIAware()

class Detection:
    def __init__(self):
        # Master Config Paths
        self.base_scripts = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.base_scripts, 'config.json')
        
        # Elite Defaults
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
        """Elite Polling: Real-time UI Sync"""
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
        # Maximum Process Priority
        process = win32process.GetCurrentProcess()
        win32process.SetPriorityClass(process, win32process.HIGH_PRIORITY_CLASS)

        # Monitor Scaling Calibration
        SCREEN_W = ctypes.windll.user32.GetSystemMetrics(0)
        SCREEN_H = ctypes.windll.user32.GetSystemMetrics(1)
        scale_factor = SCREEN_H / 1080.0 
        
        # Virtual Capture Region
        CAPTURE_SIZE = int(400 * scale_factor)
        left = (SCREEN_W - CAPTURE_SIZE) // 2
        top = (SCREEN_H - CAPTURE_SIZE) // 2
        
        region = {"top": top, "left": left, "width": CAPTURE_SIZE, "height": CAPTURE_SIZE}
        capture_center = CAPTURE_SIZE // 2
        
        # Hardware Sync (v16.7 Elite Check)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"==========================================")
        print(f"   [*] HEADSHOT ENGINE v16.7")
        print(f"   [*] DEVICE: {device.upper()}")
        if device == "cuda":
            print(f"   [*] GPU: {torch.cuda.get_device_name(0)}")
            print(f"   [*] MODE: HEADSHOT PRECISION")
        else:
            print(f"   [!] WARNING: CPU MODE ACTIVE")
        print(f"==========================================")

        base_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_path = os.path.join(base_root, 'models', 'v2.pt')
        
        try:
            # Accelerated Load
            model = YOLO(model_path)
            model.to(device)
            if device == "cuda": 
                model.model.half() # Instant GPU Speedup
        except Exception as e:
            print(f"[CRITICAL ERROR] Failed to load Brain (v2.pt): {e}")
            return

        self.vision_window_open = False
        
        with mss() as stc:
            while True:
                # Instant Config Tracking
                if time.time() - self.last_config_check > 0.1:
                    self.load_settings()
                    model.conf = self.CONFIDENCE
                    self.last_config_check = time.time()

                # Stealth/Hibernation Mode
                if not self.enable_aim and not self.visualize:
                    if self.vision_window_open:
                        cv2.destroyAllWindows()
                        self.vision_window_open = False
                    time.sleep(0.1)
                    continue

                # Elite Frame Capture
                img = np.array(stc.grab(region))
                screenshot = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                # High Precision Prediction
                results = model.predict(screenshot, save=False, verbose=False, device=device, half=(device=="cuda"))
                
                boxes = []
                if len(results[0].boxes) > 0:
                    boxes = results[0].boxes.data.cpu().numpy()

                closest_dist = 100000
                target = None
                normalized_fov = self.AIM_FOV * scale_factor

                for box in boxes:
                    # x1, y1, x2, y2, confidence, class
                    x1, y1, x2, y2, conf, cls = box
                    
                    if cls not in [0, 1]: continue 
                    
                    # Target Calculation (v16.7: Aim at HEAD area)
                    cx = (x1 + x2) / 2
                    height = y2 - y1
                    # Aim at roughly 15% down from the top of the head for maximum headshot probability
                    cy = y1 + (height * 0.15) 
                    
                    dist = math.dist([cx, cy], [capture_center, capture_center])

                    if dist < closest_dist and dist <= normalized_fov:
                        closest_dist = dist
                        target = (cx, cy, x1, y1, x2, y2)
                    
                    # RENDER 'THE EYE' PERSPECTIVE
                    if self.visualize:
                        color = (0, 0, 255) if target and target[0] == cx else (0, 255, 0)
                        cv2.rectangle(screenshot, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        # Mark the target point
                        cv2.circle(screenshot, (int(cx), int(cy)), 3, (0, 0, 255), -1)
                        cv2.putText(screenshot, f"AI: {int(conf*100)}%", (int(x1), int(y1)-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

                # EXECUTION FLOW
                trigger = (win32api.GetAsyncKeyState(self.trigger_key) < 0)
                
                if target and trigger and self.enable_aim:
                    tx, ty, x1, y1, x2, y2 = target
                    dx = tx - capture_center
                    dy = ty - capture_center
                    
                    is_on = (x1 <= capture_center <= x2) and (y1 <= capture_center <= y2)
                    smooth = self.SMOOTH_IN if is_on else self.SMOOTH_OUT
                    
                    # SCALING PARITY (v16.7 Precision)
                    move_x = (dx * self.SENS_COMP * scale_factor) / smooth
                    move_y = (dy * self.SENS_COMP * scale_factor) / smooth
                    
                    if int(move_x) != 0 or int(move_y) != 0:
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(move_x), int(move_y), 0, 0)

                # DUAL-WINDOW UI ENGINE
                if self.visualize:
                    # Draw Master FOV Ring
                    cv2.circle(screenshot, (capture_center, capture_center), int(normalized_fov), (255, 255, 0), 1)
                    window_name = 'AI VISION EYE v16.7'
                    cv2.imshow(window_name, screenshot)
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
                    cv2.waitKey(1)
                    self.vision_window_open = True
                else:
                    if self.vision_window_open:
                        cv2.destroyAllWindows()
                        self.vision_window_open = False
                    cv2.waitKey(1)

if __name__ == "__main__":
    app = Detection()
    app.start()