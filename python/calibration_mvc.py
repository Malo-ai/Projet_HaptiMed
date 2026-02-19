# calibration_mvc.py - VERSION PYQT6 (Compatible Wacom PTK-870)
import sys
import os
import csv
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QProgressBar
from PyQt6.QtGui import QTabletEvent, QFont
from PyQt6.QtCore import Qt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data")
if not os.path.exists(DATA_PATH): os.makedirs(DATA_PATH)

class CalibrationMVC(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calibration Force Maximale (MVC)")
        self.setGeometry(100, 100, 600, 300)
        
        self.max_force = 0
        self.RAW_MAX_WACOM = 8192 # Échelle de ta nouvelle tablette

        # --- INTERFACE GRAPHIQUE ---
        central_widget = QWidget()
        layout = QVBoxLayout()

        self.label_inst = QLabel("Appuyez FORT avec le stylet sur la tablette.\n(Ne cassez pas la mine !)\n\nAppuyez sur ESPACE pour valider et quitter.")
        self.label_inst.setFont(QFont("Arial", 14))
        self.label_inst.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_inst)

        self.label_score = QLabel("Force Max Actuelle : 0")
        self.label_score.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.label_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_score.setStyleSheet("color: #2980b9;")
        layout.addWidget(self.label_score)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(self.RAW_MAX_WACOM)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(40)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #e74c3c; }")
        layout.addWidget(self.progress_bar)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    # --- LECTURE IDENTIQUE AU SCRIPT PRINCIPAL ---
    def tabletEvent(self, event: QTabletEvent):
        # Lecture de la pression 0.0 -> 1.0
        current_pressure_ratio = event.pressure()
        # Conversion en niveaux réels Wacom
        current_force = int(current_pressure_ratio * self.RAW_MAX_WACOM)
        
        # Mise à jour de la barre visuelle
        self.progress_bar.setValue(current_force)

        # Enregistrement du nouveau record
        if current_force > self.max_force:
            self.max_force = current_force
            self.label_score.setText(f"Force Max Actuelle : {self.max_force}")
        
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            print(f"\n[SUCCÈS] Calibration terminée.")
            print(f"-> Force Maximale Volontaire (MVC) retenue : {self.max_force} / {self.RAW_MAX_WACOM}")
            
            # Sauvegarde dans un fichier texte pour s'en souvenir
            with open(os.path.join(DATA_PATH, "last_mvc.txt"), "w") as f:
                f.write(str(self.max_force))
                
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalibrationMVC()
    window.show()
    sys.exit(app.exec())