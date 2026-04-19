import sys, os, math, time, csv, random
import numpy as np
from PyQt6.QtWidgets import (QApplication, QWidget, QDialog, QFormLayout, QSpinBox, 
                             QLineEdit, QDialogButtonBox, QVBoxLayout, QLabel, QComboBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QTabletEvent
from PyQt6.QtMultimedia import QSoundEffect

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_RAW_PATH = os.path.join(BASE_DIR, "data", "raw")

if not os.path.exists(DATA_RAW_PATH):
    os.makedirs(DATA_RAW_PATH, exist_ok=True)

TUNNEL_LEVELS = [{"R": 350, "W": 5}] 

CONFIG = {
    "TARGET_RAW": 3200, 
    "FORCE_TOLERANCE_PCT": 20, 
    "RAW_MAX": 8192,
    "BASE_THICKNESS": 6,        
    "MIN_THICKNESS": 2,        
    "MAX_THICKNESS": 25,        
    "TEMPS_REPOS": 3, 
    "TEMPS_PAUSE_LONGUE": 20,
    "REPS_PER_ID": 10,          
    "STATIONARY_DELAY": 0.5, 
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
        form.addRow("Tolérance Force (%) :", self.input_tol)
        
        self.input_reps = QSpinBox()
        self.input_reps.setRange(1, 100)
        self.input_reps.setValue(CONFIG["REPS_PER_ID"])
        form.addRow("Nbr Répétitions / condition :", self.input_reps)

        self.input_r = QSpinBox()
        self.input_r.setRange(50, 1500)
        self.input_r.setValue(TUNNEL_LEVELS[0]["R"])
        form.addRow("Rayon du cercle (R) :", self.input_r)

        self.input_w = QSpinBox()
        self.input_w.setRange(1, 200)
        self.input_w.setValue(TUNNEL_LEVELS[0]["W"])
        form.addRow("Largeur du tunnel (W) :", self.input_w)
        
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
            "REPS": self.input_reps.value(),
            "R": self.input_r.value(),     
            "W": self.input_w.value()      
        }

# --- ÉTAPE 1.5 : QUESTIONNAIRE PROFIL PARTICIPANT ---
class DemographicsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Profil du Participant")
        self.setMinimumWidth(450)
        layout = QVBoxLayout()
        self.form = QFormLayout()

        self.input_age = QSpinBox()
        self.input_age.setRange(18, 99)
        self.input_age.setValue(25)
        self.form.addRow("Âge :", self.input_age)

        self.input_hand = QComboBox()
        self.input_hand.addItems(["Droitier", "Gaucher", "Ambidextre"])
        self.form.addRow("Main dominante :", self.input_hand)

        self.input_sleep = QDoubleSpinBox()
        self.input_sleep.setRange(0.0, 24.0)
        self.input_sleep.setSingleStep(0.5)
        self.input_sleep.setValue(8.0)
        self.form.addRow("Heures de sommeil (dernière nuit) :", self.input_sleep)

        self.input_coffee = QSpinBox()
        self.input_coffee.setRange(0, 20)
        self.form.addRow("Tasses de café (dernières 24h) :", self.input_coffee)

        self.input_fatigue = QSpinBox()
        self.input_fatigue.setRange(0, 10)
        self.form.addRow("Niveau de fatigue (0 = En forme, 10 = Épuisé) :", self.input_fatigue)

        self.input_vg = QComboBox()
        self.input_vg.addItems(["jamais", "occasionnellement", "regulierement", "quotidiennement"])
        self.form.addRow("Habitudes jeux vidéo :", self.input_vg)

        line = QWidget()
        line.setFixedHeight(2)
        line.setStyleSheet("background-color: #bdc3c7; margin-top: 10px; margin-bottom: 10px;")
        self.form.addRow(line)

        self.input_status = QComboBox()
        self.input_status.addItems(["Sélectionner...", "Interne", "Externe", "Non domaine médical"])
        self.form.addRow("Statut professionnel :", self.input_status)

        self.input_interne_type = QComboBox()
        self.input_interne_type.addItems(["Sélectionner...", "Apprentissage", "Diplômé"])
        self.row_interne_type = self.form.addRow("Niveau Interne :", self.input_interne_type)

        self.input_annee = QComboBox()
        self.input_annee.addItems([f"{i}eme annee" for i in range(1, 7)]) 
        self.row_annee = self.form.addRow("Année d'apprentissage :", self.input_annee)

        self.input_pratique = QComboBox()
        self.input_pratique.addItems(["1 a 3 ans", "4 a 6 ans", "7 a 10 ans", "10 a 15 ans", "plus de 15 ans"]) 
        self.row_pratique = self.form.addRow("En pratique depuis :", self.input_pratique)

        self.input_has_spec = QComboBox()
        self.input_has_spec.addItems(["non", "oui"])
        self.row_has_spec = self.form.addRow("Avez-vous une spécialité ?", self.input_has_spec)

        self.input_spec_name = QLineEdit()
        self.input_spec_name.setPlaceholderText("ex: cardiologie")
        self.row_spec_name = self.form.addRow("Spécialité :", self.input_spec_name)

        self.input_autre = QLineEdit()
        self.input_autre.setPlaceholderText("ex: ingenieur")
        self.row_autre = self.form.addRow("Métier ou domaine :", self.input_autre)

        layout.addLayout(self.form)
        self.btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.btns.accepted.connect(self.accept)
        layout.addWidget(self.btns)
        self.setLayout(layout)

        self.input_status.currentIndexChanged.connect(self.update_ui)
        self.input_interne_type.currentIndexChanged.connect(self.update_ui)
        self.input_has_spec.currentIndexChanged.connect(self.update_ui)
        self.update_ui()

    def set_row_visible(self, widget, visible):
        widget.setVisible(visible)
        self.form.labelForField(widget).setVisible(visible)

    def update_ui(self):
        self.set_row_visible(self.input_interne_type, False)
        self.set_row_visible(self.input_annee, False)
        self.set_row_visible(self.input_pratique, False)
        self.set_row_visible(self.input_has_spec, False)
        self.set_row_visible(self.input_spec_name, False)
        self.set_row_visible(self.input_autre, False)

        status = self.input_status.currentText()
        self.btns.button(QDialogButtonBox.StandardButton.Ok).setEnabled(status != "Sélectionner...")

        if status == "Interne":
            self.set_row_visible(self.input_interne_type, True)
            interne_type = self.input_interne_type.currentText()
            if interne_type == "Apprentissage":
                self.set_row_visible(self.input_annee, True)
                self.set_row_visible(self.input_has_spec, True)
                if self.input_has_spec.currentText() == "oui":
                    self.set_row_visible(self.input_spec_name, True)
            elif interne_type == "Diplômé":
                self.set_row_visible(self.input_pratique, True)
                self.set_row_visible(self.input_spec_name, True)
        elif status == "Externe":
            self.set_row_visible(self.input_spec_name, True)
        elif status == "Non domaine médical":
            self.set_row_visible(self.input_autre, True)

    def get_demographics(self):
        status = self.input_status.currentText().lower()
        data = {
            "age": self.input_age.value(),
            "lateralite": self.input_hand.currentText().lower(),
            "sommeil_h": self.input_sleep.value(),
            "cafe_24h": self.input_coffee.value(),
            "fatigue_eva": self.input_fatigue.value(),
            "jeux_video": self.input_vg.currentText().lower(),
            "statut_principal": status,
            "sous_statut": "na",
            "annee_apprentissage": "na",
            "annees_pratique": "na",
            "specialite": "na",
            "autre_domaine": "na"
        }

        if status == "interne":
            sous_statut = self.input_interne_type.currentText()
            data["sous_statut"] = sous_statut.lower() if sous_statut != "Sélectionner..." else "na"
            if sous_statut == "Apprentissage":
                data["annee_apprentissage"] = self.input_annee.currentText()
                if self.input_has_spec.currentText() == "oui":
                    data["specialite"] = self.input_spec_name.text().strip().lower()
            elif sous_statut == "Diplômé":
                data["annees_pratique"] = self.input_pratique.currentText()
                data["specialite"] = self.input_spec_name.text().strip().lower()
        elif status == "externe":
            data["specialite"] = self.input_spec_name.text().strip().lower()
        elif status == "non domaine médical":
            data["autre_domaine"] = self.input_autre.text().strip().lower()

        return data

# --- ÉTAPE 2 : CONSIGNES SPÉCIFIQUES ---
class InstructionDialog(QDialog):
    def __init__(self, task_type, has_feedback, is_first=False):
        super().__init__()
        self.setWindowTitle("Consignes Expérimentales")
        self.setFixedSize(750, 500)
        layout = QVBoxLayout()
        
        title_text = "BIENVENUE DANS L'EXPÉRIENCE" if is_first else "CHANGEMENT DE CONDITION"
        layout.addWidget(QLabel(f"<h1 style='color:#2c3e50; text-align:center;'>{title_text}</h1>"))

        condition_title = f"{'FORCE - VITESSE - PRÉCISION' if task_type == 'FVP' else 'VITESSE - PRÉCISION'} - {'AVEC FEEDBACK' if has_feedback else 'SANS FEEDBACK'}"
        layout.addWidget(QLabel(f"<h2 style='color:#2980b9; text-align:center;'>{condition_title}</h2>"))

        instr = "<b>DÉPART :</b><br>Placez-vous sur la croix en bas. "
        if task_type == "FVP":
            instr += "Calibrez votre pression pour rendre la croix <b style='color:green;'>VERTE</b>. Maintenez 0.5 seconde.<br><br>"
        else:
            instr += "Touchez la tablette pour rendre la croix <b style='color:green;'>VERTE</b>. Maintenez 0.5 seconde.<br><br>"

        instr += "<b>PENDANT LE DESSIN :</b><br>"
        instr += "Allez le plus vite possible tout en restant dans le tunnel.<br>"

        if has_feedback:
            instr += "• Un trait suivra votre stylet.<br>"
            instr += "• Si vous sortez du tunnel, le tracé devient <b style='color:red;'>ROUGE</b>.<br>"
            if task_type == "FVP":
                instr += "• Le tracé reste <b style='color:green;'>VERT</b> si vous êtes dans le tunnel.<br>"
                instr += "• <b style='color:purple;'>NOUVEAUTÉ : L'épaisseur du trait dépend de votre force.</b><br>"
                instr += "• Pression forte = Trait épais.<br>"
                instr += "• Pression faible = Trait fin.<br>"
                instr += "• Essayez de maintenir un trait d'épaisseur régulière, correspondant à la force demandée au départ.<br>"
                instr += "• <b style='color:#2980b9;'>Une JAUGE apparaîtra au centre pour vous aider à maintenir la force cible.</b><br>"
            else:
                instr += "• Tracé correct = <b style='color:green;'>VERT</b>.<br>"
        else:
            instr += "• <i style='color:#c0392b;'>Attention : Il n'y aura aucun trait de couleur pour vous aider.</i><br>"
            instr += "• Vous ne verrez que le pointeur de votre stylet.<br>"
            if task_type == "FVP":
                instr += "• <b style='color:#27ae60;'>Remémorez-vous la force appliquée pour que la croix devienne verte au départ.</b><br>"
                instr += "• La JAUGE de force disparaîtra au moment du départ (GO!).<br>"
                instr += "• Fiez-vous à vos sensations physiques pour maintenir cette même force tout au long du mouvement.<br>"

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
    def __init__(self, s, demo_data):
        super().__init__()
        raw_id = s["ID"] if s["ID"] else "TEST"
        self.pid = raw_id.replace('/', '-') 
        
        CONFIG["TARGET_RAW"] = s["TARGET"]
        CONFIG["FORCE_TOLERANCE_PCT"] = s["TOL_PCT"]
        CONFIG["REPS_PER_ID"] = s["REPS"]
        
        self.save_demographics(self.pid, demo_data)

        TUNNEL_LEVELS[0]["R"] = s["R"]
        TUNNEL_LEVELS[0]["W"] = s["W"]
        
        margin = CONFIG["TARGET_RAW"] * (CONFIG["FORCE_TOLERANCE_PCT"] / 100.0)
        self.f_min = CONFIG["TARGET_RAW"] - margin; self.f_max = CONFIG["TARGET_RAW"] + margin
        
        self.setStyleSheet("background-color: black;")
        self.showFullScreen()
        self.setCursor(Qt.CursorShape.BlankCursor)
        self.beep = QSoundEffect(self)
        
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
            
        self.seq_index = 0
        self.is_practice = True
        self.state = "WAIT_POS" 
        
        self.timer = QTimer(self); self.timer.timeout.connect(self.game_loop); self.timer.start(8)
        self.prev_t = time.perf_counter(); self.prev_pos = QPointF(0,0)

    def save_demographics(self, pid, demo_data):
        path = os.path.join(DATA_RAW_PATH, f"{pid}_INFO.csv")
        headers = ["ID"] + list(demo_data.keys())
        row = [pid] + list(demo_data.values())
        
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(headers)
            w.writerow(row)

    def tabletEvent(self, e: QTabletEvent):
        self.pressure = e.pressure(); self.pos = e.position(); e.accept()

    def get_pointer_color(self, px, py, R, W):
        dist_c = math.sqrt((px - self.width()/2)**2 + (py - self.height()/2)**2)
        erreur_radiale = abs(dist_c - R)
        if erreur_radiale > (W / 2): return Qt.GlobalColor.red 
        return Qt.GlobalColor.green

    def get_pointer_thickness(self, pressure, task_type, has_feedback):
        if task_type == "FVP" and has_feedback:
            thickness_range = CONFIG["MAX_THICKNESS"] - CONFIG["MIN_THICKNESS"]
            return CONFIG["MIN_THICKNESS"] + (pressure * thickness_range)
        else:
            return CONFIG["BASE_THICKNESS"]

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
                    self.go_timer = t
                    
        elif self.state == "RECORDING":
            self.collect_data(t)
            
        elif self.state == "REST":
            if t - self.timer_state >= CONFIG["TEMPS_REPOS"]: self.next_step()
            
        elif self.state == "LONG_BREAK":
            if t - self.timer_state >= CONFIG["TEMPS_PAUSE_LONGUE"]: self.state = "WAIT_POS"
            
        self.update()

    def collect_data(self, t):
        px, py = self.pos.x(), self.pos.y(); cx, cy = self.width()/2, self.height()/2
        R = self.sequence[self.seq_index]["R"]; W = self.sequence[self.seq_index]["W"]
        task_type = self.sequence[self.seq_index]["Task"]
        has_feedback = self.sequence[self.seq_index]["Feedback"]
        
        thickness = self.get_pointer_thickness(self.pressure, task_type, has_feedback)
        
        if not self.movement_started:
            dt = t - self.prev_t
            if dt > 0:
                v = math.sqrt((px-self.prev_pos.x())**2 + (py-self.prev_pos.y())**2) / dt
                if v > CONFIG["VELOCITY_THRESHOLD"]: self.movement_started = True; self.actual_start_t = t
            self.prev_t = t; self.prev_pos = QPointF(px, py); return
            
        dist_c = math.sqrt((px-cx)**2 + (py-cy)**2); erreur_radiale = abs(dist_c - R)
        in_t = 1 if erreur_radiale <= (W / 2) else 0 
        angle = math.atan2(py - cy, px - cx)
        
        col = self.get_pointer_color(px, py, R, W)
        
        self.buffer_raw.append([t, t-self.actual_start_t, px, py, self.pressure * CONFIG["RAW_MAX"], thickness, erreur_radiale, in_t, angle])
        self.current_trajectory.append((QPointF(px, py), thickness, col))
        
        if len(self.buffer_raw) > 10:
            angles = [row[8] for row in self.buffer_raw]
            nLaps = abs(np.unwrap(angles)[-1] - np.unwrap(angles)[0]) / (2 * np.pi)
            if nLaps >= 1.0: self.end_trial(timeout=False)

    def safe_save(self, base_name, data_list, header):
        path = os.path.join(DATA_RAW_PATH, base_name)
        file_exists = os.path.isfile(path) and os.path.getsize(path) > 0
        with open(path, 'a', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            if not file_exists: w.writerow(header)
            w.writerows(data_list)

    def end_trial(self, timeout=False):
        if self.is_practice:
            self.buffer_raw = []
            self.current_trajectory = []
            self.state = "PRACTICE_END"
            return
            
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
                self.is_practice = True
            self.state = "WAIT_POS"

    def closeEvent(self, event):
        if self.state == "RECORDING" and not self.is_practice: 
            self.end_trial(timeout=True)
        event.accept()

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing); cx, cy = self.width()/2, self.height()/2
        
        if self.state == "END":
            p.setPen(Qt.GlobalColor.white); p.setFont(QFont("Arial", 30))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "FIN DE L'EXPÉRIENCE\n\n[ ECHAP ]"); return
            
        if self.state == "PRACTICE_END":
            p.setPen(Qt.GlobalColor.cyan); p.setFont(QFont("Arial", 30, QFont.Weight.Bold))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "ESSAI DE TEST TERMINÉ\n\nAppuyez sur [ ESPACE ] pour lancer les vrais enregistrements.")
            return

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
        task_type = self.sequence[self.seq_index]["Task"]
        
        p.setFont(QFont("Arial", 16))
        if self.is_practice:
            p.setPen(Qt.GlobalColor.cyan)
            p.drawText(self.rect().adjusted(0, 30, 0, 0), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, "MODE TEST (Non enregistré)")
        else:
            p.setPen(Qt.GlobalColor.white)
            p.drawText(20, 40, f"Essai {self.seq_index + 1} / {len(self.sequence)}")
        
        p.setPen(QPen(QColor(100, 100, 100), W)); p.drawEllipse(QPointF(cx, cy), R, R)
        
        if has_feedback:
            for i in range(1, len(self.current_trajectory)):
                p1, th1, col1 = self.current_trajectory[i-1]; p2, th2, col2 = self.current_trajectory[i]
                p.setPen(QPen(col1, th1, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)); p.drawLine(p1, p2)
            
        if self.state in ["WAIT_POS", "COUNTDOWN"]:
            sy = cy + R; current_force = self.pressure * CONFIG["RAW_MAX"]
            dist = math.sqrt((self.pos.x()-cx)**2 + (self.pos.y()-sy)**2)
            
            if task_type == "FVP":
                p.setBrush(QColor(30, 30, 30, 200)) 
                p.setPen(Qt.GlobalColor.white)
                p.drawRect(20, 80, 280, 80)
                
                p.setFont(QFont("Arial", 16, QFont.Weight.Bold))
                p.drawText(35, 110, f"Cible à trouver : {CONFIG['TARGET_RAW']}")
                
                is_good_force = (self.f_min <= current_force <= self.f_max)
                p.setPen(Qt.GlobalColor.green if is_good_force else Qt.GlobalColor.red)
                p.drawText(35, 140, f"Pression actuelle : {int(current_force)}")
            
            p.setPen(QPen(Qt.GlobalColor.gray, 2))
            p.drawLine(QPointF(cx-15, sy), QPointF(cx+15, sy)); p.drawLine(QPointF(cx, sy-15), QPointF(cx, sy+15))
            
            color = Qt.GlobalColor.red 
            if dist < 30:
                is_good_force = (self.f_min <= current_force <= self.f_max) if task_type == "FVP" else (self.pressure > 0.05)
                if is_good_force: color = Qt.GlobalColor.green
                
            p.setPen(QPen(color, 4))
            p.drawLine(QPointF(cx-20, sy), QPointF(cx+20, sy)); p.drawLine(QPointF(cx, sy-20), QPointF(cx, sy+20))
            
            if self.state == "COUNTDOWN":
                p.setPen(Qt.GlobalColor.yellow)
                p.setFont(QFont("Arial", 120, QFont.Weight.Bold))
                p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, str(self.cd_val))
                
        if self.state == "RECORDING" and hasattr(self, 'go_timer') and (time.perf_counter() - self.go_timer < 1.0):
            p.setPen(Qt.GlobalColor.green); p.setFont(QFont("Arial", 120, QFont.Weight.Bold))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "GO !")

        # ==============================================================
        # --- NOUVEAUTÉ : DESSIN DE LA JAUGE DE FORCE AU CENTRE ---
        # ==============================================================
        show_gauge = False
        if task_type == "FVP":
            if has_feedback:
                if self.state in ["WAIT_POS", "COUNTDOWN", "RECORDING"]:
                    show_gauge = True
            else:
                if self.state in ["WAIT_POS", "COUNTDOWN"]:
                    show_gauge = True

        if show_gauge:
            current_force = self.pressure * CONFIG["RAW_MAX"]
            gauge_w = 40
            gauge_h = int(R * 1.2) # La hauteur s'adapte pour rester toujours à l'intérieur du cercle
            gauge_x = cx - (gauge_w / 2) # Centré horizontalement
            gauge_y = cy - (gauge_h / 2) # Centré verticalement
            
            target_f = CONFIG["TARGET_RAW"]
            max_f = target_f * 2.0 
            
            # 1. Fond de la jauge (gris sombre, légèrement transparent)
            p.setBrush(QColor(50, 50, 50, 180))
            p.setPen(QPen(Qt.GlobalColor.white, 2))
            p.drawRect(int(gauge_x), int(gauge_y), int(gauge_w), int(gauge_h))
            
            # 2. Remplissage de la force
            fill_h = min(gauge_h, (current_force / max_f) * gauge_h) 
            fill_y = gauge_y + gauge_h - fill_h 
            
            if self.f_min <= current_force <= self.f_max:
                fill_color = QColor(46, 204, 113) # Vert (Parfait)
            elif current_force > self.f_max:
                fill_color = QColor(231, 76, 60)  # Rouge (Trop fort)
            else:
                fill_color = QColor(241, 196, 15) # Jaune (Trop faible)
                
            p.setBrush(fill_color)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRect(int(gauge_x), int(fill_y), int(gauge_w), int(fill_h))
            
            # 3. Dessin de la zone cible (Cyan)
            zone_y_max = gauge_y + gauge_h - (self.f_min / max_f) * gauge_h
            zone_y_min = gauge_y + gauge_h - (self.f_max / max_f) * gauge_h
            zone_h = zone_y_max - zone_y_min
            
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(Qt.GlobalColor.cyan, 3))
            p.drawRect(int(gauge_x - 5), int(zone_y_min), int(gauge_w + 10), int(zone_h))
            
            # 4. Ligne cible centrale
            center_y = gauge_y + gauge_h / 2
            p.setPen(QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.DashLine))
            p.drawLine(int(gauge_x - 10), int(center_y), int(gauge_x + gauge_w + 10), int(center_y))
            
            # 5. Étiquettes
            p.setPen(Qt.GlobalColor.white)
            p.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            p.drawText(int(cx - 35), int(gauge_y - 15), "FORCE")
            
            p.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            p.drawText(int(gauge_x + gauge_w + 15), int(center_y + 5), "CIBLE")
        # ==============================================================

        current_th = self.get_pointer_thickness(self.pressure, task_type, has_feedback)
        col_pointer = self.get_pointer_color(self.pos.x(), self.pos.y(), R, W) if has_feedback else Qt.GlobalColor.lightGray
        
        p.setBrush(col_pointer); p.setPen(QPen(Qt.GlobalColor.black, 1))
        p.drawEllipse(self.pos, current_th/2 + 2, current_th/2 + 2)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Space:
            if self.state == "PRACTICE_END":
                self.is_practice = False
                self.state = "WAIT_POS"
        if e.key() == Qt.Key.Key_Escape: 
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    d_config = ConfigDialog()
    if d_config.exec():
        settings = d_config.get_settings()
        
        d_demo = DemographicsDialog()
        if d_demo.exec():
            demo_data = d_demo.get_demographics()
            
            ex = SteeringExpe(settings, demo_data)
            first = ex.sequence[0]
            instr = InstructionDialog(first['Task'], first['Feedback'], is_first=True)
            instr.exec()
            ex.show()
            sys.exit(app.exec())