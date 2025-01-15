import os
from datetime import datetime
from .settings import ordina_settings as settings
from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtGui import QImage, QPainter, QFont, QColor
from PyQt5.QtCore import Qt, QRectF

def generate_protocol():
    """Genera il prossimo numero di protocollo"""
    return settings.get_next_protocol_number()

def get_output_path(original_path):
    """Genera il percorso di output per il file protocollato"""
    try:
        filename = os.path.basename(original_path)
        name, ext = os.path.splitext(filename)
        
        # Ottieni il numero di protocollo
        protocol = generate_protocol()
        if not protocol:
            raise Exception("Errore nella generazione del numero di protocollo")
            
        print(f"Generated protocol: {protocol}")  # Debug
        
        # Crea il nome del file
        new_name = f"{name}__{protocol}{ext}"
        print(f"New filename: {new_name}")  # Debug
        
        # Crea il percorso completo
        year_folder = os.path.join(settings.get_output_directory(), settings.current_settings["year"])
        os.makedirs(year_folder, exist_ok=True)
        
        full_path = os.path.join(year_folder, new_name)
        print(f"Full output path: {full_path}")  # Debug
        
        return full_path
        
    except Exception as e:
        print(f"DEBUG - Errore in get_output_path: {str(e)}")  # Debug
        raise Exception(f"Errore nella generazione del percorso di output: {str(e)}")

def create_stamp(protocol_number):
    """Crea il timbro come immagine"""
    stamp_settings = settings.current_settings["stamp_settings"]
    
    # Crea un'immagine QImage con sfondo trasparente
    img = QImage(stamp_settings["width"], stamp_settings["height"], QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    
    # Prepara il painter
    painter = QPainter(img)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Imposta il font
    font = QFont(stamp_settings["font_family"])
    font.setPointSize(stamp_settings["font_size"])
    painter.setFont(font)
    
    # Imposta il colore
    painter.setPen(QColor(stamp_settings["text_color"]))
    
    # Prepara il testo
    text = stamp_settings["text"]
    text = text.replace("{number}", protocol_number)
    text = text.replace("{date}", datetime.now().strftime("%d/%m/%Y"))
    text = text.replace("{location}", settings.current_settings.get("location", "Cagliari"))
    
    # Disegna il testo
    rect = QRectF(0, 0, img.width(), img.height())
    painter.drawText(rect, Qt.AlignCenter, text)
    
    painter.end()
    
    # Converti QImage in PIL Image
    buffer = img.bits().asstring(img.byteCount())
    pil_image = Image.frombytes('RGBA', (img.width(), img.height()), buffer)
    
    return pil_image 