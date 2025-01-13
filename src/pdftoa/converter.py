import pikepdf
import os

class PDFConverter:
    @staticmethod
    def convert_to_pdfa(input_path, output_path=None):
        """
        Converte un PDF in PDF/A usando pikepdf.
        
        Args:
            input_path (str): Percorso del file PDF da convertire
            output_path (str, optional): Percorso dove salvare il PDF/A.
                                       Se None, usa il nome del file originale + "_PDFA"
        
        Returns:
            str: Percorso del file convertito
        """
        try:
            # Se non è specificato un output_path, ne crea uno
            if output_path is None:
                base_path = os.path.splitext(input_path)[0]
                output_path = f"{base_path}.pdf"

            # Apri il PDF
            with pikepdf.Pdf.open(input_path) as pdf:
                # Imposta i metadati per PDF/A
                with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:
                    meta['pdf:Producer'] = 'Abe-Gestionale PDFtoA Converter'
                    meta['dc:title'] = os.path.basename(input_path)
                    meta['pdf:PDFVersion'] = '1.7'
                    meta['pdfaid:part'] = '2'  # PDF/A-2
                    meta['pdfaid:conformance'] = 'B'  # Level B

                # Salva come PDF/A
                pdf.save(output_path, 
                    linearize=True,  # Ottimizzazione
                    object_stream_mode=pikepdf.ObjectStreamMode.generate,
                    compress_streams=True
                )
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Errore durante la conversione: {str(e)}") 