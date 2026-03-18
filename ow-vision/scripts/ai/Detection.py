from typing import Counter
from mss import mss
import cv2
import numpy as np
import time
import pandas as pd
from ultralytics import YOLO
import pyautogui
import win32api
import win32con
import threading
import math
import torch
import json
import os

# --- [v12.0 MASTER ENGINE] ---

class Detection:
    def __init__(self):
        # Resolve path to config.json correctly relative to this script
        # Scripts are in ow-vision/scripts/ai/Detection.py, config is in ow-vision/scripts/config.json
        base_scripts = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(base_scripts, 'config.json')
        print(f"[*] Engine Initialized. Config Path: {self.config_path}")
        
        self.last_config_check = 0
        self.AIM_FOV = 75
        self.CONFIDENCE = 0.30
        self.trigger_key = 0x06
        self.SENS_COMP = 2.6
        self.SMOOTH_IN = 1.3
        self.SMOOTH_OUT = 3.8
        self.visualize = False
        self.enable_aim = False
        
        self.load_settings()

    def load_settings(self):
        """Reloads config from disk every 0.5s."""
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
        except Exception as e:
            # Silently fail or log to a small file if needed
            pass

    def start(self):
        # 1. Dynamic Monitor Resolution Detection
        MONITOR_WIDTH, MONITOR_HEIGHT = pyautogui.size()
        MONITOR_SCALE = 5 # Small center capture area for performance
        
        # Calculate capture region for MSS
        width = int(MONITOR_WIDTH / MONITOR_SCALE)
        height = int(MONITOR_HEIGHT / MONITOR_SCALE)
        left = int((MONITOR_WIDTH - width) / 2)
        top = int((MONITOR_HEIGHT - height) / 2)
        
        region_dict = {"top": top, "left": left, "width": width, "height": height}
        screenshotCenter = [int(width / 2), int(height / 2)]
        
        # 2. Path Resolution for AI Model
        base_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_path = os.path.join(base_root, 'models', 'v2.pt')
        
        # 3. Intelligent Device Selection (CUDA vs CPU)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[*] Starting AI Engine on: {device.upper()}")
        
        try:
            model = YOLO(model_path)
            model.to(device)
        except Exception as e:
            with open("engine_error.txt", "w") as f: f.write(str(e))
            return
            
        self.vision_window_open = False
        settings = {"detect": [1]} # Targeting 'person' / specified class
        
        with mss() as stc:
            print("[*] Engine Capture Loop Started.")
            while True:
                # 4. Dynamic Config Reloading
                if time.time() - self.last_config_check > 0.5:
                    self.load_settings()
                    model.conf = self.CONFIDENCE
                    self.last_config_check = time.time()

                # Optimization: Deep sleep if both inactive
                if not self.enable_aim and not self.visualize:
                    if self.vision_window_open:
                        cv2.destroyAllWindows()
                        self.vision_window_open = False
                    time.sleep(0.1)
                    continue

                # 5. Capture & Transform
                try:
                    img = stc.grab(region_dict)
                    screenshot = np.array(img)
                    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
                except:
                    continue

                # 6. Inference
                results = model.predict(
                    screenshot, 
                    save=False, 
                    classes=settings["detect"], 
                    verbose=False, 
                    device=device, 
                    half=(device=="cuda") # Speed up if GPU
                )
                
                # Extract results into DataFrame
                if len(results[0].boxes) > 0:
                    positionsFrame = pd.DataFrame(results[0].boxes.data.cpu().numpy(), columns=['xmin', 'ymin', 'xmax', 'ymax', 'conf', 'class'])
                else:
                    positionsFrame = pd.DataFrame()

                closestPartDistance = 100000
                closestPart = -1

                # 7. Locate Nearest Target inside FOV
                for i, row in positionsFrame.iterrows():
                    xmin, ymin, xmax, ymax, confidence, category = row.astype('int')
                    centerX = (xmax - xmin) / 2 + xmin
                    centerY = (ymax - ymin) / 2 + ymin
                    distance = math.dist([centerX, centerY], screenshotCenter)

                    if distance < closestPartDistance and distance <= self.AIM_FOV:
                        closestPartDistance = distance
                        closestPart = i
                    
                    # Optional visualization drawing
                    if self.visualize:
                        color = (0, 0, 255) if i == closestPart else (0, 255, 0)
                        cv2.rectangle(screenshot, (xmin, ymin), (xmax, ymax), color, 2)

                trigger_pressed = (win32api.GetAsyncKeyState(self.trigger_key) < 0)

                # 8. Trigger Aimbot Logic (Smoothing & Locking)
                if closestPart != -1:
                    xmin, ymin, xmax, ymax = positionsFrame.iloc[closestPart, :4]
                    target_x = (xmax - xmin) / 2 + xmin
                    target_y = (ymax - ymin) / 2 + ymin
                    
                    if trigger_pressed and self.enable_aim:
                        diff_x = target_x - screenshotCenter[0]
                        diff_y = target_y - screenshotCenter[1]
                        
                        # Smoothness depends on proximity to center (locking effect)
                        is_aim_on_character = (xmin <= screenshotCenter[0] <= xmax) and (ymin <= screenshotCenter[1] <= ymax)
                        smooth_divisor = self.SMOOTH_IN if is_aim_on_character else self.SMOOTH_OUT 
                        
                        target_x_move = (diff_x * self.SENS_COMP) / smooth_divisor
                        target_y_move = (diff_y * self.SENS_COMP) / smooth_divisor

                        if int(target_x_move) != 0 or int(target_y_move) != 0:
                            # Relative mouse move
                            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(target_x_move), int(target_y_move), 0, 0)
                            
                # 9. UI Layer (The Eye/Vision Feature)
                if self.visualize:
                    # Draw FOV Circle
                    cv2.circle(screenshot, (screenshotCenter[0], screenshotCenter[1]), int(self.AIM_FOV), (255, 255, 0), 1)
                    window_name = 'AI Vision - MASTER ENGINE v12.0'
                    cv2.imshow(window_name, screenshot)
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
                    cv2.waitKey(1)
                    self.vision_window_open = True
                else:
                    if self.vision_window_open:
                        cv2.destroyAllWindows()
                        self.vision_window_open = False
                    cv2.waitKey(1)