from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtWidgets import QTableView, QHeaderView
from PySide6.QtGui import QColor
from typing import List, Dict, Any, Optional
from datetime import datetime

class XMLTableModel(QAbstractTableModel):
    """
    Model de tabela personalizado para carregar e exibir grandes volumes de documentos fiscais XML
    de forma extremamente veloz e sem travar a memória.
    """
    
    COLUMNS = [
        "Modelo",
        "Número",
        "Série",
        "Tipo",
        "Data Emissão",
        "Emitente",
        "Destinatário",
        "Valor Total",
        "Chave de Acesso"
    ]
    
    def __init__(self, documents: Optional[List[Dict[str, Any]]] = None):
        super().__init__()
        self.documents: List[Dict[str, Any]] = documents or []
        
    def set_documents(self, documents: List[Dict[str, Any]]):
        self.beginResetModel()
        self.documents = documents
        self.endResetModel()
        
    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.documents)
        
    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.COLUMNS)
        
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
            
        row = index.row()
        col = index.column()
        
        if row >= len(self.documents):
            return None
            
        doc = self.documents[row]
        
        # Alinhamentos
        if role == Qt.TextAlignmentRole:
            if col in (0, 1, 2, 3, 4):  # Modelo, Num, Serie, Tipo, Data
                return Qt.AlignCenter
            if col == 7:  # Valor Total
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter
            
        # Cores e estilizações com base no tipo da nota (Entrada/Saída)
        if role == Qt.ForegroundRole:
            if col == 3:  # Tipo da nota
                tipo = doc.get("tipo_nf")
                if tipo == 0:  # Entrada
                    return QColor("#f43f5e")  # Rosa/Vermelho suave
                elif tipo == 1:  # Saída
                    return QColor("#10b981")  # Verde esmeralda suave
            elif col == 7:  # Valor
                return QColor("#6366f1")  # Roxo
                
        # Retorno de exibição de dados
        if role == Qt.DisplayRole:
            if col == 0:  # Modelo
                mod = doc.get("modelo")
                if mod == 55: return "NF-e (55)"
                if mod == 65: return "NFC-e (65)"
                if mod == 57: return "CT-e (57)"
                return f"Mod {mod}"
                
            elif col == 1:  # Número
                return doc.get("numero")
                
            elif col == 2:  # Série
                return doc.get("serie")
                
            elif col == 3:  # Tipo
                tipo = doc.get("tipo_nf")
                if tipo == 0: return "Entrada"
                if tipo == 1: return "Saída"
                return "-"
                
            elif col == 4:  # Data Emissão
                dt_str = doc.get("data_emissao")
                if not dt_str:
                    return ""
                try:
                    # Tenta parsear datas no formato ISO: "2026-05-19T20:30:00-03:00"
                    # ou simplificada.
                    # Pega os primeiros 19 caracteres
                    dt_parsed = datetime.strptime(dt_str[:19], "%Y-%m-%dT%H:%M:%S")
                    return dt_parsed.strftime("%d/%m/%Y %H:%M")
                except ValueError:
                    try:
                        # Tenta sem hora (YYYY-MM-DD)
                        dt_parsed = datetime.strptime(dt_str[:10], "%Y-%m-%d")
                        return dt_parsed.strftime("%d/%m/%Y")
                    except ValueError:
                        return dt_str
                        
            elif col == 5:  # Emitente
                cnpj = format_cnpj_cpf(doc.get("cnpj_emitente"))
                nome = doc.get("nome_emitente") or ""
                return f"{nome} ({cnpj})" if nome else cnpj
                
            elif col == 6:  # Destinatário
                cnpj = format_cnpj_cpf(doc.get("cnpj_destinatario"))
                nome = doc.get("nome_destinatario") or ""
                return f"{nome} ({cnpj})" if nome else cnpj
                
            elif col == 7:  # Valor Total
                val = doc.get("valor_total") or 0.0
                return f"R$ {val:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
                
            elif col == 8:  # Chave de Acesso
                return doc.get("chave_acesso")
                
        return None
        
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role != Qt.DisplayRole:
            return None
            
        if orientation == Qt.Horizontal:
            return self.COLUMNS[section]
            
        return section + 1

    def get_document(self, row: int) -> Optional[Dict[str, Any]]:
        """Retorna o dicionário de documento fiscal da linha indicada."""
        if 0 <= row < len(self.documents):
            return self.documents[row]
        return None


class XMLTableView(QTableView):
    """
    QTableView personalizado e estilizado para exibição de documentos XML fiscais.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        self.setEditTriggers(QTableView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        
        # Otimizações de renderização
        self.setWordWrap(False)
        self.setHorizontalScrollMode(QTableView.ScrollPerPixel)
        self.setVerticalScrollMode(QTableView.ScrollPerItem)
        
        # Estilos dos Headers
        header = self.horizontalHeader()
        header.setHighlightSections(False)
        header.setSectionsMovable(True)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
    def adjust_columns(self):
        """Ajusta a largura das colunas dinamicamente."""
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # Definir larguras ideais padrão
        self.setColumnWidth(0, 100) # Modelo
        self.setColumnWidth(1, 90)  # Numero
        self.setColumnWidth(2, 70)  # Serie
        self.setColumnWidth(3, 80)  # Tipo
        self.setColumnWidth(4, 130) # Data Emissão
        self.setColumnWidth(5, 250) # Emitente
        self.setColumnWidth(6, 250) # Destinatário
        self.setColumnWidth(7, 120) # Valor Total
        self.setColumnWidth(8, 300) # Chave
        

def format_cnpj_cpf(val: Optional[str]) -> str:
    """Formata strings de CNPJ ou CPF para legibilidade."""
    if not val:
        return ""
    # Remove caracteres não numéricos
    clean = ''.join(c for c in val if c.isdigit())
    
    if len(clean) == 14:
        # CNPJ: 00.000.000/0000-00
        return f"{clean[0:2]}.{clean[2:5]}.{clean[5:8]}/{clean[8:12]}-{clean[12:14]}"
    elif len(clean) == 11:
        # CPF: 000.000.000-00
        return f"{clean[0:3]}.{clean[3:6]}.{clean[6:9]}-{clean[9:11]}"
    return val
