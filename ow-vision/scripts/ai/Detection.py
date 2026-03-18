from mss import mss
import cv2
import numpy as np
import time
import pandas as pd
from ultralytics import YOLO
import pyautogui
import win32api
import win32con
import math
import torch
import json
import os

# --- [v17.0 HYPER-SYNC ENGINE - THE DEFINITIVE FIX] ---

class Detection:
    def __init__(self):
        base_scripts = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(base_scripts, 'config.json')
        
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
        # 1. Screen Resolution Intelligence
        SCREEN_W, SCREEN_H = pyautogui.size()
        scale_factor = SCREEN_H / 1080.0 # Standardize based on 1080p feel
        
        # 2. Optimized Capture Region (400x400 virtual area)
        CAPTURE_SIZE = int(400 * scale_factor)
        left = (SCREEN_W - CAPTURE_SIZE) // 2
        top = (SCREEN_H - CAPTURE_SIZE) // 2
        
        region = {"top": top, "left": left, "width": CAPTURE_SIZE, "height": CAPTURE_SIZE}
        capture_center = CAPTURE_SIZE // 2
        
        # 3. Path & Device Calibration
        base_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_path = os.path.join(base_root, 'models', 'v2.pt')
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"[*] Engine v17.0 Active | Res: {SCREEN_W}x{SCREEN_H} | Scale: {scale_factor:.2f} | Device: {device.upper()}")
        
        try:
            model = YOLO(model_path)
            model.to(device)
            if device == "cuda": model.model.half() # Instant speed on GPUs
        except Exception as e:
            return

        self.vision_window_open = False
        
        with mss() as stc:
            while True:
                # Dynamic Setting Sync
                if time.time() - self.last_config_check > 0.5:
                    self.load_settings()
                    model.conf = self.CONFIDENCE
                    self.last_config_check = time.time()

                if not self.enable_aim and not self.visualize:
                    if self.vision_window_open:
                        cv2.destroyAllWindows()
                        self.vision_window_open = False
                    time.sleep(0.1)
                    continue

                # Multi-threaded image capture
                img = np.array(stc.grab(region))
                screenshot = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                # AI Inference (Detection)
                results = model.predict(screenshot, save=False, verbose=False, device=device, half=(device=="cuda"))
                
                if len(results[0].boxes) > 0:
                    boxes = results[0].boxes.data.cpu().numpy()
                else:
                    boxes = []

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
                    
                    if self.visualize:
                        cv2.rectangle(screenshot, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

                # AIM LOCK LOGIC
                trigger = (win32api.GetAsyncKeyState(self.trigger_key) < 0)
                
                if target and trigger and self.enable_aim:
                    tx, ty, x1, y1, x2, y2 = target
                    
                    # Relational Mapping (Distance from center)
                    dx = tx - capture_center
                    dy = ty - capture_center
                    
                    # Intelligent Locking (Stickiness)
                    is_on = (x1 <= capture_center <= x2) and (y1 <= capture_center <= y2)
                    smooth = self.SMOOTH_IN if is_on else self.SMOOTH_OUT
                    
                    # [v17.0 FIX]: MULTIPLY by scale_factor to compensate for high resolutions (4K)
                    # This makes 2.6 sensitivity FEEL the same everywhere.
                    move_x = (dx * self.SENS_COMP * scale_factor) / smooth
                    move_y = (dy * self.SENS_COMP * scale_factor) / smooth
                    
                    if int(move_x) != 0 or int(move_y) != 0:
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(move_x), int(move_y), 0, 0)

                # VISION OVERLAY
                if self.visualize:
                    cv2.circle(screenshot, (capture_center, capture_center), int(normalized_fov), (255, 255, 0), 1)
                    cv2.imshow('AI SUPREME v17.0', screenshot)
                    cv2.setWindowProperty('AI SUPREME v17.0', cv2.WND_PROP_TOPMOST, 1)
                    cv2.waitKey(1)
                    self.vision_window_open = True
                else:
                    if self.vision_window_open:
                        cv2.destroyAllWindows()
                        self.vision_window_open = False
                    cv2.waitKey(1)