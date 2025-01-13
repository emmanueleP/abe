import os
from PyQt5.QtCore import QFileInfo
from PIL import Image
import fitz  # PyMuPDF
from docx import Document
import openpyxl
from .utils import get_output_path, create_stamp
import io
from .history_dialog import add_to_history

def handle_file(file_path):
    """Gestisce il file in base al suo tipo"""
    try:
        file_info = QFileInfo(file_path)
        extension = file_info.suffix().lower()
        
        # Ottieni il percorso di output
        output_path = get_output_path(file_path)
        
        # Crea il timbro
        stamp = create_stamp(os.path.basename(output_path).split("__")[1].split(".")[0])
        
        if extension == "pdf":
            handle_pdf(file_path, output_path, stamp)
        elif extension == "docx":
            handle_docx(file_path, output_path, stamp)
        elif extension == "xlsx":
            handle_xlsx(file_path, output_path, stamp)
        elif extension in ["png", "jpg", "jpeg"]:
            handle_image(file_path, output_path, stamp)
        else:
            raise ValueError(f"Formato file non supportato: {extension}")
        
        # Aggiungi alla cronologia
        protocol_number = os.path.basename(output_path).split("__")[1].split(".")[0]
        add_to_history(protocol_number, output_path)
        
        return output_path
        
    except Exception as e:
        raise Exception(f"Errore durante la protocollazione: {str(e)}")

def handle_pdf(input_path, output_path, stamp):
    """Gestisce file PDF"""
    # Apri il PDF
    pdf = fitz.open(input_path)
    first_page = pdf[0]
    
    # Converti il timbro in PNG e ottieni i bytes
    img_byte_arr = io.BytesIO()
    stamp.save(img_byte_arr, format='PNG')
    stamp_bytes = img_byte_arr.getvalue()
    
    # Calcola la posizione del timbro (in basso a destra)
    page_rect = first_page.rect
    x = page_rect.width - stamp.width - 50  # 50 pixel dal bordo destro
    y = page_rect.height - stamp.height - 50  # 50 pixel dal bordo inferiore
    
    # Inserisci il timbro
    first_page.insert_image((x, y, x + stamp.width, y + stamp.height), stream=stamp_bytes)
    
    # Salva il PDF
    pdf.save(output_path)
    pdf.close()

def handle_docx(input_path, output_path, stamp):
    """Gestisce file Word"""
    doc = Document(input_path)
    
    # Salva il timbro come immagine temporanea
    temp_stamp = "temp_stamp.png"
    stamp.save(temp_stamp, "PNG")
    
    # Aggiungi il timbro al documento
    doc.add_picture(temp_stamp)
    
    # Salva il documento
    doc.save(output_path)
    
    # Rimuovi il file temporaneo
    os.remove(temp_stamp)

def handle_xlsx(input_path, output_path, stamp):
    """Gestisce file Excel"""
    wb = openpyxl.load_workbook(input_path)
    ws = wb.active
    
    # Salva il timbro come immagine temporanea
    temp_stamp = "temp_stamp.png"
    stamp.save(temp_stamp, "PNG")
    
    # Aggiungi il timbro al foglio
    img = openpyxl.drawing.image.Image(temp_stamp)
    ws.add_image(img, 'A1')
    
    # Salva il file
    wb.save(output_path)
    
    # Rimuovi il file temporaneo
    os.remove(temp_stamp)

def handle_image(input_path, output_path, stamp):
    """Gestisce file immagine"""
    with Image.open(input_path) as img:
        # Converti in RGBA se necessario
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Calcola la posizione del timbro (in basso a destra)
        x = img.width - stamp.width - 50
        y = img.height - stamp.height - 50
        
        # Incolla il timbro
        img.paste(stamp, (x, y), stamp)
        
        # Salva l'immagine
        img.save(output_path)