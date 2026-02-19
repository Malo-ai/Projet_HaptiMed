import sys, os, math, time, csv, random
import numpy as np
from PyQt6.QtWidgets import (QApplication, QWidget, QDialog, QFormLayout, QSpinBox, 
                             QLineEdit, QDialogButtonBox, QVBoxLayout, QLabel)
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QTabletEvent
from PyQt6.QtMultimedia import QSoundEffect

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_PATH = os.path.join(BASE_DIR, "data", "raw")

if not os.path.exists(DATA_RAW_PATH):
    os.makedirs(DATA_RAW_PATH, exist_ok=True)

TUNNEL_LEVELS = [{"R": 350, "W": 5}] 

CONFIG = {
    "TARGET_RAW": 3200, 
    "FORCE_TOLERANCE_PCT": 10, 
    "RAW_MAX": 8192,
    "BASE_THICKNESS": 6,        
    "TEMPS_MAX_ESSAI": 15, 
    "TEMPS_REPOS": 3, 
    "TEMPS_PAUSE_LONGUE": 20,
    "REPS_PER_ID": 10,          
    "STATIONARY_DELAY": 1.0,    
    "VELOCITY_THRESHOLD": 10.0
}

# --- ÉTAPE 1 : CONFIGURATION DU PARTICIPANT ---
class ConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HaptiMed - Configuration")
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.input_id = QLineEdit()
        self.input_id.setPlaceholderText("ex: P01")
        form.addRow("ID Participant :", self.input_id)
        
        self.input_target = QSpinBox()
        self.input_target.setRange(100, 8000)
        self.input_target.setValue(CONFIG["TARGET_RAW"])
        form.addRow("Cible Force (MVC) :", self.input_target)
        
        self.input_tol = QSpinBox()
        self.input_tol.setRange(1, 50)
        self.input_tol.setValue(CONFIG["FORCE_TOLERANCE_PCT"])
        form.addRow("Tolérance (%) :", self.input_tol)
        
        self.input_reps = QSpinBox()
        self.input_reps.setRange(1, 100)
        self.input_reps.setValue(CONFIG["REPS_PER_ID"])
        form.addRow("Nbr Répétitions / condition :", self.input_reps)
        
        layout.addLayout(form)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btns.accepted.connect(self.accept)
        layout.addWidget(btns)
        self.setLayout(layout)
        
    def get_settings(self):
        return {
            "ID": self.input_id.text().strip(), 
            "TARGET": self.input_target.value(), 
            "TOL_PCT": self.input_tol.value(),
            "REPS": self.input_reps.value()
        }

# --- ÉTAPE 2 : CONSIGNES SPÉCIFIQUES ---
class InstructionDialog(QDialog):
    def __init__(self, task_type, has_feedback, is_first=False):
        super().__init__()
        self.setWindowTitle("Consignes Expérimentales")
        self.setFixedSize(750, 500)
        layout = QVBoxLayout()
        
        title_text = "BIENVENUE DANS L'EXPÉRIENCE" if is_first else "CHANGEMENT DE CONDITION"
        layout.addWidget(QLabel(f"<h1 style='color:#2c3e50; text-align:center;'>{title_text}</h1>"))

        # MODIFICATION DU NOM ICI
        condition_title = f"{'FORCE - VITESSE - PRÉCISION' if task_type == 'FVP' else 'VITESSE - PRÉCISION'} - {'AVEC FEEDBACK' if has_feedback else 'SANS FEEDBACK'}"
        layout.addWidget(QLabel(f"<h2 style='color:#2980b9; text-align:center;'>{condition_title}</h2>"))

        instr = "<b>DÉPART :</b><br>Placez-vous sur la croix en bas. "
        if task_type == "FVP":
            instr += "Calibrez votre pression pour rendre la croix <b style='color:green;'>VERTE</b>. Maintenez 1 seconde.<br><br>"
        else:
            instr += "Touchez la tablette pour rendre la croix <b style='color:green;'>VERTE</b>. Maintenez 1 seconde.<br><br>"

        instr += "<b>PENDANT LE DESSIN :</b><br>"
        instr += "Allez le plus vite possible tout en restant dans le tunnel.<br>"

        if has_feedback:
            instr += "• Un trait de couleur suivra votre stylet.<br>"
            instr += "• Si vous sortez du tunnel, le tracé devient <b style='color:red;'>ROUGE</b>.<br>"
            if task_type == "FVP":
                instr += "• Force correcte = <b style='color:green;'>VERT</b>.<br>"
                instr += "• Pression trop faible = <b style='color:blue;'>BLEU</b>.<br>"
                instr += "• Pression trop forte = <b style='color:orange;'>ORANGE</b>.<br>"
            else:
                instr += "• Tracé correct = <b style='color:green;'>VERT</b>.<br>"
        else:
            instr += "• <i style='color:#c0392b;'>Attention : Il n'y aura aucun trait de couleur pour vous aider.</i><br>"
            instr += "• Vous ne verrez que le pointeur de votre stylet.<br>"
            if task_type == "FVP":
                instr += "• Fiez-vous à vos sensations physiques pour maintenir la force mémorisée au départ.<br>"

        desc = QLabel(instr)
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 16px; padding: 20px; background: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 10px;")
        layout.addWidget(desc)
        
        btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btn.accepted.connect(self.accept)
        layout.addWidget(btn)
        self.setLayout(layout)

