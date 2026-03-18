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
import subprocess

# --- [v22.0 ULTIMATE FIX - COMPACT & VISION REPAIR] ---

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "configs")
ACTIVE_CFG_PATH = os.path.join(BASE_DIR, "config.json")

if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

DEFAULT_CONFIG = {
    "aim_fov": 75.0,
    "sens_comp": 3.0,
    "smooth_in": 1.3,
    "smooth_out": 3.8,
    "confidence": 0.30,
    "trigger_key": "XButton 2",
    "visualize": False,
    "enable_aim": False
}

def save_active_config(cfg):
    try:
        with open(ACTIVE_CFG_PATH, "w") as f:
            json.dump(cfg, f, indent=4)
            f.flush(); os.fsync(f.fileno())
    except: pass

def run_detection():
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        from ai.Detection import Detection
        app = Detection(); app.start()
    except Exception as e:
        with open("engine_fatal_error.txt", "w") as f: f.write(str(e))

TRANSLATIONS = {
    "AR": {
        "title": "Config Settings",
        "fields": [("FOV Size:", "(رقم أكبر = مساحة أوسع)"), ("Aim Speed:", "(رقم أكبر = قوة تثبيت)"), ("Smooth In:", "(رقم أكبر = نعومة وضبط)"), ("Smooth Out:", "(رقم أكبر = سحب مخفي)"), ("Confidence:", "(رقم أقل = رصد أسرع)")],
        "profile": "ملف الإعدادات الحالي:",
        "trigger": "زر تشغيل الإيمبوت:",
        "show_aim": "إظهار الإيم",
        "hide_aim": "إخفاء الإيم"
    },
    "EN": {
        "title": "Config Settings",
        "fields": [("FOV Size:", "(Higher = wider scan)"), ("Aim Speed:", "(Higher = stronger aim)"), ("Smooth In:", "(Higher = smoother aim)"), ("Smooth Out:", "(Higher = subtle pull)"), ("Confidence:", "(Lower = faster AI)")],
        "profile": "Current Profile:",
        "trigger": "Aimbot Trigger Key:",
        "show_aim": "Show Aim",
        "hide_aim": "Hide Aim"
    }
}

