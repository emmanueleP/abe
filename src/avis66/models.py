from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
import pandas as pd
from .settings import avis_settings as settings

class AvisTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.columns = [chr(65 + i) for i in range(23)]  # A to W
        
        # Crea DataFrame con la prima riga contenente i valori predefiniti
        header_row = {col: settings.get_column_name(col) for col in self.columns}
        self._data = pd.DataFrame([header_row], columns=self.columns)

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
            
        if role == Qt.DisplayRole or role == Qt.EditRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value) if pd.notna(value) else ""
        elif role == Qt.BackgroundRole and index.row() == 0:
            return Qt.lightGray
        
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.row() > 0:
            self._data.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.columns[section]
            else:
                return str(section + 1)
        return None

    def flags(self, index):
        if index.row() == 0:
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def insertRows(self, position, rows, parent=None):
        if position == 0:
            position = 1
            
        self.beginInsertRows(parent or QModelIndex(), position, position + rows - 1)
        for i in range(rows):
            empty_row = pd.DataFrame([[""]*len(self.columns)], columns=self.columns)
            self._data = pd.concat([
                self._data.iloc[:position],
                empty_row,
                self._data.iloc[position:]
            ]).reset_index(drop=True)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=None):
        if position == 0:
            return False
            
        self.beginRemoveRows(parent or QModelIndex(), position, position + rows - 1)
        self._data = pd.concat([
            self._data.iloc[:position],
            self._data.iloc[position + rows:]
        ]).reset_index(drop=True)
        self.endRemoveRows()
        return True

    def load_data(self, data):
        self.beginResetModel()
        header_row = pd.DataFrame([{col: settings.get_column_name(col) for col in self.columns}])
        self._data = pd.concat([header_row, data]).reset_index(drop=True)
        self.endResetModel()

    def get_data(self):
        return self._data