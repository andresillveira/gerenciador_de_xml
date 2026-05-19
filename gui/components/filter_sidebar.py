from PySide6.QtCore import Signal, QDate, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, 
    QDateEdit, QPushButton, QFormLayout, QHBoxLayout, QFrame
)
from typing import Dict, Any, List

class FilterSidebar(QFrame):
    """
    Painel lateral esquerdo com controles de filtro avançado para pesquisa instantânea.
    Dispara o sinal 'filters_changed' contendo um dicionário com todos os filtros ativos.
    """
    filters_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarFrame")
        self.setFixedWidth(280)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)
        
        # Título da Seção
        title = QLabel("Filtros Avançados")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        
        # Formulário para filtros
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        
        # 1. Pesquisa Global
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Chave, Nº, CNPJ, Razão...")
        self.search_input.textChanged.connect(self.emit_filters)
        form_layout.addRow("Pesquisa:", self.search_input)
        
        # 2. Modelo
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Todos", "NF-e (55)", "NFC-e (65)", "CT-e (57)"])
        self.model_combo.currentIndexChanged.connect(self.emit_filters)
        form_layout.addRow("Modelo:", self.model_combo)
        
        # 3. Tipo (Entrada/Saída)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Todos", "Entrada", "Saída"])
        self.type_combo.currentIndexChanged.connect(self.emit_filters)
        form_layout.addRow("Tipo:", self.type_combo)
        
        # 4. Emitente (Carregado dinamicamente)
        self.emit_combo = QComboBox()
        self.emit_combo.addItem("Todos", "")
        self.emit_combo.currentIndexChanged.connect(self.emit_filters)
        form_layout.addRow("Emitente:", self.emit_combo)
        
        # 5. Destinatário (Carregado dinamicamente)
        self.dest_combo = QComboBox()
        self.dest_combo.addItem("Todos", "")
        self.dest_combo.currentIndexChanged.connect(self.emit_filters)
        form_layout.addRow("Destinatário:", self.dest_combo)
        
        # 6. Data Emissão (Período)
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate.currentDate().addMonths(-3)) # Padrão: últimos 3 meses
        self.date_start.dateChanged.connect(self.emit_filters)
        
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate())
        self.date_end.dateChanged.connect(self.emit_filters)
        
        # Checkbox ou controle para ignorar datas
        self.use_date_btn = QPushButton("Habilitar Período")
        self.use_date_btn.setObjectName("secondaryButton")
        self.use_date_btn.setCheckable(True)
        self.use_date_btn.setChecked(False)
        self.use_date_btn.toggled.connect(self.toggle_dates)
        
        # Widgets de data iniciam desabilitados
        self.date_start.setEnabled(False)
        self.date_end.setEnabled(False)
        
        form_layout.addRow(self.use_date_btn)
        form_layout.addRow("De:", self.date_start)
        form_layout.addRow("Até:", self.date_end)
        
        # 7. Valores
        self.val_min = QLineEdit()
        self.val_min.setPlaceholderText("R$ Min")
        self.val_min.textChanged.connect(self.emit_filters)
        
        self.val_max = QLineEdit()
        self.val_max.setPlaceholderText("R$ Max")
        self.val_max.textChanged.connect(self.emit_filters)
        
        val_layout = QHBoxLayout()
        val_layout.addWidget(self.val_min)
        val_layout.addWidget(self.val_max)
        
        form_layout.addRow("Valores:", val_layout)
        
        layout.addLayout(form_layout)
        
        layout.addStretch()
        
        # Botões de Ação
        btn_layout = QHBoxLayout()
        self.clear_btn = QPushButton("Limpar")
        self.clear_btn.setObjectName("secondaryButton")
        self.clear_btn.clicked.connect(self.clear_filters)
        
        self.filter_btn = QPushButton("Filtrar")
        self.filter_btn.clicked.connect(self.emit_filters)
        
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.filter_btn)
        layout.addLayout(btn_layout)

    def toggle_dates(self, checked: bool):
        """Habilita ou desabilita os seletores de data conforme checkbox."""
        self.date_start.setEnabled(checked)
        self.date_end.setEnabled(checked)
        self.use_date_btn.setText("Filtrar por Período" if checked else "Habilitar Período")
        self.emit_filters()

    def update_combos(self, emitentes: List[Dict[str, str]], destinatarios: List[Dict[str, str]]):
        """Atualiza dinamicamente as opções de Emitente e Destinatário."""
        # Desconecta para não disparar eventos a cada adição
        self.emit_combo.blockSignals(True)
        self.dest_combo.blockSignals(True)
        
        # Guarda seleção atual
        current_emit = self.emit_combo.currentData()
        current_dest = self.dest_combo.currentData()
        
        self.emit_combo.clear()
        self.emit_combo.addItem("Todos", "")
        for emit in emitentes:
            self.emit_combo.addItem(f"{emit['nome'][:25]}... ({emit['cnpj']})", emit["cnpj"])
            
        self.dest_combo.clear()
        self.dest_combo.addItem("Todos", "")
        for dest in destinatarios:
            self.dest_combo.addItem(f"{dest['nome'][:25]}... ({dest['cnpj']})", dest["cnpj"])
            
        # Restaura seleção se existir
        idx_emit = self.emit_combo.findData(current_emit)
        if idx_emit >= 0: self.emit_combo.setCurrentIndex(idx_emit)
        
        idx_dest = self.dest_combo.findData(current_dest)
        if idx_dest >= 0: self.dest_combo.setCurrentIndex(idx_dest)
        
        self.emit_combo.blockSignals(False)
        self.dest_combo.blockSignals(False)

    def clear_filters(self):
        """Reseta todos os inputs de filtros para o estado original."""
        self.search_input.blockSignals(True)
        self.model_combo.blockSignals(True)
        self.type_combo.blockSignals(True)
        self.emit_combo.blockSignals(True)
        self.dest_combo.blockSignals(True)
        self.date_start.blockSignals(True)
        self.date_end.blockSignals(True)
        self.val_min.blockSignals(True)
        self.val_max.blockSignals(True)
        
        self.search_input.clear()
        self.model_combo.setCurrentIndex(0)
        self.type_combo.setCurrentIndex(0)
        self.emit_combo.setCurrentIndex(0)
        self.dest_combo.setCurrentIndex(0)
        
        self.date_start.setDate(QDate.currentDate().addMonths(-3))
        self.date_end.setDate(QDate.currentDate())
        self.use_date_btn.setChecked(False)
        self.date_start.setEnabled(False)
        self.date_end.setEnabled(False)
        self.use_date_btn.setText("Habilitar Período")
        
        self.val_min.clear()
        self.val_max.clear()
        
        self.search_input.blockSignals(False)
        self.model_combo.blockSignals(False)
        self.type_combo.blockSignals(False)
        self.emit_combo.blockSignals(False)
        self.dest_combo.blockSignals(False)
        self.date_start.blockSignals(False)
        self.date_end.blockSignals(False)
        self.val_min.blockSignals(False)
        self.val_max.blockSignals(False)
        
        self.emit_filters()

    def get_filters(self) -> Dict[str, Any]:
        """Constrói e retorna o dicionário com os filtros ativos."""
        filters = {}
        
        # 1. Pesquisa Global
        search_txt = self.search_input.text().strip()
        if search_txt:
            filters["search"] = search_txt
            
        # 2. Modelo
        model_idx = self.model_combo.currentIndex()
        if model_idx == 1: filters["modelo"] = 55
        elif model_idx == 2: filters["modelo"] = 65
        elif model_idx == 3: filters["modelo"] = 57
        
        # 3. Tipo (Entrada/Saída)
        type_idx = self.type_combo.currentIndex()
        if type_idx == 1: filters["tipo_nf"] = 0 # Entrada
        elif type_idx == 2: filters["tipo_nf"] = 1 # Saída
        
        # 4. Emitente
        emit_cnpj = self.emit_combo.currentData()
        if emit_cnpj:
            filters["cnpj_emitente"] = emit_cnpj
            
        # 5. Destinatário
        dest_cnpj = self.dest_combo.currentData()
        if dest_cnpj:
            filters["cnpj_destinatario"] = dest_cnpj
            
        # 6. Datas
        if self.use_date_btn.isChecked():
            filters["data_inicio"] = self.date_start.date().toString("yyyy-MM-dd")
            filters["data_fim"] = self.date_end.date().toString("yyyy-MM-dd")
            
        # 7. Valores
        try:
            val_min_str = self.val_min.text().replace(",", ".").strip()
            if val_min_str:
                filters["valor_min"] = float(val_min_str)
        except ValueError:
            pass
            
        try:
            val_max_str = self.val_max.text().replace(",", ".").strip()
            if val_max_str:
                filters["valor_max"] = float(val_max_str)
        except ValueError:
            pass
            
        return filters

    def emit_filters(self):
        """Emite o sinal com os filtros atuais."""
        self.filters_changed.emit(self.get_filters())
