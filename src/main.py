import sys
import os

# Aggiungi la directory src al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PyQt5.QtWidgets import QApplication
from src.welcome import WelcomeDialog
from src.ordina.settings import ordina_settings as settings

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    try:
        from qt_material import apply_stylesheet
        theme = f"{settings.get_theme()}_teal.xml"
        apply_stylesheet(app, theme=theme)
    except ImportError:
        print("Installare qt-material con: pip install qt-material")
    
    welcome = WelcomeDialog(app)
    welcome.show()
    
    sys.exit(app.exec()) 