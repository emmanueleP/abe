import os
from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfWriter, PdfReader
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from openpyxl import load_workbook, drawing
from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill, Font as XLFont, Alignment
import io
from .utils import generate_protocol, get_output_path
from .settings import ordina_settings as settings
import json
from datetime import datetime
from .database import ProtocolDatabase

db = ProtocolDatabase()

def handle_file(file_path):
    """Gestisce la protocollazione del file."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError("Il file non esiste")

        protocol_number, timestamp = generate_protocol()
        output_path = get_output_path(file_path)
        
        # Assicurati che la directory di output esista
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Gestisci il file in base al tipo
        if file_path.lower().endswith((".png", ".jpg", ".jpeg")):
            result = add_stamp_to_image(file_path, protocol_number, timestamp)
        elif file_path.lower().endswith(".pdf"):
            result = add_stamp_to_pdf(file_path, protocol_number, timestamp)
        elif file_path.lower().endswith(".docx"):
            result = add_stamp_to_docx(file_path, protocol_number, timestamp)
        elif file_path.lower().endswith(".xlsx"):
            result = add_stamp_to_xlsx(file_path, protocol_number, timestamp)
        else:
            return "Formato file non supportato."
        
        # Salva nel database
        db.add_entry(protocol_number, output_path)
        
        return f"Documento protocollato con successo!\nNumero protocollo: {protocol_number}\nSalvato in: {output_path}"
            
    except Exception as e:
        raise Exception(f"Errore durante la protocollazione: {str(e)}")

def add_stamp_to_image(file_path, protocol, timestamp):
    """Aggiunge il timbro di protocollo all'immagine."""
    try:
        with Image.open(file_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 36)
            except:
                font = ImageFont.load_default()
            
            stamp_text = f"{protocol}\n{timestamp}"
            margin = 20
            position = (margin, margin)
            
            # Aggiungi sfondo semi-trasparente
            text_bbox = draw.textbbox(position, stamp_text, font=font)
            padding = 10
            draw.rectangle(
                [
                    text_bbox[0] - padding,
                    text_bbox[1] - padding,
                    text_bbox[2] + padding,
                    text_bbox[3] + padding
                ],
                fill=(255, 255, 255, 128)
            )
            
            draw.text(position, stamp_text, fill=(255, 0, 0), font=font)
            
            output_path = get_output_path(file_path)
            img.save(output_path, quality=95)
            
            return output_path
            
    except Exception as e:
        raise Exception(f"Errore durante la protocollazione dell'immagine: {str(e)}")

def add_stamp_to_pdf(file_path, protocol, timestamp):
    """Aggiunge il timbro di protocollo al PDF."""
    try:
        # Crea un'immagine con il timbro
        width, height = 600, 200
        img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Aggiungi il testo del protocollo
        stamp_text = f"{protocol}\n{timestamp}"
        draw.text((20, 20), stamp_text, fill=(255, 0, 0), font=font)
        
        # Converti l'immagine in PDF
        pdf_bytes = io.BytesIO()
        img.save(pdf_bytes, format='PDF')
        pdf_bytes.seek(0)
        stamp_page = PdfReader(pdf_bytes).pages[0]
        
        # Applica il timbro al PDF
        reader = PdfReader(file_path)
        writer = PdfWriter()
        
        # Aggiungi il timbro solo alla prima pagina
        for i, page in enumerate(reader.pages):
            if i == 0:
                page.merge_page(stamp_page)
            writer.add_page(page)
        
        # Salva il PDF
        output_path = get_output_path(file_path)
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
            
        return output_path
        
    except Exception as e:
        raise Exception(f"Errore durante la protocollazione del PDF: {str(e)}")

def add_stamp_to_docx(file_path, protocol, timestamp):
    """Aggiunge il timbro di protocollo al documento Word."""
    try:
        # Carica il documento
        doc = Document(file_path)
        
        # Aggiungi una sezione all'inizio del documento
        section = doc.sections[0]
        header = section.header
        
        # Aggiungi il testo del protocollo nell'header
        paragraph = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        run = paragraph.add_run(f"{protocol}\n{timestamp}")
        font = run.font
        font.name = 'Arial'
        font.size = Pt(12)
        font.color.rgb = RGBColor(255, 0, 0)
        
        # Salva il documento
        output_path = get_output_path(file_path)
        doc.save(output_path)
        
        return output_path
        
    except Exception as e:
        raise Exception(f"Errore durante la protocollazione del documento Word: {str(e)}")

def add_stamp_to_xlsx(file_path, protocol, timestamp):
    """Aggiunge il timbro di protocollo al foglio Excel."""
    try:
        # Carica il workbook
        wb = load_workbook(file_path)
        ws = wb.active
        
        # Aggiungi il testo del protocollo in alto a sinistra
        stamp_text = f"{protocol}\n{timestamp}"
        ws['A1'] = stamp_text
        
        # Formatta la cella
        cell = ws['A1']
        cell.font = XLFont(name='Arial', size=12, color='FF0000')
        cell.alignment = Alignment(wrap_text=True)
        ws.row_dimensions[1].height = 40
        
        # Salva il file
        output_path = get_output_path(file_path)
        wb.save(output_path)
        
        return output_path
        
    except Exception as e:
        raise Exception(f"Errore durante la protocollazione del foglio Excel: {str(e)}")