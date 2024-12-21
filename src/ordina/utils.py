from datetime import datetime
import os
from .settings import ordina_settings as settings

def generate_protocol():
    """Genera un numero di protocollo e timestamp."""
    timestamp = datetime.now()
    protocol_number = settings.get_next_protocol_number()
    timestamp_formatted = timestamp.strftime("%d/%m/%Y %H:%M:%S")
    return protocol_number, timestamp_formatted

def get_output_path(file_path):
    """Genera il percorso di output per il file protocollato."""
    filename = f"protocollato_{os.path.basename(file_path)}"
    output_dir = settings.get_output_directory()
    return os.path.join(output_dir, filename) 