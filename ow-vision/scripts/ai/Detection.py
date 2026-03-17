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

class Detection:
    def __init__(self):
        # تحميل الإعدادات بشكل ذكي وتلقائي حسب مكان المجلد
        base_scripts = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(base_scripts, 'config.json')
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
        except:
            pass

    def start(self):
        MONITOR_WIDTH = 1920
        MONITOR_HEIGHT = 1080
        MONITOR_SCALE = 5 
        region = (int(MONITOR_WIDTH/2-MONITOR_WIDTH/MONITOR_SCALE/2),
                       int(MONITOR_HEIGHT/2-MONITOR_HEIGHT/MONITOR_SCALE/2),
                       int(MONITOR_WIDTH/2+MONITOR_WIDTH/MONITOR_SCALE/2),
                       int(MONITOR_HEIGHT/2+MONITOR_HEIGHT/MONITOR_SCALE/2))
        x, y, width, height = region
        screenshotCenter = [int((width-x)/2), int((height-y)/2)]
        
        base_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_path = os.path.join(base_root, 'models', 'v2.pt')
        
        model = YOLO(model_path)
        model.to("cuda")
        model.conf = self.CONFIDENCE 
        model.maxdet = 10
        model.apm = True
        
        settings = {"detect": [1]} 
        self.vision_window_open = False
        
        with mss() as stc:
            while True:
                # تحديث الإعدادات
                if time.time() - self.last_config_check > 0.5:
                    self.load_settings()
                    model.conf = self.CONFIDENCE
                    self.last_config_check = time.time()

                # تحسين الأداء: إذا كان الأيمبوت والمنظور مغلقين، السكربت ينام تماماً لتوفير الطاقة
                if not self.enable_aim and not self.visualize:
                    if self.vision_window_open:
                        cv2.destroyAllWindows()
                        self.vision_window_open = False
                    time.sleep(0.1) # نوم عميق لتوفير المعالج
                    continue

                screenshot = np.array(stc.grab(region))
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

                try:
                    frame = model.predict(screenshot, save=False, classes=settings["detect"], verbose=False, device=0, half=True) # half=True للسرعة
                    positionsFrame = pd.DataFrame(frame[0].cpu().numpy().boxes.data, columns=['xmin', 'ymin', 'xmax', 'ymax', 'conf', 'class'])
                except:
                    continue

                closestPartDistance = 100000
                closestPart = -1

                for i, row in enumerate(positionsFrame.iterrows()):
                    try:
                        xmin, ymin, xmax, ymax, confidence, category = row[1].astype('int')
                        centerX = (xmax-xmin)/2+xmin
                        centerY = (ymax-ymin)/2+ymin
                        distance = math.dist([centerX, centerY], screenshotCenter)

                        if int(distance) < closestPartDistance and distance <= self.AIM_FOV:
                            closestPartDistance = distance
                            closestPart = i
                        
                        # الرسم يتم "فقط" إذا كانت العين مفتوحة
                        if self.visualize:
                            color = (0, 0, 255) if i == closestPart else (0, 255, 0)
                            cv2.rectangle(screenshot, (xmin, ymin), (xmax, ymax), color, 2)
                            cv2.putText(screenshot, f"Conf: {confidence}", (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    except: pass

                trigger_pressed = (win32api.GetAsyncKeyState(self.trigger_key) < 0)

                if closestPart != -1:
                    xmin, ymin, xmax, ymax = positionsFrame.iloc[closestPart, :4]
                    target_x = (xmax - xmin) / 2 + xmin
                    target_y = (ymax - ymin) / 2 + ymin
                    
                    if self.visualize:
                        cv2.line(screenshot, (screenshotCenter[0], screenshotCenter[1]), (int(target_x), int(target_y)), (255, 255, 255), 1)

                    if trigger_pressed and self.enable_aim:
                        diff_x = target_x - screenshotCenter[0]
                        diff_y = target_y - screenshotCenter[1]
                        
                        is_aim_on_character = (xmin <= screenshotCenter[0] <= xmax) and (ymin <= screenshotCenter[1] <= ymax)
                        smooth_divisor = self.SMOOTH_IN if is_aim_on_character else self.SMOOTH_OUT 
                        
                        target_x_move = (diff_x * self.SENS_COMP) / smooth_divisor
                        target_y_move = (diff_y * self.SENS_COMP) / smooth_divisor

                        if target_x_move > 0: target_x_move = math.ceil(target_x_move)
                        elif target_x_move < 0: target_x_move = math.floor(target_x_move)
                        if target_y_move > 0: target_y_move = math.ceil(target_y_move)
                        elif target_y_move < 0: target_y_move = math.floor(target_y_move)
                        
                        if int(target_x_move) != 0 or int(target_y_move) != 0:
                            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(target_x_move), int(target_y_move), 0, 0)
                            
                if self.visualize:
                    cv2.circle(screenshot, (screenshotCenter[0], screenshotCenter[1]), int(self.AIM_FOV), (255, 255, 0), 1)
                    window_name = 'AI Vision - Perspective'
                    cv2.imshow(window_name, screenshot)
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
                    cv2.waitKey(1)
                    self.vision_window_open = True
                else:
                    if self.vision_window_open:
                        cv2.destroyAllWindows()
                        self.vision_window_open = False
                    cv2.waitKey(1)