import sys
from PyQt5.QtWidgets import QApplication
from gui import ProtocolGUI
from settings import settings

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    try:
        # Applica stile Material Design
        from qt_material import apply_stylesheet
        theme = f"{settings.get_theme()}_teal.xml"
        apply_stylesheet(app, theme=theme)
    except ImportError:
        print("Installare qt-material con: pip install qt-material")
    
    # Avvia l'interfaccia passando l'istanza di app
    window = ProtocolGUI(app)
    window.show()
    sys.exit(app.exec())
