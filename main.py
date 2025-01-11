import sys
import os

# Aggiungi la directory src al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from src.welcome import WelcomeDialog
from src.ordina.settings import ordina_settings
from src.avis66.settings import avis_settings
from src.utils import get_asset_path

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(get_asset_path('logo_abe.ico')))
    
    try:
        from qt_material import apply_stylesheet
        # Usiamo il tema di ordina come default
        theme = f"{ordina_settings.get_theme()}_teal.xml"
        apply_stylesheet(app, theme=theme)
    except ImportError:
        print("Installare qt-material con: pip install qt-material")
    
    welcome = WelcomeDialog(app)
    welcome.show()
    
    sys.exit(app.exec())
