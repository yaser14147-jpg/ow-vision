import tkinter as tk
from tkinter import ttk, messagebox
import multiprocessing
import sys
import os
import json
import glob
import ctypes

# إخفاء شاشة الـ CMD السوداء بالكامل عن طريق الـ Kernel
def hide_console():
    try:
        hwnd_cmd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd_cmd:
            ctypes.windll.user32.ShowWindow(hwnd_cmd, 0)
    except Exception:
        pass
hide_console()

CONFIG_DIR = r"C:\Users\yaser\Desktop\AI\ow-vision\scripts\configs"
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

DEFAULT_CONFIG = {
    "aim_fov": 75,
    "sens_comp": 2.6,
    "smooth_in": 1.3,
    "smooth_out": 3.8,
    "confidence": 0.30,
    "trigger_key": "XButton 2"
}

ACTIVE_CFG_PATH = r"C:\Users\yaser\Desktop\AI\ow-vision\scripts\config.json"

def save_active_config(cfg):
    with open(ACTIVE_CFG_PATH, "w") as f:
        json.dump(cfg, f, indent=4)

def run_detection():
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        from ai.Detection import Detection
        app = Detection()
    except Exception as e:
        print(f"Error: {e}")

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
        "trigger": "زر تشغيل الإيمبوت:"
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
        "trigger": "Aimbot Trigger Key:"
    }
}

class ClassicAHKUI:
    def __init__(self, root):
        self.root = root
        self.root.title("overwatch-ai")
        # تم تكبير الطول قليلاً ليسع زر اختيار المفتاح
        self.root.geometry("340x540")
        self.root.resizable(False, False)
        
        self.root.wm_attributes("-toolwindow", True)
        self.root.after(100, self.apply_stealth_capture)
        
        style = ttk.Style()
        style.theme_use('vista')
        self.root.eval('tk::PlaceWindow . center')
        
        self.process = None
        self.current_lang = "AR"
        
        # تحميل رقم الإصدار من ملف version.json
        self.app_version = "1.0"
        try:
            v_path = os.path.join(os.path.dirname(__file__), "version.json")
            if os.path.exists(v_path):
                with open(v_path, 'r') as f:
                    self.app_version = json.load(f).get("version", "1.0")
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

        # إضافة رقم الإصدار تحت يمين الواجهة بشكل واضح
        # v1.0
        self.lbl_ver_num = ttk.Label(main_frame, text=f"v{self.app_version}", font=("Segoe UI", 8, "bold"), foreground="#666666")
        self.lbl_ver_num.pack(side=tk.BOTTOM, anchor="se", pady=(15, 0))

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

        self.configs_list = []
        self.current_cfg_idx = 0
        
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

    def apply_stealth_capture(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            WDA_EXCLUDEFROMCAPTURE = 0x00000011
            ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
        except Exception as e:
            print("Stealth Mode Error:", e)

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
        vals["trigger_key"] = selected_key_name # حفظ الاسم للملف
        vals["trigger_key_hex"] = hex(self.key_map.get(selected_key_name, 0x06)) # الكود للتشغيل
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
        vals = self.get_current_values()
        save_active_config(vals)
        if self.process is None or not self.process.is_alive():
            self.process = multiprocessing.Process(target=run_detection)
            self.process.start()
            
            self.btn_aim_on.config(state=tk.DISABLED)
            self.btn_aim_off.config(state=tk.NORMAL)

    def stop_ai(self):
        if self.process and self.process.is_alive():
            try:
                # نحصل على رقم العملية (PID) لقتلها هي فقط دون التأثير على محرك الـ VS Code
                pid = self.process.pid
                # محاولة الإيقاف الطبيعي
                self.process.terminate()
                self.process.join(timeout=0.5)
                
                # إذا لم تنتهِ، نقتلها قسرياً برقمها الخاص فقط (بشكل نظيف جداً)
                if self.process.is_alive():
                    import subprocess
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass
            
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
    app = ClassicAHKUI(root)
    root.mainloop()
