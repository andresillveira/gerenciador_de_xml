import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from gui.main_window import MainWindow

def main():
    # Em Qt6, o suporte High-DPI para múltiplos monitores já é nativo e ativado por padrão.
    # Apenas criamos e configuramos o loop principal do QApplication.
    app = QApplication(sys.argv)
    app.setApplicationName("Gerenciador de XML Fiscal")
    app.setApplicationDisplayName("Gerenciador de XML Fiscal")
    
    # Criamos a janela principal
    window = MainWindow()
    window.show()
    
    # Executa o loop principal
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
