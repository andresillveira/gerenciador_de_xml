from PySide6.QtCore import QRunnable, QObject, Signal
import traceback
from core.file_watcher import scan_directory

class XMLScanSignals(QObject):
    """
    Sinais emitidos pelo processo de indexação em background.
    """
    progress = Signal(int, int) # (atual, total)
    finished = Signal(tuple)    # (inseridos, removidos, erros)
    error = Signal(str)         # mensagem de erro

class XMLScanWorker(QRunnable):
    """
    Worker que executa a varredura e indexação de XMLs em segundo plano,
    evitando qualquer travamento da interface gráfica.
    """
    def __init__(self, directory_path: str):
        super().__init__()
        self.directory_path = directory_path
        self.signals = XMLScanSignals()
        
    def run(self):
        try:
            # Função de callback para relatar o progresso
            def progress_callback(current: int, total: int):
                self.signals.progress.emit(current, total)
                
            # Executa a varredura sincronizada com o banco
            inserted, removed, errors = scan_directory(self.directory_path, progress_callback)
            
            # Sinaliza a conclusão com os resultados
            self.signals.finished.emit((inserted, removed, errors))
            
        except Exception as e:
            traceback.print_exc()
            self.signals.error.emit(str(e))
