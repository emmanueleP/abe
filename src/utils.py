import os
import sys
import platform
from .paths import path_manager

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

def get_data_path(app_name, filename):
    """
    Ottiene il percorso per un file di dati specifico dell'applicazione
    """
    if app_name == "ordina":
        base_dir = path_manager.ordina_dir
    elif app_name == "avis66":
        base_dir = path_manager.avis_dir
    elif app_name == "pdftoa":
        base_dir = path_manager.pdftoa_dir
    elif app_name == "manrev":
        base_dir = path_manager.manrev_dir
    elif app_name == "cbp":
        base_dir = path_manager.cbp_dir
    elif app_name == "agenda":
        base_dir = path_manager.agenda_dir
    else:
        base_dir = path_manager.app_dir
        
    return os.path.join(base_dir, filename)

def get_config_path(app_name):
    """
    Ottiene il percorso del file di configurazione per un'applicazione
    """
    return path_manager.get_config_path(app_name) 