# --- ÉTAPE 3 : L'EXPÉRIENCE ---
class SteeringExpe(QWidget):
    def __init__(self, s):
        super().__init__()
        self.pid = s["ID"] if s["ID"] else "TEST"
        CONFIG["TARGET_RAW"] = s["TARGET"]
        CONFIG["FORCE_TOLERANCE_PCT"] = s["TOL_PCT"]
        CONFIG["REPS_PER_ID"] = s["REPS"]
        
        margin = CONFIG["TARGET_RAW"] * (CONFIG["FORCE_TOLERANCE_PCT"] / 100.0)
        self.f_min = CONFIG["TARGET_RAW"] - margin; self.f_max = CONFIG["TARGET_RAW"] + margin
        
        self.setStyleSheet("background-color: black;")
        self.showFullScreen(); self.setCursor(Qt.CursorShape.BlankCursor); self.beep = QSoundEffect(self)
        
        self.pos = QPointF(0,0); self.pressure = 0.0
        self.buffer_raw = []; self.current_trajectory = [] 
        
        self.sequence = []
        conditions = [("VP", False), ("VP", True), ("FVP", False), ("FVP", True)]
        random.shuffle(conditions) 
        
        for task, fb in conditions:
            essais_bloc = []
            for rep in range(CONFIG["REPS_PER_ID"]):
                essais_bloc.append({
                    "Task": task, "Feedback": fb, "IDc_Level": 1, 
                    "R": TUNNEL_LEVELS[0]["R"], "W": TUNNEL_LEVELS[0]["W"], "Rep_Geo": rep + 1
                })
            random.shuffle(essais_bloc)
            for index, essai in enumerate(essais_bloc): essai["Trial_in_Block"] = index + 1
            self.sequence.extend(essais_bloc)
            
        self.seq_index = 0; self.state = "WAIT_POS" 
        self.timer = QTimer(self); self.timer.timeout.connect(self.game_loop); self.timer.start(8)
        self.prev_t = time.perf_counter(); self.prev_pos = QPointF(0,0)

    def tabletEvent(self, e: QTabletEvent):
        self.pressure = e.pressure(); self.pos = e.position(); e.accept()

    def get_pointer_color(self, px, py, pressure, R, W):
        dist_c = math.sqrt((px - self.width()/2)**2 + (py - self.height()/2)**2)
        erreur_radiale = abs(dist_c - R)
        
        if erreur_radiale > (W / 2): return Qt.GlobalColor.red 
        
        if self.sequence[self.seq_index]["Task"] == "FVP":
            current_force = pressure * CONFIG["RAW_MAX"]
            if current_force < self.f_min: return Qt.GlobalColor.blue 
            elif current_force > self.f_max: return QColor("orange")
            
        return Qt.GlobalColor.green

    def game_loop(self):
        t = time.perf_counter(); cx, cy = self.width()/2, self.height()/2
        if self.state in ["WAIT_POS", "COUNTDOWN", "RECORDING"]: 
            R = self.sequence[self.seq_index]["R"]; sy = cy + R 
            
        if self.state == "WAIT_POS":
            dist = math.sqrt((self.pos.x()-cx)**2 + (self.pos.y()-sy)**2)
            current_force = self.pressure * CONFIG["RAW_MAX"]
            if dist < 30: 
                force_ok = (self.f_min <= current_force <= self.f_max) if self.sequence[self.seq_index]["Task"] == "FVP" else (self.pressure > 0.05)
                if force_ok:
                    if not hasattr(self, 'stationary_start_t') or self.stationary_start_t is None: self.stationary_start_t = t
                    if t - self.stationary_start_t > CONFIG["STATIONARY_DELAY"]: 
                        self.state = "COUNTDOWN"; self.timer_state = t; self.cd_val = 3
                else: self.stationary_start_t = None
            else: self.stationary_start_t = None
            
        elif self.state == "COUNTDOWN":
            if t - self.timer_state >= 1.0:
                self.cd_val -= 1; self.timer_state = t
                if self.cd_val == 0: 
                    self.beep.play(); self.state = "RECORDING"
                    self.start_trial_time = t; self.movement_started = False
                    self.buffer_raw = []; self.current_trajectory = []
                    
        elif self.state == "RECORDING":
            if t - self.start_trial_time > CONFIG["TEMPS_MAX_ESSAI"]: self.end_trial(timeout=True)
            else: self.collect_data(t)
        elif self.state == "REST":
            if t - self.timer_state >= CONFIG["TEMPS_REPOS"]: self.next_step()
        elif self.state == "LONG_BREAK":
            if t - self.timer_state >= CONFIG["TEMPS_PAUSE_LONGUE"]: self.state = "WAIT_POS"
        self.update()

    def collect_data(self, t):
        px, py = self.pos.x(), self.pos.y(); cx, cy = self.width()/2, self.height()/2
        R = self.sequence[self.seq_index]["R"]; W = self.sequence[self.seq_index]["W"]
        thickness = CONFIG["BASE_THICKNESS"] 
        
        if not self.movement_started:
            dt = t - self.prev_t
            if dt > 0:
                v = math.sqrt((px-self.prev_pos.x())**2 + (py-self.prev_pos.y())**2) / dt
                if v > CONFIG["VELOCITY_THRESHOLD"]: self.movement_started = True; self.actual_start_t = t
            self.prev_t = t; self.prev_pos = QPointF(px, py); return
            
        dist_c = math.sqrt((px-cx)**2 + (py-cy)**2); erreur_radiale = abs(dist_c - R)
        in_t = 1 if erreur_radiale <= (W / 2) else 0 
        angle = math.atan2(py - cy, px - cx)
        
        col = self.get_pointer_color(px, py, self.pressure, R, W)
        
        self.buffer_raw.append([t, t-self.actual_start_t, px, py, self.pressure * CONFIG["RAW_MAX"], thickness, erreur_radiale, in_t, angle])
        self.current_trajectory.append((QPointF(px, py), thickness, col))
        
        if len(self.buffer_raw) > 10:
            angles = [row[8] for row in self.buffer_raw]
            nLaps = abs(np.unwrap(angles)[-1] - np.unwrap(angles)[0]) / (2 * np.pi)
            if nLaps >= 1.0: self.end_trial(timeout=False)

    def safe_save(self, base_name, data_list, header):
        path = os.path.join(DATA_RAW_PATH, base_name)
        file_exists = os.path.isfile(path) and os.path.getsize(path) > 0
        with open(path, 'a', newline='') as f:
            w = csv.writer(f)
            if not file_exists: w.writerow(header)
            w.writerows(data_list)

    def end_trial(self, timeout=False):
        t_info = self.sequence[self.seq_index]; bloc_id = f"{t_info['Task']}_{'FB' if t_info['Feedback'] else 'NoFB'}"
        if self.buffer_raw:
            raw_to_save = [[self.pid, bloc_id, t_info["IDc_Level"], t_info["Rep_Geo"], t_info["R"], t_info["W"], t_info["Trial_in_Block"]] + r for r in self.buffer_raw]
            self.safe_save(f"{self.pid}_RAW.csv", raw_to_save, ["ID", "Bloc", "IDc_Lvl", "Rep_Geo", "R", "W", "Trial_in_Bloc", "Time_Abs", "Time_Rel", "X", "Y", "P_Raw", "Thickness", "Err_Radiale", "InT", "Angle"])
            
            data = np.array(self.buffer_raw); times, pressures, err_rad, in_t = data[:, 1], data[:, 4], data[:, 6], data[:, 7]
            score_row = [[self.pid, bloc_id, t_info["Task"], int(t_info["Feedback"]), t_info["IDc_Level"], t_info["R"], t_info["W"], t_info["Rep_Geo"], t_info["Trial_in_Block"], round(times[-1], 3), round(np.sqrt(np.mean(err_rad**2)), 2), round(np.mean(in_t) * 100, 1), round(np.mean(pressures), 1), round(np.std(pressures), 1), int(timeout)]]
            self.safe_save(f"{self.pid}_SCORES.csv", score_row, ["ID", "Bloc", "Task", "FB", "IDc_Lvl", "R", "W", "Rep_Geo", "Trial_in_Bloc", "MT", "RMSE", "Pct_InT", "Mean_Force", "Std_Force", "Timeout"])
            
        self.current_trajectory = []; self.state = "REST"; self.timer_state = time.perf_counter()

    def next_step(self):
        old_bloc = (self.sequence[self.seq_index]["Task"], self.sequence[self.seq_index]["Feedback"])
        self.seq_index += 1
        if self.seq_index >= len(self.sequence): self.state = "END"
        else:
            new_bloc = (self.sequence[self.seq_index]["Task"], self.sequence[self.seq_index]["Feedback"])
            if old_bloc != new_bloc:
                instr = InstructionDialog(new_bloc[0], new_bloc[1], is_first=False)
                instr.exec()
            self.state = "WAIT_POS"

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing); cx, cy = self.width()/2, self.height()/2
        
        if self.state == "END":
            p.setPen(Qt.GlobalColor.white); p.setFont(QFont("Arial", 30))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "FIN DE L'EXPÉRIENCE\n\n[ ECHAP ]"); return
            
        # NOUVEL ECRAN DE REPOS AVEC DECOMPTE VISUEL
        if self.state == "REST":
            t = time.perf_counter()
            time_left = math.ceil(CONFIG["TEMPS_REPOS"] - (t - self.timer_state))
            if time_left < 1: time_left = 1
            p.setPen(Qt.GlobalColor.white)
            p.setFont(QFont("Arial", 40, QFont.Weight.Bold))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"Essai terminé\n\nProchain essai dans : {time_left}")
            return

        R = self.sequence[self.seq_index]["R"]; W = self.sequence[self.seq_index]["W"]
        has_feedback = self.sequence[self.seq_index]["Feedback"]
        
        p.setPen(Qt.GlobalColor.white); p.setFont(QFont("Arial", 16))
        p.drawText(20, 40, f"Essai {self.seq_index + 1} / {len(self.sequence)}")
        
        p.setPen(QPen(QColor(100, 100, 100), W)); p.drawEllipse(QPointF(cx, cy), R, R)
        
        if has_feedback:
            for i in range(1, len(self.current_trajectory)):
                p1, th1, col1 = self.current_trajectory[i-1]; p2, th2, col2 = self.current_trajectory[i]
                p.setPen(QPen(col1, th1, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)); p.drawLine(p1, p2)
            
        if self.state in ["WAIT_POS", "COUNTDOWN"]:
            sy = cy + R; current_force = self.pressure * CONFIG["RAW_MAX"]
            dist = math.sqrt((self.pos.x()-cx)**2 + (self.pos.y()-sy)**2)
            
            p.setPen(QPen(Qt.GlobalColor.gray, 2))
            p.drawLine(QPointF(cx-15, sy), QPointF(cx+15, sy)); p.drawLine(QPointF(cx, sy-15), QPointF(cx, sy+15))
            
            color = Qt.GlobalColor.red 
            if dist < 30:
                is_good_force = (self.f_min <= current_force <= self.f_max) if self.sequence[self.seq_index]["Task"] == "FVP" else (self.pressure > 0.05)
                if is_good_force: color = Qt.GlobalColor.green
                
            p.setPen(QPen(color, 4))
            p.drawLine(QPointF(cx-20, sy), QPointF(cx+20, sy)); p.drawLine(QPointF(cx, sy-20), QPointF(cx, sy+20))
            
            if self.state == "COUNTDOWN":
                p.setPen(Qt.GlobalColor.yellow)
                p.setFont(QFont("Arial", 120, QFont.Weight.Bold))
                p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, str(self.cd_val))
        
        current_th = CONFIG["BASE_THICKNESS"]
        col_pointer = self.get_pointer_color(self.pos.x(), self.pos.y(), self.pressure, R, W) if has_feedback else Qt.GlobalColor.lightGray
        
        p.setBrush(col_pointer); p.setPen(QPen(Qt.GlobalColor.black, 1))
        p.drawEllipse(self.pos, current_th/2 + 2, current_th/2 + 2)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape: self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    d = ConfigDialog()
    if d.exec():
        settings = d.get_settings()
        ex = SteeringExpe(settings)
        first = ex.sequence[0]
        instr = InstructionDialog(first['Task'], first['Feedback'], is_first=True)
        instr.exec()
        ex.show()
        sys.exit(app.exec())