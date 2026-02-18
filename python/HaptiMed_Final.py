import sys, os, math, time, csv, random
import numpy as np
from PyQt6.QtWidgets import (QApplication, QWidget, QDialog, QFormLayout, QSpinBox, 
                             QLineEdit, QDialogButtonBox, QVBoxLayout)
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QTabletEvent
from PyQt6.QtMultimedia import QSoundEffect

# ==========================================================
# CONFIGURATION SYSTÈME ET DIFFICULTÉS
# ==========================================================
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

# 5 Niveaux de difficulté géométrique
TUNNEL_LEVELS = [
    {"R": 250, "W": 100}, # Très facile
    {"R": 400, "W": 100}, # Facile
    {"R": 250, "W": 50},  # Moyen
    {"R": 400, "W": 50},  # Difficile
    {"R": 400, "W": 30}   # Très difficile
]

# Calcul automatique et infaillible du chemin vers data/raw
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG = {
    "SAVE_PATH": os.path.join(BASE_DIR, "data", "raw"),
    "TARGET_RAW": 3200,   
    "FORCE_TOLERANCE_PCT": 5, 
    "RAW_MAX": 8192,
    "BASE_THICKNESS": 4,  
    "MAX_THICKNESS": 40,  
    "TEMPS_MAX_ESSAI": 15,
    "TEMPS_REPOS": 5,     
    "TEMPS_PAUSE_LONGUE": 30, 
    "REPS_PER_ID": 2,     # 2 rep * 5 niveaux = 10 essais
    "STATIONARY_DELAY": 0.5,
    "VELOCITY_THRESHOLD": 10.0
}

class ConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuration HaptiMed Steering")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.input_id = QLineEdit(); self.input_id.setPlaceholderText("ex: P01")
        form.addRow("ID Participant :", self.input_id)
        self.input_target = QSpinBox(); self.input_target.setRange(100, 8000); self.input_target.setValue(CONFIG["TARGET_RAW"])
        form.addRow("Cible Force (Brute) :", self.input_target)
        self.input_tol = QSpinBox(); self.input_tol.setRange(1, 50); self.input_tol.setValue(CONFIG["FORCE_TOLERANCE_PCT"]); self.input_tol.setSuffix(" %")
        form.addRow("Tolérance Force (+/-) :", self.input_tol)
        
        layout.addLayout(form)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        self.setLayout(layout)

    def get_settings(self):
        return {"ID": self.input_id.text(), "TARGET": self.input_target.value(), "TOL_PCT": self.input_tol.value()}

