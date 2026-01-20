import sys
from PyQt6.QtWidgets import QApplication
from gui.app import GPWSimulatorApp

def main():
    app = QApplication(sys.argv)
    window = GPWSimulatorApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
