import tkinter as tk
from tkinter import ttk, messagebox
import multiprocessing
import sys
import os
import json
import glob
import ctypes
import win32api
import win32con
import threading

# إيقاف أي كود قد يسبب وميضاً

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "configs")
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

DEFAULT_CONFIG = {
    "aim_fov": 75,
    "sens_comp": 2.6,
    "smooth_in": 1.3,
    "smooth_out": 3.8,
    "confidence": 0.30,
    "trigger_key": "XButton 2",
    "visualize": False,
    "enable_aim": False
}

ACTIVE_CFG_PATH = os.path.join(BASE_DIR, "config.json")

def save_active_config(cfg):
    try:
        # تأكد من المسار الصحيح للملف config.json بجانب main.py
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        with open(config_path, "w") as f:
            json.dump(cfg, f, indent=4)
            f.flush()
            os.fsync(f.fileno()) # إجبار ويندوز على كتابة الملف فوراً
    except Exception as e:
        with open("error_save.txt", "a") as ef:
            ef.write(f"Error saving config: {e}\n")

def run_detection():
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        from ai.Detection import Detection
        app = Detection()
        app.start()
    except Exception as e:
        with open("crash_log_detection.txt", "w") as f:
            f.write(str(e))

TRANSLATIONS = {
    "AR": {
        "title": "إعدادات الإيم",
        "fields": [
            ("حجم الدائرة:", "(رقم أكبر = مساحة أوسع للشبك)"),
            ("قوة السحب:", "(رقم أكبر = قوة تثبيت أسرع)"),
            ("سلاسة التثبيت:", "(رقم أكبر = نعومة وثبات بشري)"),
            ("سلاسة السحب:", "(رقم أكبر = سحب مخفي من بعيد)"),
            ("دقة الذكاء:", "(رقم أقل = رصد واستجابة أسرع)")
        ],
        "profile": "ملف الإعدادات الحالي:",
        "trigger": "زر تشغيل الإيمبوت:",
        "show_aim": "إظهار الإيم",
        "hide_aim": "إخفاء الإيم"
    },
    "EN": {
        "title": "Config Settings",
        "fields": [
            ("FOV Size:", "(Higher = wider scan area)"),
            ("Aim Speed:", "(Higher = stronger aim lock)"),
            ("Smooth In:", "(Higher = smoother locked aim)"),
            ("Smooth Out:", "(Higher = subtle stealth pull)"),
            ("Confidence:", "(Lower = faster AI tracking)")
        ],
        "profile": "Current Config Profile:",
        "trigger": "Aimbot Trigger Key:",
        "show_aim": "Show Aim",
        "hide_aim": "Hide Aim"
    }
}

