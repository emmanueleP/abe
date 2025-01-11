import os
import sys

def get_asset_path(filename):
    """
    Ottiene il percorso corretto per un file nella cartella assets,
    sia in sviluppo che nell'eseguibile
    """
    try:
        # PyInstaller crea una cartella temporanea e memorizza il percorso in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Se non siamo in un eseguibile, usa il percorso normale
        base_path = os.path.abspath(".")

    return os.path.join(base_path, 'src', 'assets', filename) 