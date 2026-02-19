import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QTabletEvent

class PressureTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wacom PTK-870 Test")
        self.setGeometry(100, 100, 400, 200)
        print("Appuyez avec le Pro Pen 3 sur la tablette...")

    def tabletEvent(self, event):
        # Récupère la pression entre 0.0 (rien) et 1.0 (max)
        pressure = event.pressure()
        # Convertit en niveaux bruts (8192 pour la PTK-870)
        raw_pressure = int(pressure * 8192)
        
        print(f"Pression: {pressure:.4f} | Raw (0-8192): {raw_pressure}", end='\r')
        sys.stdout.flush()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PressureTest()
    window.show()
    sys.exit(app.exec())