class ClassicAHKUI:
    def __init__(self, root):
        self.root = root
        self.root.title("overwatch-ai")
        self.root.geometry("340x480") # ULTIMATE COMPACT
        self.root.resizable(False, False)
        self.root.wm_attributes("-toolwindow", True); self.root.wm_attributes("-topmost", True)
        
        self.visible = False; self.root.withdraw(); self.root.attributes("-alpha", 0.0) 
        self.stealth_active = True; self.keys_pressed = {}
        
        # Zero Audio - Confirmed
        
        style = ttk.Style(); style.theme_use('vista')
        self.root.eval('tk::PlaceWindow . center')
        
        self.current_lang = "AR"; self.visualize_active = False; self.aimbot_running = False; self.app_version = "24.0"; self.process = None
        
        main_frame = ttk.Frame(root, padding="10 10 10 10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        top_frame = ttk.Frame(main_frame); top_frame.pack(fill=tk.X, pady=(0, 5))
        self.lbl_top_title = ttk.Label(top_frame, text=TRANSLATIONS[self.current_lang]["title"], font=("Segoe UI", 10, "bold")); self.lbl_top_title.pack(side=tk.LEFT)
        self.btn_lang = ttk.Button(top_frame, text="EN", width=3, command=self.toggle_lang); self.btn_lang.pack(side=tk.RIGHT)
        
        # Power Levels (Elite Header)
        presets_frame = ttk.LabelFrame(main_frame, text="Power Levels", padding=5)
        presets_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(presets_frame, text="Legit", width=8, command=lambda: self.apply_preset("Legit")).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(presets_frame, text="Normal", width=8, command=lambda: self.apply_preset("Normal")).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(presets_frame, text="High", width=8, command=lambda: self.apply_preset("High")).pack(side=tk.LEFT, expand=True, padx=2)

        # Config Inputs (Ultra Compact)
        inputs_frame = ttk.Frame(main_frame); inputs_frame.pack(fill=tk.X)
        self.entries = {}; self.label_names = []; self.label_descs = []
        self.keys = ["aim_fov", "sens_comp", "smooth_in", "smooth_out", "confidence"]
        fields_text = TRANSLATIONS[self.current_lang]["fields"]
        for i, key in enumerate(self.keys):
            row = ttk.Frame(inputs_frame); row.pack(fill=tk.X, pady=1)
            lbl = ttk.Label(row, text=fields_text[i][0]); lbl.pack(side=tk.LEFT)
            self.label_names.append(lbl)
            ent = ttk.Entry(row, width=10, justify="center"); ent.pack(side=tk.RIGHT)
            self.entries[key] = ent
            desc = ttk.Label(inputs_frame, text=fields_text[i][1], font=("Segoe UI", 7), foreground="#777777")
            desc.pack(anchor="w", pady=(0, 2)); self.label_descs.append(desc)

        # Control Buttons
        c_frame = ttk.Frame(main_frame); c_frame.pack(fill=tk.X, pady=(5, 0))
        self.btn_aim_on = ttk.Button(c_frame, text="Aimbot ON", command=self.start_ai); self.btn_aim_on.grid(row=0, column=0, padx=2, pady=1, sticky="ew")
        self.btn_aim_off = ttk.Button(c_frame, text="Aimbot OFF", command=self.stop_ai, state=tk.DISABLED); self.btn_aim_off.grid(row=0, column=1, padx=2, pady=1, sticky="ew")
        self.btn_load = ttk.Button(c_frame, text="Load Profile", command=self.load_config); self.btn_load.grid(row=1, column=0, padx=2, pady=1, sticky="ew")
        self.btn_save = ttk.Button(c_frame, text="Save Profile", command=self.save_config); self.btn_save.grid(row=1, column=1, padx=2, pady=1, sticky="ew")
        c_frame.columnconfigure(0, weight=1); c_frame.columnconfigure(1, weight=1)
        
        # Profile/Trigger Selectors
        sel_frame = ttk.Frame(main_frame); sel_frame.pack(fill=tk.X, pady=(5, 0))
        self.lbl_profile = ttk.Label(sel_frame, text=TRANSLATIONS[self.current_lang]["profile"], font=("Segoe UI", 8)); self.lbl_profile.pack(anchor="w")
        p_row = ttk.Frame(sel_frame); p_row.pack(fill=tk.X)
        ttk.Button(p_row, text="<", width=3, command=self.prev_config).pack(side=tk.LEFT)
        self.config_var = tk.StringVar(value="Default")
        ttk.Entry(p_row, textvariable=self.config_var, justify="center").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(p_row, text=">", width=3, command=self.next_config).pack(side=tk.RIGHT)

        self.lbl_trigger = ttk.Label(sel_frame, text=TRANSLATIONS[self.current_lang]["trigger"], font=("Segoe UI", 8)); self.lbl_trigger.pack(anchor="w", pady=(5, 0))
        t_row = ttk.Frame(sel_frame); t_row.pack(fill=tk.X)
        self.key_map = {"Left Mouse": 0x01, "Right Mouse": 0x02, "Middle Mouse": 0x04, "XButton 1": 0x05, "XButton 2": 0x06, "Shift": 0x10, "Ctrl": 0x11, "Alt": 0x12, "Space": 0x20}
        self.trigger_keys_list = list(self.key_map.keys()); self.current_key_idx = 4
        ttk.Button(t_row, text="<", width=3, command=self.prev_key).pack(side=tk.LEFT)
        self.trigger_var = tk.StringVar(value=self.trigger_keys_list[self.current_key_idx])
        ttk.Entry(t_row, textvariable=self.trigger_var, justify="center", state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(t_row, text=">", width=3, command=self.next_key).pack(side=tk.RIGHT)

        # Bottom Dock (ZERO PADDING)
        bot_frame = ttk.Frame(main_frame); bot_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        self.btn_stealth = ttk.Button(bot_frame, text=TRANSLATIONS[self.current_lang]["show_aim"], width=10, command=self.toggle_stealth); self.btn_stealth.pack(side=tk.LEFT)
        self.btn_vision = ttk.Button(bot_frame, text="👁️", width=4, command=self.toggle_vision); self.btn_vision.pack(side=tk.LEFT, padx=(5,0))
        ttk.Label(bot_frame, text=f"v{self.app_version}", font=("Segoe UI", 7), foreground="#999999").pack(side=tk.RIGHT)

        self.configs_list = []; self.current_cfg_idx = 0; self.process = None
        self.refresh_configs(); self.load_active_config(); self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.after(100, self.monitor_hotkeys)

    def monitor_hotkeys(self):
        hotkeys = {"F4": 0x73, "HOME": 0x24, "INSERT": 0x2D}
        for name, vk in hotkeys.items():
            state = win32api.GetAsyncKeyState(vk) & 0x8000
            if state:
                if not self.keys_pressed.get(name): self.toggle_visibility(); self.keys_pressed[name] = True
            else: self.keys_pressed[name] = False
        self.root.after(100, self.monitor_hotkeys)

    def toggle_visibility(self):
        if self.visible: self.root.attributes("-alpha", 0.0); self.root.withdraw(); self.visible = False
        else: self.root.deiconify(); self.root.attributes("-alpha", 1.0); self.root.wm_attributes("-topmost", True); self.root.focus_force(); self.visible = True
        if self.stealth_active: self.root.after(10, self.apply_stealth_capture)

    def apply_preset(self, level):
        p = {"Legit": {"aim_fov": 75.0, "sens_comp": 3.0, "smooth_in": 1.6, "smooth_out": 4.5, "confidence": 0.35},
             "Normal": {"aim_fov": 110.0, "sens_comp": 4.5, "smooth_in": 1.4, "smooth_out": 3.0, "confidence": 0.30},
             "High": {"aim_fov": 160.0, "sens_comp": 6.5, "smooth_in": 1.2, "smooth_out": 2.2, "confidence": 0.25}}
        if level in p: self.update_entries(p[level]); save_active_config(self.get_current_values())

    def toggle_lang(self): self.set_lang("EN" if self.current_lang == "AR" else "AR")
    def set_lang(self, lang):
        self.current_lang = lang; self.btn_lang.config(text="AR" if lang == "EN" else "EN"); self.lbl_top_title.config(text=TRANSLATIONS[lang]["title"])
        f_t = TRANSLATIONS[lang]["fields"]
        for i in range(len(self.keys)): self.label_names[i].config(text=f_t[i][0]); self.label_descs[i].config(text=f_t[i][1])
        self.lbl_profile.config(text=TRANSLATIONS[lang]["profile"]); self.lbl_trigger.config(text=TRANSLATIONS[lang]["trigger"])
        self.btn_stealth.config(text=TRANSLATIONS[lang]["show_aim"] if self.stealth_active else TRANSLATIONS[lang]["hide_aim"])

    def apply_stealth_capture(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id()) or self.root.winfo_id()
            if hwnd: ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x11); self.stealth_active = True
        except: pass

    def disable_stealth_capture(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id()) or self.root.winfo_id()
            if hwnd: ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x00); self.stealth_active = False
        except: pass

    def toggle_stealth(self):
        if self.stealth_active: self.disable_stealth_capture(); self.btn_stealth.config(text=TRANSLATIONS[self.current_lang]["hide_aim"])
        else: self.apply_stealth_capture(); self.btn_stealth.config(text=TRANSLATIONS[self.current_lang]["show_aim"])

    def toggle_vision(self): 
        self.visualize_active = not self.visualize_active; self.btn_vision.config(text="👁️" if self.visualize_active else "🚫👁️")
        save_active_config(self.get_current_values()); self.ensure_ai_running()
        
    def ensure_ai_running(self):
        if self.process is None or not self.process.is_alive(): self.process = multiprocessing.Process(target=run_detection); self.process.start()
    def start_ai(self): self.aimbot_running = True; save_active_config(self.get_current_values()); self.ensure_ai_running(); self.btn_aim_on.config(state=tk.DISABLED); self.btn_aim_off.config(state=tk.NORMAL)
    def stop_ai(self): self.aimbot_running = False; save_active_config(self.get_current_values()); self.btn_aim_on.config(state=tk.NORMAL); self.btn_aim_off.config(state=tk.DISABLED)
    def refresh_configs(self):
        fs = glob.glob(os.path.join(CONFIG_DIR, "*.json")); ns = [os.path.basename(f).replace(".json", "") for f in fs]; self.configs_list = ns if ns else ["Default"]
        if self.config_var.get() in self.configs_list: self.current_cfg_idx = self.configs_list.index(self.config_var.get())
        else: self.current_cfg_idx = 0; self.config_var.set(self.configs_list[0])
    def next_config(self): self.current_cfg_idx = (self.current_cfg_idx + 1) % len(self.configs_list); self.config_var.set(self.configs_list[self.current_cfg_idx])
    def prev_config(self): self.current_cfg_idx = (self.current_cfg_idx - 1) % len(self.configs_list); self.config_var.set(self.configs_list[self.current_cfg_idx])
    def next_key(self): self.current_key_idx = (self.current_key_idx + 1) % len(self.trigger_keys_list); self.trigger_var.set(self.trigger_keys_list[self.current_key_idx])
    def prev_key(self): self.current_key_idx = (self.current_key_idx - 1) % len(self.trigger_keys_list); self.trigger_var.set(self.trigger_keys_list[self.current_key_idx])
    def load_active_config(self):
        if os.path.exists(ACTIVE_CFG_PATH):
            try:
                with open(ACTIVE_CFG_PATH, "r") as f: d = json.load(f); self.update_entries(d)
            except: pass
        else: self.update_entries(DEFAULT_CONFIG)
    def update_entries(self, d):
        for k, e in self.entries.items(): e.delete(0, tk.END); e.insert(0, str(d.get(k, DEFAULT_CONFIG.get(k, ""))))
        t = d.get("trigger_key", "XButton 2"); self.trigger_var.set(t)
        if t in self.trigger_keys_list: self.current_key_idx = self.trigger_keys_list.index(t)
    def get_current_values(self):
        vals = {}
        for k, e in self.entries.items():
            try: vals[k] = float(e.get())
            except: vals[k] = DEFAULT_CONFIG.get(k, 0)
        s = self.trigger_var.get(); vals["trigger_key"] = s; vals["trigger_key_hex"] = hex(self.key_map.get(s, 0x06)); vals["visualize"] = self.visualize_active; vals["enable_aim"] = self.aimbot_running; return vals
    def save_config(self):
        n = self.config_var.get().strip() or "MyConfig"; v = self.get_current_values(); cp = os.path.join(CONFIG_DIR, f"{n}.json")
        with open(cp, "w") as f: json.dump(v, f, indent=4)
        save_active_config(v); self.refresh_configs(); self.config_var.set(n)
        if self.process and self.process.is_alive(): self.stop_ai(); self.root.after(300, self.start_ai)
    def load_config(self):
        n = self.config_var.get().strip(); cp = os.path.join(CONFIG_DIR, f"{n}.json")
        if os.path.exists(cp):
            with open(cp, "r") as f: d = json.load(f); self.update_entries(d); save_active_config(d)
            if self.process and self.process.is_alive(): self.stop_ai(); self.root.after(300, self.start_ai)
        else: messagebox.showerror("Error", "File not found!")
    def on_closing(self):
        try:
            self.stop_ai()
            for c in multiprocessing.active_children(): subprocess.call(['taskkill', '/F', '/T', '/PID', str(c.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); c.kill()
        except: pass
        self.root.destroy(); os._exit(0) 

if __name__ == '__main__':
    multiprocessing.freeze_support()
    root = tk.Tk(); root.withdraw(); root.attributes("-alpha", 0.0)
    try: app = ClassicAHKUI(root); root.mainloop()
    except Exception as e:
        with open("crash_log.txt", "w") as f: f.write(str(e))
