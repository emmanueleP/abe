import re
import numpy as np

class FormulaCalculator:
    def __init__(self):
        self.functions = {
            'SUM': np.sum,
            'AVG': np.mean,
            'MIN': np.min,
            'MAX': np.max,
            'COUNT': len,
            'ROUND': np.round
        }
    
    def evaluate(self, formula, table):
        """Valuta una formula Excel-like"""
        if not formula.startswith("="):
            return float(formula)
            
        # Rimuovi il segno =
        formula = formula[1:]
        
        # Trova tutte le referenze alle celle (es. B2:B10)
        cell_refs = re.findall(r'([A-Z]+[0-9]+(?::[A-Z]+[0-9]+)?)', formula)
        
        for ref in cell_refs:
            if ":" in ref:
                # Range di celle
                start, end = ref.split(":")
                values = self.get_range_values(start, end, table)
                formula = formula.replace(ref, str(values))
            else:
                # Singola cella
                value = self.get_cell_value(ref, table)
                formula = formula.replace(ref, str(value))
        
        # Sostituisci le funzioni Excel con le funzioni numpy
        for excel_func, np_func in self.functions.items():
            if excel_func in formula:
                formula = formula.replace(excel_func, "np_func")
        
        try:
            return eval(formula, {"np_func": self.functions}, {})
        except:
            return 0
    
    def get_cell_value(self, ref, table):
        """Ottiene il valore di una cella"""
        col = ord(ref[0]) - ord('A')
        row = int(ref[1:]) - 1
        
        item = table.item(row, col)
        if item and item.text():
            try:
                return float(item.text().replace("€", "").replace(",", ""))
            except:
                return 0
        return 0
    
    def get_range_values(self, start, end, table):
        """Ottiene i valori da un range di celle"""
        start_col = ord(start[0]) - ord('A')
        start_row = int(start[1:]) - 1
        end_col = ord(end[0]) - ord('A')
        end_row = int(end[1:]) - 1
        
        values = []
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                item = table.item(row, col)
                if item and item.text():
                    try:
                        values.append(float(item.text().replace("€", "").replace(",", "")))
                    except:
                        values.append(0)
                else:
                    values.append(0)
        
        return values 