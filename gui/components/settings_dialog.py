from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QFileDialog, QFormLayout, QFrame
)
from PySide6.QtCore import Qt
import config

class SettingsDialog(QDialog):
    """
    Diálogo para configurar pasta de XMLs e preferências de tema.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações do Sistema")
        self.setMinimumWidth(450)
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)
        
        # Frame de conteúdo
        frame = QFrame()
        form_layout = QFormLayout(frame)
        form_layout.setSpacing(12)
        
        # 1. Seleção de Diretório
        self.dir_input = QLineEdit()
        self.dir_input.setText(config.get_xml_directory())
        self.dir_input.setPlaceholderText("Selecione a pasta contendo seus XMLs...")
        
        dir_btn = QPushButton("Procurar...")
        dir_btn.setObjectName("secondaryButton")
        dir_btn.clicked.connect(self.browse_directory)
        
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(dir_btn)
        
        form_layout.addRow("Pasta de XMLs:", dir_layout)
        
        # 2. Preferência de Tema
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Sistema", "Claro", "Escuro"])
        
        current_theme = config.get_theme_preference()
        idx = self.theme_combo.findText(current_theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
            
        form_layout.addRow("Tema Visual:", self.theme_combo)
        
        layout.addWidget(frame)
        
        # 3. Rodapé com Botões de Ação
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Salvar Configurações")
        save_btn.clicked.connect(self.save_settings)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)

    def browse_directory(self):
        """Abre seletor de diretório nativo."""
        dir_path = QFileDialog.getExistingDirectory(
            self, 
            "Selecionar Pasta de XMLs", 
            self.dir_input.text() or "."
        )
        if dir_path:
            self.dir_input.setText(dir_path)

    def save_settings(self):
        """Salva as configurações de fato e fecha o diálogo."""
        config.set_xml_directory(self.dir_input.text().strip())
        config.set_theme_preference(self.theme_combo.currentText())
        self.accept()