class SteeringExpe(QWidget):
    def __init__(self, s):
        super().__init__()
        self.pid = s["ID"] if s["ID"] else "TEST"
        CONFIG["TARGET_RAW"] = s["TARGET"]
        CONFIG["FORCE_TOLERANCE_PCT"] = s["TOL_PCT"]
        
        margin = CONFIG["TARGET_RAW"] * (CONFIG["FORCE_TOLERANCE_PCT"] / 100.0)
        self.f_min = CONFIG["TARGET_RAW"] - margin
        self.f_max = CONFIG["TARGET_RAW"] + margin
        
        if not os.path.exists(CONFIG["SAVE_PATH"]): 
            os.makedirs(CONFIG["SAVE_PATH"], exist_ok=True)

        self.setStyleSheet("background-color: black;")
        self.showFullScreen()
        self.setCursor(Qt.CursorShape.BlankCursor) 
        self.beep = QSoundEffect(self)

        self.pos = QPointF(0,0); self.pressure = 0.0
        self.buffer_raw = []
        self.current_trajectory = [] 
        
        # ==========================================================
        # PLAN EXPÉRIMENTAL (Randomisation et Numérotation propre)
        # ==========================================================
        self.sequence = []
        conditions = [("VP", False), ("VP", True), ("FVP", False), ("FVP", True)]
        random.shuffle(conditions) 
        
        for task, fb in conditions:
            essais_bloc = []
            for idc_level, params in enumerate(TUNNEL_LEVELS):
                for rep in range(CONFIG["REPS_PER_ID"]):
                    essais_bloc.append({
                        "Task": task, "Feedback": fb, "IDc_Level": idc_level + 1,
                        "R": params["R"], "W": params["W"], "Rep_Geo": rep + 1
                    })
            # On randomise la géométrie
            random.shuffle(essais_bloc) 
            
            # MAIS on attribue un numéro d'ordre propre (1 à 10) pour l'affichage au sujet
            for index, essai in enumerate(essais_bloc):
                essai["Trial_in_Block"] = index + 1
                
            self.sequence.extend(essais_bloc)

        self.seq_index = 0
        self.state = "INTRO_TASK"

        self.timer = QTimer(self); self.timer.timeout.connect(self.game_loop); self.timer.start(8)
        self.prev_t = time.perf_counter(); self.prev_pos = QPointF(0,0)

    def tabletEvent(self, e: QTabletEvent):
        self.pressure = e.pressure()
        self.pos = e.position()
        e.accept()

    def get_pointer_color(self, px, py, pressure, R, W, thickness, force_fb_override=False):
        t_info = self.sequence[self.seq_index]
        show_fb = t_info["Feedback"] or force_fb_override
        
        if not show_fb:
            return Qt.GlobalColor.white 
            
        dist_c = math.sqrt((px - self.width()/2)**2 + (py - self.height()/2)**2)
        erreur_radiale = abs(dist_c - R)
        current_force = pressure * CONFIG["RAW_MAX"]
        
        # 1. Erreur Spatiale prioritaire
        if (erreur_radiale + thickness/2) > (W / 2):
            return Qt.GlobalColor.red 
        
        # 2. Erreur de Force (seulement si la tâche l'exige)
        if t_info["Task"] == "FVP":
            if current_force < self.f_min:
                return Qt.GlobalColor.blue 
            elif current_force > self.f_max:
                return QColor("orange")    
                
        # 3. Tout est parfait
        return Qt.GlobalColor.green

    def game_loop(self):
        t = time.perf_counter()
        cx, cy = self.width()/2, self.height()/2
        
        if self.state in ["WAIT_POS", "COUNTDOWN", "RECORDING"]:
            R = self.sequence[self.seq_index]["R"]
            sy = cy + R 

        if self.state == "WAIT_POS":
            dist = math.sqrt((self.pos.x()-cx)**2 + (self.pos.y()-sy)**2)
            current_force = self.pressure * CONFIG["RAW_MAX"]
            
            if dist < 30:
                force_ok = False
                if self.sequence[self.seq_index]["Task"] == "FVP":
                    if self.f_min <= current_force <= self.f_max:
                        force_ok = True
                else:
                    if self.pressure > 0.05:
                        force_ok = True
                
                if force_ok:
                    if not hasattr(self, 'stationary_start_t') or self.stationary_start_t is None: 
                        self.stationary_start_t = t
                    if t - self.stationary_start_t > CONFIG["STATIONARY_DELAY"]:
                        self.state = "COUNTDOWN"; self.timer_state = t; self.cd_val = 3
                else:
                    self.stationary_start_t = None
            else: 
                self.stationary_start_t = None

        elif self.state == "COUNTDOWN":
            if t - self.timer_state >= 1.0:
                self.cd_val -= 1; self.timer_state = t
                if self.cd_val == 0:
                    self.beep.play()
                    self.state = "RECORDING"
                    self.start_trial_time = t
                    self.movement_started = False
                    self.buffer_raw = []
                    self.current_trajectory = []
                    self.go_timer = t

        elif self.state == "RECORDING":
            if t - self.start_trial_time > CONFIG["TEMPS_MAX_ESSAI"]: 
                self.end_trial(timeout=True)
            else: 
                self.collect_data(t)

        elif self.state == "REST":
            if t - self.timer_state >= CONFIG["TEMPS_REPOS"]: 
                self.next_step()

        elif self.state == "LONG_BREAK":
            if t - self.timer_state >= CONFIG["TEMPS_PAUSE_LONGUE"]: 
                self.state = "INTRO_TASK"

        self.update()

    def collect_data(self, t):
        px, py = self.pos.x(), self.pos.y()
        cx, cy = self.width()/2, self.height()/2
        R = self.sequence[self.seq_index]["R"]
        W = self.sequence[self.seq_index]["W"]

        if self.sequence[self.seq_index]["Feedback"]:
            thickness = CONFIG["BASE_THICKNESS"] + (self.pressure * CONFIG["MAX_THICKNESS"])
        else:
            thickness = CONFIG["BASE_THICKNESS"]
        
        if not self.movement_started:
            dt = t - self.prev_t
            if dt > 0:
                v = math.sqrt((px-self.prev_pos.x())**2 + (py-self.prev_pos.y())**2) / dt
                if v > CONFIG["VELOCITY_THRESHOLD"]:
                    self.movement_started = True
                    self.actual_start_t = t
            self.prev_t = t; self.prev_pos = QPointF(px, py)
            return

        dist_c = math.sqrt((px-cx)**2 + (py-cy)**2)
        erreur_radiale = abs(dist_c - R)
        
        in_t = 1 if (erreur_radiale + thickness/2) <= (W / 2) else 0
        angle = math.atan2(py - cy, px - cx)
        
        # On calcule la couleur en temps réel pour l'enregistrer dans la trace (même si FB False)
        trace_color = self.get_pointer_color(px, py, self.pressure, R, W, thickness, force_fb_override=False)
        
        self.buffer_raw.append([
            t, t-self.actual_start_t, px, py, 
            self.pressure * CONFIG["RAW_MAX"], 
            thickness, erreur_radiale, in_t, angle
        ])
        
        # On sauvegarde la Position, l'Epaisseur ET la Couleur
        self.current_trajectory.append((QPointF(px, py), thickness, trace_color))

        if len(self.buffer_raw) > 10:
            angles = [row[8] for row in self.buffer_raw]
            nLaps = abs(np.unwrap(angles)[-1] - np.unwrap(angles)[0]) / (2 * np.pi)
            if nLaps >= 1.0:
                self.end_trial(timeout=False)

    def safe_save(self, base_name, data_list, header):
        path = os.path.join(CONFIG["SAVE_PATH"], base_name)
        file_exists = os.path.isfile(path) and os.path.getsize(path) > 0
        try:
            with open(path, 'a', newline='') as f:
                w = csv.writer(f)
                if not file_exists: w.writerow(header)
                w.writerows(data_list)
        except PermissionError:
            pass

    def end_trial(self, timeout=False):
        t_info = self.sequence[self.seq_index]
        bloc_id = f"{t_info['Task']}_{'FB' if t_info['Feedback'] else 'NoFB'}"
        
        if self.buffer_raw:
            # Ajout du Trial_in_Block (l'ordre 1 à 10) dans les datas
            raw_to_save = [[self.pid, bloc_id, t_info["IDc_Level"], t_info["Rep_Geo"], t_info["Trial_in_Block"]] + r for r in self.buffer_raw]
            self.safe_save(f"{self.pid}_RAW.csv", raw_to_save, 
                           ["ID", "Bloc", "IDc_Lvl", "Rep_Geo", "Trial_in_Bloc", "Time_Abs", "Time_Rel", "X", "Y", "P_Raw", "Thickness", "Err_Radiale", "InT", "Angle"])
            
            data = np.array(self.buffer_raw)
            times, pressures, err_rad, in_t = data[:, 1], data[:, 4], data[:, 6], data[:, 7]
            
            score_row = [[self.pid, bloc_id, t_info["Task"], int(t_info["Feedback"]), 
                          t_info["IDc_Level"], t_info["R"], t_info["W"], t_info["Rep_Geo"], t_info["Trial_in_Block"],
                          round(times[-1], 3), round(np.sqrt(np.mean(err_rad**2)), 2), 
                          round(np.mean(in_t) * 100, 1), round(np.mean(pressures), 1), 
                          round(np.std(pressures), 1), int(timeout)]]
            
            self.safe_save(f"{self.pid}_SCORES.csv", score_row, 
                           ["ID", "Bloc", "Task", "FB", "IDc_Lvl", "R", "W", "Rep_Geo", "Trial_in_Bloc",
                            "MT", "RMSE", "Pct_InT", "Mean_Force", "Std_Force", "Timeout"])
            
        self.current_trajectory = []
        self.state = "REST"
        self.timer_state = time.perf_counter()

    def next_step(self):
        old_bloc = (self.sequence[self.seq_index]["Task"], self.sequence[self.seq_index]["Feedback"])
        self.seq_index += 1
        
        if self.seq_index >= len(self.sequence): 
            self.state = "END"
        else:
            new_bloc = (self.sequence[self.seq_index]["Task"], self.sequence[self.seq_index]["Feedback"])
            if old_bloc != new_bloc: 
                self.state = "LONG_BREAK"
                self.timer_state = time.perf_counter()
            else: 
                self.state = "WAIT_POS"

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width()/2, self.height()/2
        
        # Préparation des textes clairs
        if self.seq_index < len(self.sequence):
            t_info = self.sequence[self.seq_index]
            nom_tache = "FORCE - VITESSE - PRÉCISION" if t_info['Task'] == "FVP" else "VITESSE - PRÉCISION"
            nom_fb = "AVEC Feedback Visuel" if t_info['Feedback'] else "SANS Feedback Visuel"
        
        if self.state == "INTRO_TASK":
            p.setPen(Qt.GlobalColor.white); p.setFont(QFont("Arial", 30, QFont.Weight.Bold))
            p.drawText(self.rect().adjusted(0,80,0,0), Qt.AlignmentFlag.AlignHCenter, f"NOUVEAU BLOC\n\n{nom_tache}\n{nom_fb}")
            
            p.setFont(QFont("Arial", 22))
            consigne = "Faites 1 tour complet dans le tunnel.\nSoyez le plus RAPIDE et le plus PRÉCIS possible."
            if t_info['Task'] == "FVP":
                consigne += f"\nMaintenez une pression cible de {CONFIG['TARGET_RAW']} (+/- {CONFIG['FORCE_TOLERANCE_PCT']}%)."
            if t_info['Feedback']:
                consigne += "\n\nAVEC FEEDBACK : L'épaisseur et la couleur de la trace varient avec votre force.\nRestez VERT. Si vous débordez (ROUGE), c'est une erreur !"
            else:
                consigne += "\n\nSANS FEEDBACK : Le pointeur reste blanc. Fiez-vous à vos sensations mémorisées au départ."
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, consigne + "\n\n[ ESPACE POUR DÉMARRER ]")

        elif self.state in ["REST", "LONG_BREAK", "END"]:
            p.setPen(Qt.GlobalColor.white); p.setFont(QFont("Arial", 30))
            if self.state == "REST": p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"Essai {self.sequence[self.seq_index-1]['Trial_in_Block']} terminé.\nSuivant dans un instant...")
            elif self.state == "LONG_BREAK": p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "CHANGEMENT DE CONDITION\n\n[ ESPACE POUR PASSER ]")
            else: p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "FIN DE L'EXPÉRIENCE\n[ ECHAP POUR QUITTER ]")
        
        else:
            R = self.sequence[self.seq_index]["R"]
            W = self.sequence[self.seq_index]["W"]
            
            # Affichage de la condition en permanence en haut à gauche
            p.setPen(Qt.GlobalColor.white)
            p.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            p.drawText(20, 40, f"Règle : {nom_tache} | {nom_fb}")
            p.setFont(QFont("Arial", 14))
            p.drawText(20, 70, f"Essai {t_info['Trial_in_Block']} / {CONFIG['REPS_PER_ID'] * len(TUNNEL_LEVELS)}")

            # Dessin du tunnel (Gris)
            p.setPen(QPen(QColor(50, 50, 50), W)) 
            p.drawEllipse(QPointF(cx, cy), R, R)

            sy = cy + R 
            
            # Trace du sujet (MULTICOLORE)
            for i in range(1, len(self.current_trajectory)):
                p1, th1, col1 = self.current_trajectory[i-1]
                p2, th2, col2 = self.current_trajectory[i]
                p.setPen(QPen(col1, th1, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                p.drawLine(p1, p2)

            # Croix de départ et instructions de calibration
            if self.state in ["WAIT_POS", "COUNTDOWN"]:
                p.setPen(QPen(Qt.GlobalColor.yellow if getattr(self, 'stationary_start_t', None) else Qt.GlobalColor.red, 4))
                p.drawLine(QPointF(cx-20, sy), QPointF(cx+20, sy)); p.drawLine(QPointF(cx, sy-20), QPointF(cx, sy+20))
                
                if self.state == "WAIT_POS" and t_info["Task"] == "FVP":
                    p.setPen(Qt.GlobalColor.white); p.setFont(QFont("Arial", 20))
                    p.drawText(int(cx - 200), int(sy + 60), 400, 50, Qt.AlignmentFlag.AlignCenter, "Ajustez votre pression\npour être VERT")

                if self.state == "COUNTDOWN":
                    p.setPen(Qt.GlobalColor.yellow); p.setFont(QFont("Arial", 100, QFont.Weight.Bold))
                    p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, str(self.cd_val))

            # ==========================================================
            # POINTEUR ACTUEL
            # ==========================================================
            show_fb_now = t_info["Feedback"]
            if self.state == "WAIT_POS" and t_info["Task"] == "FVP":
                show_fb_now = True

            current_th = CONFIG["BASE_THICKNESS"] + (self.pressure * CONFIG["MAX_THICKNESS"]) if show_fb_now else CONFIG["BASE_THICKNESS"]
            col = self.get_pointer_color(self.pos.x(), self.pos.y(), self.pressure, R, W, current_th, force_fb_override=show_fb_now)

            # Dessin de la bille (Avec un liseré noir pour toujours être visible sur la croix jaune)
            p.setBrush(col)
            p.setPen(QPen(Qt.GlobalColor.black, 1)) 
            p.drawEllipse(self.pos, current_th/2, current_th/2)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Space and self.state in ["INTRO_TASK", "LONG_BREAK"]: 
            self.state = "WAIT_POS"
        if e.key() == Qt.Key.Key_Escape: 
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv); d = ConfigDialog()
    if d.exec(): 
        ex = SteeringExpe(d.get_settings())
        ex.show()
        sys.exit(app.exec())