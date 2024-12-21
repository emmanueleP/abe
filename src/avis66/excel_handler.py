import pandas as pd

def import_from_excel(file_path):
    """Importa dati da un file Excel."""
    try:
        df = pd.read_excel(file_path)
        # Verifica che le colonne corrispondano
        expected_columns = [chr(65 + i) for i in range(23)]
        
        # Se il file non ha intestazioni, aggiungiamole
        if list(df.columns) == list(range(len(expected_columns))):
            df.columns = expected_columns
        # Se le intestazioni non corrispondono, solleviamo un errore
        elif list(df.columns) != expected_columns:
            raise ValueError("La struttura del file Excel non corrisponde")
        
        # Converti tutti i valori in stringhe e gestisci i NaN
        df = df.fillna("")
        return df
    except Exception as e:
        raise Exception(f"Errore durante l'importazione: {str(e)}")

def export_to_excel(data, file_path):
    """Esporta dati in un file Excel."""
    try:
        # Assicurati che il file abbia estensione .xlsx
        if not file_path.endswith('.xlsx'):
            file_path += '.xlsx'

        # Crea una copia del DataFrame per non modificare l'originale
        export_data = data.copy()

        # Rinomina le colonne con i valori della prima riga
        # e poi rimuovi la prima riga che conteneva i nomi delle colonne
        export_data.columns = export_data.iloc[0]
        export_data = export_data.iloc[1:]

        # Resetta gli indici dopo aver rimosso la prima riga
        export_data = export_data.reset_index(drop=True)

        # Crea un nuovo file Excel con xlsxwriter come engine
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            # Esporta i dati senza formattazione
            export_data.to_excel(writer, index=False, sheet_name='Sheet1')
            
            # Ottieni il foglio di lavoro
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            
            # Definisci il formato per tutte le celle
            cell_format = workbook.add_format({
                'font_name': 'Calibri',
                'font_size': 11,
                'border': 0,
                'bold': False
            })
            
            # Applica il formato a tutte le celle
            for row in range(len(export_data) + 1):  # +1 per l'intestazione
                for col in range(len(export_data.columns)):
                    # Ottieni il valore direttamente dal DataFrame
                    if row == 0:
                        value = export_data.columns[col]
                    else:
                        value = export_data.iloc[row-1, col]
                    worksheet.write(row, col, value, cell_format)

    except Exception as e:
        raise Exception(f"Errore durante l'esportazione: {str(e)}") 