class ClassicAHKUI:
    def __init__(self, root):
        self.root = root
        self.root.title("overwatch-ai")
        # زيادة الطول للتأكد من ظهور كل العناصر بدون تداخل
        self.root.geometry("340x560")
        self.root.resizable(False, False)
        
        self.root.wm_attributes("-toolwindow", True)
        self.root.wm_attributes("-topmost", True)  # يخلي البرنامج فوق اللعبة وكل النوافذ غصب
        
        # حماية ثلاثية لمنع الفلاش والاختفاء:
        # 1. البرنامج يبدأ مُنسحب (withdraw)
        # 2. شفافية صفر (alpha 0)
        # 3. إخفاء من شريط المهام (toolwindow)
        self.visible = False
        self.root.withdraw()
        self.root.attributes("-alpha", 0.0) 
        
        self.stealth_active = True # الحماية من التصوير مفعلة افتراضياً (مخفي عن الآخرين)
        
        # تشغيل مراقب F4
        self.f4_was_pressed = False
        self.root.after(100, self.monitor_f4_safe)
        
        style = ttk.Style()
        style.theme_use('vista')
        self.root.eval('tk::PlaceWindow . center')
        
        self.current_lang = "AR"
        # مراقبة الحالة الحالية (هل الرؤية مفعلة؟ هل الأيمبوت يعمل؟)
        self.visualize_active = False
        self.aimbot_running = False
        
        # تحميل رقم الإصدار
        self.app_version = "3.3"
        try:
            v_path = os.path.join(os.path.dirname(__file__), "version.json")
            if os.path.exists(v_path):
                with open(v_path, 'r') as f:
                    self.app_version = json.load(f).get("version", "1.9")
        except: pass
        
        main_frame = ttk.Frame(root, padding="15 15 15 15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # العنوان العلوي وأزرار اللغة
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.lbl_top_title = ttk.Label(top_frame, text=TRANSLATIONS[self.current_lang]["title"], font=("Segoe UI", 10, "bold"))
        self.lbl_top_title.pack(side=tk.LEFT)
        
        # زر اللغة الصغير يمين أعلى الشاشة (تبديل بنقرة واحدة)
        self.btn_lang = ttk.Button(top_frame, text="EN", width=3, command=self.toggle_lang)
        self.btn_lang.pack(side=tk.RIGHT)
        
        inputs_frame = ttk.Frame(main_frame)
        inputs_frame.pack(fill=tk.X)
        
        self.entries = {}
        self.label_names = []
        self.label_descs = []
        
        self.keys = ["aim_fov", "sens_comp", "smooth_in", "smooth_out", "confidence"]
        fields_text = TRANSLATIONS[self.current_lang]["fields"]
        
        row_idx = 0
        for i, key in enumerate(self.keys):
            lbl_name = ttk.Label(inputs_frame, text=fields_text[i][0])
            lbl_name.grid(row=row_idx, column=0, sticky="w", pady=(4, 0))
            self.label_names.append(lbl_name)
            
            ent = ttk.Entry(inputs_frame, width=14, justify="center")
            ent.grid(row=row_idx, column=1, sticky="e", pady=(4, 0), padx=(5, 0))
            self.entries[key] = ent
            
            row_idx += 1
            lbl_desc = ttk.Label(inputs_frame, text=fields_text[i][1], font=("Segoe UI", 8), foreground="#777777")
            lbl_desc.grid(row=row_idx, column=0, columnspan=2, sticky="w", pady=(0, 4))
            self.label_descs.append(lbl_desc)
            row_idx += 1
            
        btns_frame = ttk.Frame(main_frame)
        btns_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.btn_aim_on = ttk.Button(btns_frame, text="Aimbot ON", command=self.start_ai)
        self.btn_aim_on.grid(row=0, column=0, padx=3, pady=3, sticky="ew", ipady=2)
        
        self.btn_aim_off = ttk.Button(btns_frame, text="Aimbot OFF", command=self.stop_ai, state=tk.DISABLED)
        self.btn_aim_off.grid(row=0, column=1, padx=3, pady=3, sticky="ew", ipady=2)
        
        self.btn_load = ttk.Button(btns_frame, text="Load Profile", command=self.load_config)
        self.btn_load.grid(row=1, column=0, padx=3, pady=3, sticky="ew", ipady=2)
        
        self.btn_save = ttk.Button(btns_frame, text="Save Profile", command=self.save_config)
        self.btn_save.grid(row=1, column=1, padx=3, pady=3, sticky="ew", ipady=2)
        
        btns_frame.columnconfigure(0, weight=1)
        btns_frame.columnconfigure(1, weight=1)
        
        self.lbl_profile = ttk.Label(main_frame, text=TRANSLATIONS[self.current_lang]["profile"])
        self.lbl_profile.pack(anchor="w", pady=(15, 2))
        
        cfg_frame = ttk.Frame(main_frame)
        cfg_frame.pack(fill=tk.X)
        
        self.btn_prev = ttk.Button(cfg_frame, text="<", width=3, command=self.prev_config)
        self.btn_prev.pack(side=tk.LEFT)
        
        self.config_var = tk.StringVar(value="Default")
        self.config_ent = ttk.Entry(cfg_frame, textvariable=self.config_var, justify="center")
        self.config_ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        
        self.btn_next = ttk.Button(cfg_frame, text=">", width=3, command=self.next_config)
        self.btn_next.pack(side=tk.RIGHT)

        # اختيار زر التشغيل (Trigger Key)
        self.lbl_trigger = ttk.Label(main_frame, text=TRANSLATIONS[self.current_lang]["trigger"])
        self.lbl_trigger.pack(anchor="w", pady=(15, 2))
        
        self.key_map = {
            "Left Mouse": 0x01,
            "Right Mouse": 0x02,
            "Middle Mouse": 0x04,
            "XButton 1": 0x05,
            "XButton 2": 0x06,
            "Shift": 0x10,
            "Ctrl": 0x11,
            "Alt": 0x12,
            "Space": 0x20
        }
        
        self.trigger_keys_list = list(self.key_map.keys())
        self.current_key_idx = 4 # Default to XButton 2 (index 4)
        
        trigger_frame = ttk.Frame(main_frame)
        trigger_frame.pack(fill=tk.X)
        
        self.btn_key_prev = ttk.Button(trigger_frame, text="<", width=3, command=self.prev_key)
        self.btn_key_prev.pack(side=tk.LEFT)
        
        self.trigger_var = tk.StringVar(value=self.trigger_keys_list[self.current_key_idx])
        self.trigger_ent = ttk.Entry(trigger_frame, textvariable=self.trigger_var, justify="center", state="readonly")
        self.trigger_ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        
        self.btn_key_next = ttk.Button(trigger_frame, text=">", width=3, command=self.next_key)
        self.btn_key_next.pack(side=tk.RIGHT)

        # حاوية سفلية للنسخة وزر الإخفاء/الإظهار - نضعها هنا بعد كل العناصر
        bottom_info_frame = ttk.Frame(main_frame)
        bottom_info_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))

        # زر التحكم في الظهور بالتصوير (Stealth Toggle)
        self.stealth_active = True 
        self.btn_stealth = ttk.Button(bottom_info_frame, text=TRANSLATIONS[self.current_lang]["show_aim"], 
                                    width=11, command=self.toggle_stealth)
        self.btn_stealth.pack(side=tk.LEFT)
        
        # زر العين الجديد (AI Vision)
        # 👁️ = Eye on, 🕶️ = Eye off
        self.btn_vision = ttk.Button(bottom_info_frame, text="👁️", width=4, command=self.toggle_vision)
        self.btn_vision.pack(side=tk.LEFT, padx=(5, 0))

        # v1.9
        self.lbl_ver_num = ttk.Label(bottom_info_frame, text=f"v{self.app_version}", font=("Segoe UI", 8, "bold"), foreground="#666666")
        self.lbl_ver_num.pack(side=tk.RIGHT)

        self.configs_list = []
        self.current_cfg_idx = 0
        self.process = None # العملية الخلفية
        
        self.refresh_configs()
        self.load_active_config()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_lang(self):
        # تبديل اللغة الحالية
        new_lang = "EN" if self.current_lang == "AR" else "AR"
        self.set_lang(new_lang)

    def set_lang(self, lang):
        self.current_lang = lang
        # تحديث زر اللغة ليظهر اللغة "الأخرى" التي سينتقل لها المستخدم المرة القادمة
        self.btn_lang.config(text="AR" if lang == "EN" else "EN")
        
        self.lbl_top_title.config(text=TRANSLATIONS[lang]["title"])
        
        fields_text = TRANSLATIONS[lang]["fields"]
        for i in range(len(self.keys)):
            self.label_names[i].config(text=fields_text[i][0])
            self.label_descs[i].config(text=fields_text[i][1])
            
        self.lbl_profile.config(text=TRANSLATIONS[lang]["profile"])
        self.lbl_trigger.config(text=TRANSLATIONS[lang]["trigger"])
        
        # تحديث نص زر التخفي حسب الحالة الحالية (Stealth Active = Hidden from capture)
        if self.stealth_active:
            self.btn_stealth.config(text=TRANSLATIONS[lang]["show_aim"]) # نص الزر: إظهار في التصوير
        else:
            self.btn_stealth.config(text=TRANSLATIONS[lang]["hide_aim"]) # نص الزر: إخفاء من التصوير

    def apply_stealth_capture(self):
        # إخفاء النافذة من برامج التسجيل والديسكورد (التخفي)
        try:
            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if not hwnd: hwnd = self.root.winfo_id()
            if hwnd:
                # 0x11 = WDA_EXCLUDEFROMCAPTURE
                ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x11)
                self.stealth_active = True
        except Exception: pass

    def disable_stealth_capture(self):
        # إظهار النافذة في برامج التسجيل (إلغاء التخفي)
        try:
            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if not hwnd: hwnd = self.root.winfo_id()
            if hwnd:
                # 0x00 = WDA_NONE
                ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x01 if os.name == 'nt' else 0x00)
                # ملحوظة: بعض الأجهزة تحتاج 0x01 لإعادة الإظهار وبعضها 0x00
                ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x00)
                self.stealth_active = False
        except Exception: pass

    def toggle_stealth(self):
        if self.stealth_active:
            self.disable_stealth_capture()
            self.btn_stealth.config(text=TRANSLATIONS[self.current_lang]["hide_aim"])
        else:
            self.apply_stealth_capture()
            self.btn_stealth.config(text=TRANSLATIONS[self.current_lang]["show_aim"])

    def toggle_vision(self):
        # تبديل ظهور نافذة المعاينة (العين)
        self.visualize_active = not self.visualize_active
        self.btn_vision.config(text="👁️" if self.visualize_active else "🚫👁️")
        
        # تحديث ملف الإعدادات ليقرأه السكربت في الخلفية
        vals = self.get_current_values()
        save_active_config(vals)
        
        # التأكد من أن العملية تعمل
        self.ensure_ai_running()

    def ensure_ai_running(self):
        if self.process is None or not self.process.is_alive():
            self.process = multiprocessing.Process(target=run_detection)
            self.process.start()

    def monitor_f4_safe(self):
        # مراقبة F4 بشكل آمن لتفادي تجمد الواجهة
        f4_key = 0x73
        is_pressed = win32api.GetAsyncKeyState(f4_key) & 0x8000
        if is_pressed and not self.f4_was_pressed:
            self.toggle_visibility()
        self.f4_was_pressed = is_pressed
        self.root.after(100, self.monitor_f4_safe)

    def toggle_visibility(self):
        if self.visible:
            self.root.attributes("-alpha", 0.0)
            self.root.withdraw() # ننسحب تماماً
            self.visible = False
        else:
            self.root.deiconify() # نظهر النافذة
            self.root.attributes("-alpha", 1.0) # نلغي الشفافية
            self.root.wm_attributes("-topmost", True) # نأكد أنها فوق اللعبة
            self.root.focus_force() # نطلب التركيز
            self.visible = True
            
            # نطبق الحماية من التصوير فوراً عشان "أنت بس اللي تشوفه"
            if self.stealth_active:
                self.root.after(10, self.apply_stealth_capture)

    def refresh_configs(self):
        files = glob.glob(os.path.join(CONFIG_DIR, "*.json"))
        names = [os.path.basename(f).replace(".json", "") for f in files]
        self.configs_list = names if names else ["Default"]
        
        if self.config_var.get() in self.configs_list:
            self.current_cfg_idx = self.configs_list.index(self.config_var.get())
        else:
            self.current_cfg_idx = 0
            self.config_var.set(self.configs_list[self.current_cfg_idx])

    def next_config(self):
        if not self.configs_list: return
        self.current_cfg_idx = (self.current_cfg_idx + 1) % len(self.configs_list)
        self.config_var.set(self.configs_list[self.current_cfg_idx])

    def prev_config(self):
        if not self.configs_list: return
        self.current_cfg_idx = (self.current_cfg_idx - 1) % len(self.configs_list)
        self.config_var.set(self.configs_list[self.current_cfg_idx])

    def next_key(self):
        self.current_key_idx = (self.current_key_idx + 1) % len(self.trigger_keys_list)
        self.trigger_var.set(self.trigger_keys_list[self.current_key_idx])

    def prev_key(self):
        self.current_key_idx = (self.current_key_idx - 1) % len(self.trigger_keys_list)
        self.trigger_var.set(self.trigger_keys_list[self.current_key_idx])

    def load_active_config(self):
        if os.path.exists(ACTIVE_CFG_PATH):
            try:
                with open(ACTIVE_CFG_PATH, "r") as f:
                    data = json.load(f)
                    self.update_entries(data)
            except:
                pass
        else:
            self.update_entries(DEFAULT_CONFIG)

    def update_entries(self, data):
        for key, ent in self.entries.items():
            ent.delete(0, tk.END)
            ent.insert(0, str(data.get(key, DEFAULT_CONFIG[key])))
        
        trigger_val = data.get("trigger_key", "XButton 2")
        self.trigger_var.set(trigger_val)
        if trigger_val in self.trigger_keys_list:
            self.current_key_idx = self.trigger_keys_list.index(trigger_val)

    def get_current_values(self):
        vals = {}
        for key, ent in self.entries.items():
            try:
                vals[key] = float(ent.get())
            except:
                vals[key] = DEFAULT_CONFIG[key]
        
        selected_key_name = self.trigger_var.get()
        vals["trigger_key"] = selected_key_name 
        vals["trigger_key_hex"] = hex(self.key_map.get(selected_key_name, 0x06))
        
        # إضافة إعدادات الرؤية والأيمبوت للقيم المحفوظة
        vals["visualize"] = self.visualize_active
        vals["enable_aim"] = self.aimbot_running
        return vals

    def save_config(self):
        name = self.config_var.get().strip()
        if not name:
            name = "MyConfig"
            self.config_var.set(name)
        
        vals = self.get_current_values()
        
        cfg_path = os.path.join(CONFIG_DIR, f"{name}.json")
        with open(cfg_path, "w") as f:
            json.dump(vals, f, indent=4)
        
        save_active_config(vals)
        self.refresh_configs()
        self.config_var.set(name)
        
        if self.process and self.process.is_alive():
            self.stop_ai()
            self.root.after(300, self.start_ai) 
        else:
            pass 

    def load_config(self):
        name = self.config_var.get().strip()
        cfg_path = os.path.join(CONFIG_DIR, f"{name}.json")
        if os.path.exists(cfg_path):
            with open(cfg_path, "r") as f:
                data = json.load(f)
                self.update_entries(data)
                save_active_config(data)
            if self.process and self.process.is_alive():
                self.stop_ai()
                self.root.after(300, self.start_ai)
        else:
            messagebox.showerror("Error", "Save file not found!")

    def start_ai(self):
        # تشغيل وضع الأيمبوت (لكن السكربت يعمل فعلياً في الخلفية دائماً عند تشغيله)
        self.aimbot_running = True
        vals = self.get_current_values()
        save_active_config(vals)
        
        self.ensure_ai_running()
        
        self.btn_aim_on.config(state=tk.DISABLED)
        self.btn_aim_off.config(state=tk.NORMAL)

    def stop_ai(self):
        # تعطيل خاصية السحب/الأيمبوت ولكن مع إبقاء العملية تعمل (لميزة العين)
        self.aimbot_running = False
        vals = self.get_current_values()
        save_active_config(vals)
        
        self.btn_aim_on.config(state=tk.NORMAL)
        self.btn_aim_off.config(state=tk.DISABLED)

    def on_closing(self):
        # ضمان قتل كل العمليات المتبقية للذكاء الاصطناعي في الخلفية
        try:
            # نوقف الإيمبوت أولاً بشكل نظيف
            self.stop_ai()
            
            # ثم نغلق العمليات الفرعية للبرنامج نفسه فقط
            for child in multiprocessing.active_children():
                pid = child.pid
                import subprocess
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                child.kill()
        except:
            pass
        
        self.root.destroy()
        # الخروج القسري النهائي لضمان عدم بقاء النافذة في الذاكرة
        os._exit(0) 

if __name__ == '__main__':
    multiprocessing.freeze_support()
    root = tk.Tk()
    
    # الإخفاء المطلق قبل أي شيء (يمنع الفلاش في كل كروت الشاشة)
    root.withdraw()
    root.attributes("-alpha", 0.0)
    
    try:
        app = ClassicAHKUI(root)
        root.mainloop()
    except Exception as e:
        # سجل أخطاء في حال تعطل البرنامج بصمت
        with open("crash_log.txt", "w") as f:
            f.write(str(e))
