import sys
import argparse
import os
import json
import shutil
from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet
from src.welcome import WelcomeDialog
from src.ordina.gui import ProtocolGUI
from src.avis66.gui import AvisGUI
from src.pdftoa.gui import PDFtoAGUI
from src.manrev.gui import ManRevGUI
from src.cbp.gui import CbpGUI
from src.agenda.gui import AgendaGUI

def reset_settings(app_name):
    """Resetta le impostazioni di un'applicazione specifica"""
    config_dir = os.path.join(os.path.dirname(__file__), 'data', 'config')
    
    if app_name == 'suite':
        # Resetta tutte le configurazioni
        if os.path.exists(config_dir):
            shutil.rmtree(config_dir)
            os.makedirs(config_dir)
        print("Configurazioni di tutte le applicazioni resettate")
        return
    
    # Mappa delle configurazioni per app
    config_files = {
        'ordina': 'ordina_config.json',
        'avis66': 'avis66_config.json',
        'pdftoa': 'pdftoa_config.json',
        'manrev': 'manrev_config.json',
        'cbp': 'cbp_config.json',
        'agenda': 'agenda_config.json'
    }
    
    if app_name in config_files:
        config_file = os.path.join(config_dir, config_files[app_name])
        if os.path.exists(config_file):
            os.remove(config_file)
            print(f"Configurazione di {app_name} resettata")
        else:
            print(f"Nessuna configurazione trovata per {app_name}")

def main():
    # Configura il parser degli argomenti
    parser = argparse.ArgumentParser(description='Abe-Gestionale Development Tool')
    
    # Argomenti
    parser.add_argument('--app', type=str, choices=['suite', 'ordina', 'avis66', 'pdftoa', 'manrev', 'cbp', 'agenda'],
                      help='Applicazione da avviare', default='suite')
    parser.add_argument('--theme', type=str, choices=['light', 'dark'],
                      help='Tema da utilizzare', default='dark')
    parser.add_argument('--reset', action='store_true',
                      help='Resetta le impostazioni dell\'applicazione')
    
    args = parser.parse_args()

    # Se richiesto il reset, esegui e termina
    if args.reset:
        reset_settings(args.app)
        return

    # Crea l'applicazione Qt
    app = QApplication(sys.argv)
    
    # Applica il tema
    theme = f"{args.theme}_teal.xml"
    apply_stylesheet(app, theme=theme)
    
    # Avvia l'applicazione richiesta
    if args.app == 'suite':
        window = WelcomeDialog(app)
    elif args.app == 'ordina':
        window = ProtocolGUI(app)
    elif args.app == 'avis66':
        window = AvisGUI(app)
    elif args.app == 'pdftoa':
        window = PDFtoAGUI(app)
    elif args.app == 'manrev':
        window = ManRevGUI(app)
    elif args.app == 'cbp':
        window = CbpGUI(app)
    elif args.app == 'agenda':
        window = AgendaGUI(app)
    
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

#Lista comandi dev
#Avvia intera suite
# python dev.py --app suite
#python dev.py

#Avvia un'applicazione specifica
# python dev.py --app NOMEAPP

#Resetta configurazione di un'applicazione
# python dev.py --app NOMEAPP --reset

#Resetta tutte le configurazioni
# python dev.py --app suite --reset

#Vedi opzioni
# python dev.py --help

