import json
import os
from datetime import datetime
from PIL import Image
import base64
from io import BytesIO

class Settings:
    def __init__(self):
        self.settings_file = "config.json"
        user_docs = os.path.join(os.path.expanduser("~"), "Documents")
        self.default_settings = {
            "theme": "dark",
            "year": str(datetime.now().year),
            "last_protocol_number": 0,
            "protocol_format": "PROT-{year}-{number:05d}",
            "output_directory": os.path.join(user_docs, "Protocolli"),
            "stamp_image": None,  # Base64 dell'immagine del timbro
            "stamp_position": "bottom-right"  # Posizione del timbro
        }
        self.current_settings = self.load_settings()

        # Crea la cartella di output se non esiste
        self.ensure_output_directory()

    def load_settings(self):
        """Carica le impostazioni dal file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return {**self.default_settings, **json.load(f)}
            return self.default_settings.copy()
        except Exception:
            return self.default_settings.copy()

    def save_settings(self):
        """Salva le impostazioni su file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.current_settings, f, indent=4)
        except Exception as e:
            print(f"Errore nel salvare le impostazioni: {e}")

    def get_next_protocol_number(self):
        """Genera il prossimo numero di protocollo"""
        current_year = str(datetime.now().year)
        if current_year != self.current_settings["year"]:
            self.current_settings["year"] = current_year
            self.current_settings["last_protocol_number"] = 0
        
        self.current_settings["last_protocol_number"] += 1
        self.save_settings()
        
        return self.current_settings["protocol_format"].format(
            year=self.current_settings["year"],
            number=self.current_settings["last_protocol_number"]
        )

    def get_theme(self):
        """Restituisce il tema corrente"""
        return self.current_settings["theme"]

    def set_theme(self, theme):
        """Imposta il tema"""
        self.current_settings["theme"] = theme
        self.save_settings()

    def set_year(self, year):
        """Imposta l'anno"""
        self.current_settings["year"] = str(year)
        self.current_settings["last_protocol_number"] = 0
        self.save_settings()

    def save_stamp_image(self, image_path):
        """Salva l'immagine del timbro come base64"""
        try:
            with Image.open(image_path) as img:
                # Converti in RGBA e ridimensiona se necessario
                img = img.convert('RGBA')
                # Mantieni le proporzioni ma limita la dimensione massima
                img.thumbnail((200, 200))
                
                # Converti in base64
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                self.current_settings["stamp_image"] = img_str
                self.save_settings()
                return True
        except Exception as e:
            print(f"Errore nel salvare il timbro: {e}")
            return False

    def get_stamp_image(self):
        """Recupera l'immagine del timbro come oggetto PIL.Image"""
        if self.current_settings["stamp_image"]:
            try:
                img_data = base64.b64decode(self.current_settings["stamp_image"])
                return Image.open(BytesIO(img_data))
            except:
                return None
        return None

    def reset_protocol_number(self, year=None):
        """
        Resetta il numero di protocollo per l'anno specificato o corrente.
        
        Args:
            year (str, optional): Anno per cui resettare la numerazione.
                                Se None, usa l'anno corrente nelle impostazioni.
        """
        if year:
            self.current_settings["year"] = str(year)
        self.current_settings["last_protocol_number"] = 0
        self.save_settings()

    def ensure_output_directory(self):
        """Assicura che la cartella di output esista"""
        try:
            year_folder = os.path.join(
                self.current_settings["output_directory"],
                self.current_settings["year"]
            )
            os.makedirs(year_folder, exist_ok=True)
        except Exception as e:
            print(f"Errore nella creazione della cartella di output: {e}")

    def set_output_directory(self, path):
        """Imposta la cartella di output"""
        self.current_settings["output_directory"] = path
        self.save_settings()
        self.ensure_output_directory()

    def get_output_directory(self):
        """Restituisce il percorso della cartella di output per l'anno corrente"""
        return os.path.join(
            self.current_settings["output_directory"],
            self.current_settings["year"]
        )

settings = Settings() 