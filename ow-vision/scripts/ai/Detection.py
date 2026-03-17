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
        target_json = os.path.join(base_scripts, 'config.json')
        
        config = {}
        if os.path.exists(target_json):
            with open(target_json, 'r') as f:
                try:
                    config = json.load(f)
                except:
                    pass
        
        AIM_FOV = float(config.get("aim_fov", 75))
        CONFIDENCE = float(config.get("confidence", 0.30))
        self.trigger_key = int(config.get("trigger_key_hex", "0x06"), 0)
        SENS_COMP = float(config.get("sens_comp", 2.6))
        SMOOTH_IN = float(config.get("smooth_in", 1.3))
        SMOOTH_OUT = float(config.get("smooth_out", 3.8))

        MONITOR_WIDTH = 1920
        MONITOR_HEIGHT = 1080
        MONITOR_SCALE = 5 # تصغير مساحة الرصد بشكل كبير لتقليل استهلاك الموارد (قص الشاشة من النص ليكون أصغر)
        region = (int(MONITOR_WIDTH/2-MONITOR_WIDTH/MONITOR_SCALE/2),
                       int(MONITOR_HEIGHT/2-MONITOR_HEIGHT/MONITOR_SCALE/2),
                       int(MONITOR_WIDTH/2+MONITOR_WIDTH/MONITOR_SCALE/2),
                       int(MONITOR_HEIGHT/2+MONITOR_HEIGHT/MONITOR_SCALE/2))
        x, y, width, height = region
        screenshotCenter = [int((width-x)/2), int((height-y)/2)]
        
        # تحديد مكان الموديل بشكل تلقائي
        base_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_path = os.path.join(base_root, 'models', 'v2.pt')
        
        model = YOLO(model_path)
        model.to("cuda")
        model.conf = CONFIDENCE # الاعتماد على الواجهة
        model.maxdet = 10
        model.apm = True
        triggerbot = False
        lastClick = 0
        settings = {"toggleKey": "²", # the key to toggle the trigger bot, the square on the frame is the state (red=disabled)
                    "cooldown": 1.1, # cooldown between click in seconds (only for mode 0)
                    "detect": [1], # detect enemybody [0] or enemyhead [1] and [0, 1] for both
                    "triggerDelay": 0} # delay between clicking on the target in seconds, 0 is fine 
        with mss() as stc:
            while True:
                closestPartDistance = 100000
                closestPart = -1

                currentTime = time.time()
                screenshot = np.array(stc.grab(region))
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

                frame = model.predict(screenshot, save=False, classes=settings["detect"], verbose=False, device=0, half=False)

                positionsFrame = pd.DataFrame(frame[0].cpu().numpy().boxes.data, columns=['xmin', 'ymin', 'xmax', 'ymax', 'conf', 'class'])

                for i, row in enumerate(positionsFrame.iterrows()):
                    try:
                        xmin, ymin, xmax, ymax, confidence, category = row[1].astype('int')
                        centerX = (xmax-xmin)/2+xmin
                        centerY = (ymax-ymin)/2+ymin
                        distance = math.dist([centerX, centerY], screenshotCenter)

                        # لا تشبك على الهدف إلا إذا كان أقرب لمركز الشاشة (الكورسير) وداخل الـ FOV المسموح
                        if int(distance) < closestPartDistance and distance <= AIM_FOV:
                            closestPartDistance = distance
                            closestPart = i
                    except:
                        pass

                if win32api.GetAsyncKeyState(self.trigger_key) < 0:
                    triggerbot = True
                else:
                    triggerbot = False

                if closestPart != -1:
                    xmin = positionsFrame.iloc[closestPart, 0]
                    ymin = positionsFrame.iloc[closestPart, 1]
                    xmax = positionsFrame.iloc[closestPart, 2]
                    ymax = positionsFrame.iloc[closestPart, 3]
                    
                    # حساب المركز الحقيقي للهدف اللي نبغى نسحب له
                    target_x = (xmax - xmin) / 2 + xmin
                    target_y = (ymax - ymin) / 2 + ymin
                    
                    if triggerbot:
                        diff_x = target_x - screenshotCenter[0]
                        diff_y = target_y - screenshotCenter[1]
                        
                        # حساب المسافة من مؤشر الماوس لـ الهدف
                        distance_to_target = math.sqrt(diff_x**2 + diff_y**2)
                        
                        # الحسبة السحرية: قوة المغناطيس (Multiplier)
                        # السحب من بعيد بيكون خفيف للتمويه، لكن يوم يوصل النص يمسك بقوة خياليه (Hard Lock)
                        # تحقق: هل مؤشر الماوس (الكروس هير) يقع فعلياً "داخل" المربع الخاص بالشخصية أم خارجها؟
                        # نستخدم إحداثيات المربع المستخرجة مسبقاً: xmin, ymin, xmax, ymax
                        # نستخدم إحداثيات المربع المستخرجة مسبقاً: xmin, ymin, xmax, ymax
                        is_aim_on_character = (xmin <= screenshotCenter[0] <= xmax) and \
                                              (ymin <= screenshotCenter[1] <= ymax)

                        # بما أن الذكاء الاصطناعي يقرأ الفريمات بسرعة أقل من الـ AHK، القفز المباشر هو اللي يخليه "مو سلس ومقطع".
                        # السّر الجديد للسلاسة البشرية: (Smooth Easing)
                        # بدال ما نقفز للرأس في فريم واحد، بنخليه يطير للمسافة كنِسبة (Gliding) تتناقص كل ما قرّب.. هذي الحركة مستحيل تبان إنها سكربت!
                        
                        if is_aim_on_character:
                            smooth_divisor = SMOOTH_IN 
                        else:
                            smooth_divisor = SMOOTH_OUT 
                        
                        target_x_move = (diff_x * SENS_COMP) / smooth_divisor
                        target_y_move = (diff_y * SENS_COMP) / smooth_divisor

                        # الإجبار للوصول لنقطة الصفر (المنتصف تماماً):
                        # علشان إذا صار قريب، الماوس ما يوقف ويتجاهل البكسلات العشرية لأنه بيسوي تقطيع.
                        if target_x_move > 0: target_x_move = math.ceil(target_x_move)
                        elif target_x_move < 0: target_x_move = math.floor(target_x_move)

                        if target_y_move > 0: target_y_move = math.ceil(target_y_move)
                        elif target_y_move < 0: target_y_move = math.floor(target_y_move)
                        
                        if int(target_x_move) != 0 or int(target_y_move) != 0:
                            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(target_x_move), int(target_y_move), 0, 0)
                            
                # تم إزالة كافة شاشات العرض ورسومات OpenCV كما طلب المستخدمเพื่อ أن يكون البرنامج مخفي بدون أي نوافذ تزعج أو تظهر