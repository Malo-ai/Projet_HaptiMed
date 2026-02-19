import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTabletEvent, QFont

class SimpleCalibration(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vérification Stylet (Brut)")
        self.resize(400, 300)
        self.setStyleSheet("background-color: #222; color: white;")
        
        layout = QVBoxLayout()
        
        # Titre
        title = QLabel("TEST PRESSION BRUTE")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Jauge Visuelle
        self.bar = QProgressBar()
        self.bar.setRange(0, 8192)
        # Style : Rouge quand c'est faible, Vert quand c'est fort
        self.bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                height: 50px;
                background-color: #444;
            }
            QProgressBar::chunk {
                background-color: #00ff00; 
            }
        """)
        self.bar.setValue(0)
        layout.addWidget(self.bar)
        
        # Affichage Numérique
        self.val_lbl = QLabel("0")
        self.val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.val_lbl.setFont(QFont("Arial", 50, QFont.Weight.Bold))
        layout.addWidget(self.val_lbl)
        
        # Affichage du MAX atteint (pour voir si on touche le plafond)
        self.max_reached = 0
        self.max_lbl = QLabel("Pic Max atteint : 0")
        self.max_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.max_lbl.setStyleSheet("color: yellow; font-size: 16px;")
        layout.addWidget(self.max_lbl)

        layout.addStretch()
        self.setLayout(layout)

    def tabletEvent(self, e: QTabletEvent):
        # On récupère la pression (0.0 à 1.0) et on convertit en 0-8192
        val = int(e.pressure() * 8192)
        
        # Mise à jour Jauge et Texte
        self.bar.setValue(val)
        self.val_lbl.setText(str(val))
        
        # Mise à jour du Pic Max
        if val > self.max_reached:
            self.max_reached = val
            self.max_lbl.setText(f"Pic Max atteint : {self.max_reached}")
            
        e.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SimpleCalibration()
    ex.show()
    sys.exit(app.exec())