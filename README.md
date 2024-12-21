# Abe-Gestionale

Abe-Gestionale è una suite di applicazioni desktop sviluppata da Emmanuele Pani.

## Applicazioni

### Ordina
- Protocollazione automatica di documenti con numerazione progressiva
- Supporto per multipli formati di file (PDF, DOCX, XLSX, immagini)
- Aggiunta automatica di timbro e numerazione
- Cronologia dei documenti protocollati
- Gestione per anno di protocollazione

### AViS66
- Gestione del registro soci e volontari
- Importazione ed esportazione dati da/verso Excel
- Gestione tabellare con 23 colonne personalizzabili
- Selezione multipla e modifica in blocco
- Protezione dei dati di intestazione

### PDFtoA
- Conversione di documenti PDF in formato PDF/A
- Supporto per la conversione multipla
- Monitoraggio del progresso di conversione
- Mantenimento della struttura originale del documento

## Caratteristiche Comuni

- Interfaccia grafica moderna e intuitiva
- Supporto per tema chiaro/scuro
- Configurazione flessibile
- Salvataggio automatico delle impostazioni
- Gestione errori avanzata

## Requisiti di Sistema

- Python 3.8 o superiore
- Dipendenze Python (installabili via pip):
  - PyQt5
  - qt-material
  - Pillow
  - PyPDF2
  - python-docx
  - openpyxl
  - pandas
  - xlsxwriter
  - PyMuPDF

## Installazione

1. Clona il repository:
```bash
git clone https://github.com/emmanueleP/abe.git
cd abe
```

2. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

3. Esegui l'applicazione:
```bash
python main.py
```
## Utilizzo

1. Avvia l'applicazione con `python main.py`
2. Seleziona l'applicazione desiderata dalla schermata principale:
   - **Ordina** per la protocollazione documenti
   - **AViS66** per la gestione soci
   - **PDFtoA** per la conversione PDF
3. Ogni applicazione ha il proprio menu di aiuto e configurazione

## Licenza

Abe-Gestionale è rilasciato sotto la licenza MIT. Vedi il file LICENSE per ulteriori dettagli.

## Contatti

Per qualsiasi domanda o problema, contattare Emmanuele Pani su GitHub.
