from datetime import datetime
import os
from settings import settings

def generate_protocol():
    """
    Genera un numero di protocollo e timestamp.
    
    Returns:
        tuple: (numero_protocollo, timestamp_formattato)
    """
    timestamp = datetime.now()
    protocol_number = settings.get_next_protocol_number()
    timestamp_formatted = timestamp.strftime("%d/%m/%Y %H:%M:%S")
    return protocol_number, timestamp_formatted

def get_output_path(file_path):
    """
    Genera il percorso di output per il file protocollato.
    
    Args:
        file_path (str): Percorso del file originale
        
    Returns:
        str: Percorso del file di output
    """
    filename = os.path.basename(file_path)
    output_dir = settings.get_output_directory()
    return os.path.join(output_dir, f"protocollato_{filename}")
