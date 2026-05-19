from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QPushButton, QStatusBar, QMessageBox, QFileDialog, QFrame, 
    QProgressBar, QSplitter
)
from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QIcon
import os
import darkdetect

import config
from core.database import (
    init_db, search_documents, get_stats, 
    delete_xml_by_path, get_unique_emitentes, get_unique_destinatarios
)
from gui.styles import DARK_THEME, LIGHT_THEME
from gui.components.table_view import XMLTableView, XMLTableModel
from gui.components.filter_sidebar import FilterSidebar
from gui.components.xml_viewer import XMLViewer
from gui.components.settings_dialog import SettingsDialog
from gui.workers import XMLScanWorker

class MainWindow(QMainWindow):
    """
    Janela Principal do Gerenciador de XML Fiscal.
    Combina os painéis de Filtro, Listagem e Visualização em um layout elástico,
    gerencia processos em background e sincronização com o banco e disco.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XML Fiscal Manager")
        self.setMinimumSize(1200, 750)
        
        # Inicializa o banco de dados
        init_db()
        
        # Gerenciador de Processos em Background
        self.thread_pool = QThreadPool.globalInstance()
        self.is_scanning = False
        
        # Setup UI
        self.setup_ui()
        
        # Aplica o tema
        self.apply_theme()
        
        # Carrega dados iniciais do banco
        self.refresh_data()
        
        # Executa varredura inicial se houver pasta configurada
        self.run_initial_scan()

    def setup_ui(self):
        # Widget Central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)
        
        # 1. Barra de Ferramentas Superior
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)
        
        title_app = QLabel("XML Manager")
        title_app.setObjectName("appTitle")
        top_bar.addWidget(title_app)
        
        top_bar.addStretch()
        
        # Botões de Ação
        self.btn_select_dir = QPushButton("Selecionar Pasta")
        self.btn_select_dir.clicked.connect(self.select_directory)
        
        self.btn_sync = QPushButton("Sincronizar Pasta")
        self.btn_sync.setObjectName("secondaryButton")
        self.btn_sync.clicked.connect(self.run_folder_scan)
        
        self.btn_export = QPushButton("Exportar Excel")
        self.btn_export.setObjectName("secondaryButton")
        self.btn_export.clicked.connect(self.export_to_excel)
        
        self.btn_settings = QPushButton("Configurações")
        self.btn_settings.setObjectName("secondaryButton")
        self.btn_settings.clicked.connect(self.open_settings)
        
        top_bar.addWidget(self.btn_select_dir)
        top_bar.addWidget(self.btn_sync)
        top_bar.addWidget(self.btn_export)
        top_bar.addWidget(self.btn_settings)
        
        main_layout.addLayout(top_bar)
        
        # 2. Splitter Principal (Layout Elástico de 3 Painéis)
        splitter = QSplitter(Qt.Horizontal)
        
        # Painel Esquerdo: Filtros
        self.sidebar = FilterSidebar()
        self.sidebar.filters_changed.connect(self.on_filters_changed)
        splitter.addWidget(self.sidebar)
        
        # Painel Central: Tabela Virtualizada de Alta Performance
        table_container = QFrame()
        table_container.setObjectName("tableContainer")
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(10, 10, 10, 10)
        
        table_title = QLabel("Documentos Indexados")
        table_title.setObjectName("sectionTitle")
        table_layout.addWidget(table_title)
        
        self.table_view = XMLTableView()
        self.table_model = XMLTableModel()
        self.table_view.setModel(self.table_model)
        self.table_view.adjust_columns()
        
        # Evento de clique na tabela para carregar visualizador
        self.table_view.clicked.connect(self.on_table_row_selected)
        
        table_layout.addWidget(self.table_view)
        splitter.addWidget(table_container)
        
        # Painel Direito: Visualização/DANFE/Código
        self.viewer = XMLViewer()
        # Conecta sinal de exclusão
        self.viewer.delete_btn.clicked.connect(self.delete_selected_xml)
        
        splitter.addWidget(self.viewer)
        
        # Configura as proporções iniciais do Splitter (Filtros: 20%, Tabela: 50%, Visualizador: 30%)
        splitter.setSizes([260, 600, 340])
        main_layout.addWidget(splitter)
        
        # 3. Barra de Status com ProgressBar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        self.status_bar.showMessage("Pronto")

    def run_initial_scan(self):
        """Dispara varredura em background se houver uma pasta configurada."""
        xml_dir = config.get_xml_directory()
        if xml_dir and os.path.exists(xml_dir):
            self.run_folder_scan()
        else:
            self.status_bar.showMessage("Nenhuma pasta de XMLs configurada. Vá em 'Configurações' ou clique em 'Selecionar Pasta'.")

    def apply_theme(self):
        """Aplica estilos dinâmicos baseados nas preferências de tema (Claro/Escuro/Sistema)."""
        theme_pref = config.get_theme_preference()
        
        if theme_pref == "Sistema":
            is_dark = darkdetect.isDark()
            self.setStyleSheet(DARK_THEME if is_dark else LIGHT_THEME)
        elif theme_pref == "Escuro":
            self.setStyleSheet(DARK_THEME)
        else:
            self.setStyleSheet(LIGHT_THEME)

    def refresh_data(self):
        """Consulta banco de dados com filtros ativos e atualiza a tabela e estatísticas."""
        filters = self.sidebar.get_filters()
        docs = search_documents(filters)
        
        # Converte sqlite3.Row para lista de dicionários para compatibilidade
        dict_docs = [dict(row) for row in docs]
        self.table_model.set_documents(dict_docs)
        self.table_view.adjust_columns()
        
        # Atualiza Emitters e Recipients no Sidebar
        emitentes = get_unique_emitentes()
        destinatarios = get_unique_destinatarios()
        self.sidebar.update_combos(emitentes, destinatarios)
        
        # Atualiza Barra de Status com Estatísticas Gerais
        stats = get_stats()
        total_docs = stats.get("total_documentos", 0)
        total_val = stats.get("valor_total", 0.0)
        
        total_val_str = f"R$ {total_val:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
        self.status_bar.showMessage(f"Total: {total_docs} documentos indexados | Soma dos Valores: {total_val_str}")

    def on_filters_changed(self, filters: dict):
        """Disparado sempre que um filtro é ajustado no Sidebar."""
        self.refresh_data()
        self.viewer.clear()

    def on_table_row_selected(self, index):
        """Disparado ao selecionar um documento na listagem."""
        doc = self.table_model.get_document(index.row())
        if doc:
            self.viewer.load_document(doc)

    def select_directory(self):
        """Abre seletor rápido de pasta e inicia sincronização."""
        dir_path = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de XMLs")
        if dir_path:
            config.set_xml_directory(dir_path)
            self.run_folder_scan()

    def open_settings(self):
        """Abre a janela de diálogo de configurações."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Aplica novas configurações
            self.apply_theme()
            self.refresh_data()
            self.run_folder_scan()

    def run_folder_scan(self):
        """Inicia o escaneamento de arquivos XML em background sem travar a GUI."""
        xml_dir = config.get_xml_directory()
        if not xml_dir or not os.path.exists(xml_dir):
            QMessageBox.warning(
                self, 
                "Pasta não configurada", 
                "Por favor, configure uma pasta de arquivos XML válida nas configurações do sistema."
            )
            self.open_settings()
            return
            
        if self.is_scanning:
            return
            
        self.is_scanning = True
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Varrendo pasta de XMLs...")
        
        # Cria e executa worker em background
        worker = XMLScanWorker(xml_dir)
        worker.signals.progress.connect(self.on_scan_progress)
        worker.signals.finished.connect(self.on_scan_finished)
        worker.signals.error.connect(self.on_scan_error)
        
        self.thread_pool.start(worker)

    def on_scan_progress(self, current: int, total: int):
        """Atualiza a barra de progresso em tempo real."""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.status_bar.showMessage(f"Sincronizando pasta: {current} de {total} arquivos processados...")

    def on_scan_finished(self, results: tuple):
        """Finaliza o escaneamento em background, atualiza dados na tela."""
        inserted, removed, errors = results
        self.is_scanning = False
        self.progress_bar.setVisible(False)
        
        # Atualiza dados da listagem
        self.refresh_data()
        self.viewer.clear()
        
        msg = f"Sincronização concluída! Inseridos: {inserted} | Removidos: {removed}"
        if errors > 0:
            msg += f" | Erros: {errors}"
        self.status_bar.showMessage(msg)
        
        QMessageBox.information(
            self, 
            "Sincronização Concluída", 
            f"Processamento da pasta finalizado com sucesso!\n\n"
            f"• XMLs Adicionados/Atualizados: {inserted}\n"
            f"• XMLs Removidos do banco: {removed}\n"
            f"• Arquivos com erro: {errors}"
        )

    def on_scan_error(self, err_msg: str):
        """Tratamento de exceções ocorridas no thread worker."""
        self.is_scanning = False
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Erro ao varrer pasta de XMLs.")
        QMessageBox.critical(
            self,
            "Erro de Processamento",
            f"Ocorreu um erro ao escanear a pasta de arquivos XML:\n\n{err_msg}"
        )

    def delete_selected_xml(self):
        """
        Exclui fisicamente o arquivo XML com aviso duplo explícito (Conforme diretriz do usuário).
        """
        doc = self.viewer.current_doc
        if not doc:
            return
            
        filepath = doc.get("caminho_arquivo")
        chave = doc.get("chave_acesso")
        
        # Caixa de diálogo com aviso vermelho explícito
        reply = QMessageBox.warning(
            self,
            "ATENÇÃO: CONFIRMAÇÃO DE EXCLUSÃO",
            f"Você tem certeza absoluta que deseja excluir este arquivo físico do seu computador?\n\n"
            f"Arquivo: {os.path.basename(filepath)}\n"
            f"Caminho: {filepath}\n\n"
            f"IMPORTANTE: O arquivo será apagado do disco permanentemente. Esta ação NÃO pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 1. Exclui arquivo do disco
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                # 2. Exclui do SQLite
                delete_xml_by_path(filepath)
                
                # 3. Atualiza interface e limpa visualizador
                self.refresh_data()
                self.viewer.clear()
                
                self.status_bar.showMessage(f"Documento {chave} excluído permanentemente.")
                QMessageBox.information(self, "Sucesso", "O arquivo físico foi excluído com sucesso do disco.")
                
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Erro ao Excluir", 
                    f"Não foi possível excluir o arquivo do disco:\n\n{e}"
                )

    def export_to_excel(self):
        """Exporta as linhas ativas da listagem para planilha Excel usando reports/excel_exporter."""
        # Obtém registros atualmente filtrados
        filters = self.sidebar.get_filters()
        docs = search_documents(filters)
        dict_docs = [dict(row) for row in docs]
        
        if not dict_docs:
            QMessageBox.warning(self, "Exportação", "Não há registros disponíveis na listagem para exportar.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Salvar Relatório Excel", 
            "relatorio_xmls.xlsx", 
            "Planilha Excel (*.xlsx);;Arquivo CSV (*.csv)"
        )
        
        if file_path:
            from reports.excel_exporter import export_to_excel
            ok = export_to_excel(dict_docs, file_path)
            if ok:
                QMessageBox.information(
                    self, 
                    "Relatório Gerado", 
                    f"Planilha exportada com sucesso em:\n{file_path}"
                )
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível exportar a planilha.")
