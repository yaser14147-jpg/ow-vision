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

# --- [v13.0 SUPREME ENGINE - RESOLUTION INDEPENDENT] ---

class Detection:
    def __init__(self):
        base_scripts = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(base_scripts, 'config.json')
        
        # Default settings
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
        # 1. Physical Resolution Detection
        SCREEN_W, SCREEN_H = pyautogui.size()
        
        # 2. Virtual Normalization (Targeting 1080p feel on all screens)
        # This makes the FOV circle and movement feel the same on 4K and 1080p
        scale_factor = SCREEN_H / 1080.0
        
        # Consistent capture size (400x400 virtual pixels)
        CAPTURE_SIZE = int(400 * scale_factor)
        left = (SCREEN_W - CAPTURE_SIZE) // 2
        top = (SCREEN_H - CAPTURE_SIZE) // 2
        
        region = {"top": top, "left": left, "width": CAPTURE_SIZE, "height": CAPTURE_SIZE}
        capture_center = CAPTURE_SIZE // 2
        
        # 3. Path & Device
        base_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_path = os.path.join(base_root, 'models', 'v2.pt')
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"[*] Engine v13.0 Active | Res: {SCREEN_W}x{SCREEN_H} | Device: {device.upper()}")
        
        try:
            model = YOLO(model_path)
            model.to(device)
            # Use Half-presicion if on GPU for double speed (Turbo Mode)
            if device == "cuda": model.model.half() 
        except Exception as e:
            return

        self.vision_window_open = False
        
        with mss() as stc:
            while True:
                # Dynamic Setting Update
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

                # Capture
                img = np.array(stc.grab(region))
                screenshot = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                # Predict
                results = model.predict(screenshot, save=False, verbose=False, device=device, half=(device=="cuda"))
                
                if len(results[0].boxes) > 0:
                    boxes = results[0].boxes.data.cpu().numpy()
                else:
                    boxes = []

                closest_dist = 100000
                target = None

                # Normalize FOV for screen resolution
                normalized_fov = self.AIM_FOV * scale_factor

                for box in boxes:
                    x1, y1, x2, y2, conf, cls = box
                    if cls != 1: continue # Targeting class 1
                    
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    dist = math.dist([cx, cy], [capture_center, capture_center])

                    if dist < closest_dist and dist <= normalized_fov:
                        closest_dist = dist
                        target = (cx, cy, x1, y1, x2, y2)
                    
                    if self.visualize:
                        cv2.rectangle(screenshot, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

                # AIMING LOGIC
                trigger = (win32api.GetAsyncKeyState(self.trigger_key) < 0)
                
                if target and trigger and self.enable_aim:
                    tx, ty, x1, y1, x2, y2 = target
                    
                    # Calculate Relative Movement
                    dx = tx - capture_center
                    dy = ty - capture_center
                    
                    # On-Target Smoothing
                    is_on = (x1 <= capture_center <= x2) and (y1 <= capture_center <= y2)
                    smooth = self.SMOOTH_IN if is_on else self.SMOOTH_OUT
                    
                    # Compensation adjusted for screen scaling
                    move_x = (dx * self.SENS_COMP) / (smooth * scale_factor)
                    move_y = (dy * self.SENS_COMP) / (smooth * scale_factor)
                    
                    if int(move_x) != 0 or int(move_y) != 0:
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(move_x), int(move_y), 0, 0)

                # VISION UI
                if self.visualize:
                    cv2.circle(screenshot, (capture_center, capture_center), int(normalized_fov), (255, 255, 0), 1)
                    cv2.imshow('AI SUPREME v13.0', screenshot)
                    cv2.setWindowProperty('AI SUPREME v13.0', cv2.WND_PROP_TOPMOST, 1)
                    cv2.waitKey(1)
                    self.vision_window_open = True
                else:
                    if self.vision_window_open:
                        cv2.destroyAllWindows()
                        self.vision_window_open = False
                    cv2.waitKey(1)