# Configurações de estilo QSS (Qt Style Sheets) para os temas Claro e Escuro.
# Proporciona um visual moderno, "Clean" e premium, semelhante a interfaces modernas (Glassmorphism sutil, cantos arredondados).

DARK_THEME = """
/* Tema Escuro Premium */
QMainWindow {
    background-color: #0f0f11;
}

QWidget {
    color: #e2e8f0;
    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
    font-size: 13px;
}

/* Painéis e Cards */
QFrame#sidebarFrame, QFrame#detailFrame {
    background-color: #16161a;
    border-radius: 12px;
    border: 1px solid #232329;
}

QFrame#tableContainer {
    background-color: #16161a;
    border-radius: 12px;
    border: 1px solid #232329;
}

/* Títulos */
QLabel#sectionTitle {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 8px;
}

QLabel#appTitle {
    font-size: 20px;
    font-weight: bold;
    color: #6366f1; /* Indigo */
    margin-bottom: 12px;
}

/* Inputs de Texto e Combos */
QLineEdit, QComboBox, QDateEdit {
    background-color: #1e1e24;
    border: 1px solid #31313c;
    border-radius: 8px;
    padding: 6px 12px;
    color: #f1f5f9;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 1px solid #6366f1;
    background-color: #24242d;
}

QComboBox::drop-down {
    border: 0px;
}

/* Botões */
QPushButton {
    background-color: #6366f1;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #4f46e5;
}

QPushButton:pressed {
    background-color: #3730a3;
}

QPushButton:disabled {
    background-color: #31313c;
    color: #64748b;
}

/* Botão Secundário */
QPushButton#secondaryButton {
    background-color: #232329;
    color: #e2e8f0;
    border: 1px solid #31313c;
}

QPushButton#secondaryButton:hover {
    background-color: #2d2d35;
    border-color: #475569;
}

QPushButton#dangerButton {
    background-color: #ef4444;
    color: white;
}

QPushButton#dangerButton:hover {
    background-color: #dc2626;
}

/* Tabela de Alta Performance */
QTableView {
    background-color: #16161a;
    border: none;
    gridline-color: #232329;
    selection-background-color: #2d2d39;
    selection-color: #ffffff;
    border-radius: 12px;
}

QTableView::item {
    padding: 10px;
    border-bottom: 1px solid #232329;
}

QTableView::item:selected {
    background-color: rgba(99, 102, 241, 0.2);
    color: #ffffff;
    border-left: 3px solid #6366f1;
}

QHeaderView::section {
    background-color: #1e1e24;
    color: #94a3b8;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #232329;
    font-weight: bold;
}

/* Barra de Rolagem Moderna */
QScrollBar:vertical {
    border: none;
    background: #16161a;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #31313c;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #4b4b5c;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #16161a;
    height: 8px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #31313c;
    min-width: 20px;
    border-radius: 4px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Abas (Tab Widget) */
QTabWidget::pane {
    border: 1px solid #232329;
    border-radius: 8px;
    background: #1e1e24;
}

QTabBar::tab {
    background: #16161a;
    border: 1px solid #232329;
    padding: 6px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    color: #94a3b8;
}

QTabBar::tab:selected {
    background: #1e1e24;
    border-bottom-color: #1e1e24;
    color: #ffffff;
    font-weight: bold;
}
"""

LIGHT_THEME = """
/* Tema Claro Moderno e Clean */
QMainWindow {
    background-color: #f8fafc;
}

QWidget {
    color: #334155;
    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
    font-size: 13px;
}

/* Painéis e Cards */
QFrame#sidebarFrame, QFrame#detailFrame {
    background-color: #ffffff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

QFrame#tableContainer {
    background-color: #ffffff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

/* Títulos */
QLabel#sectionTitle {
    font-size: 16px;
    font-weight: bold;
    color: #0f172a;
    margin-bottom: 8px;
}

QLabel#appTitle {
    font-size: 20px;
    font-weight: bold;
    color: #4f46e5;
    margin-bottom: 12px;
}

/* Inputs de Texto e Combos */
QLineEdit, QComboBox, QDateEdit {
    background-color: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 6px 12px;
    color: #1e293b;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 1px solid #4f46e5;
    background-color: #ffffff;
}

QComboBox::drop-down {
    border: 0px;
}

/* Botões */
QPushButton {
    background-color: #4f46e5;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #4338ca;
}

QPushButton:pressed {
    background-color: #3730a3;
}

QPushButton:disabled {
    background-color: #cbd5e1;
    color: #94a3b8;
}

/* Botão Secundário */
QPushButton#secondaryButton {
    background-color: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
}

QPushButton#secondaryButton:hover {
    background-color: #f8fafc;
    border-color: #94a3b8;
}

QPushButton#dangerButton {
    background-color: #ef4444;
    color: white;
}

QPushButton#dangerButton:hover {
    background-color: #dc2626;
}

/* Tabela de Alta Performance */
QTableView {
    background-color: #ffffff;
    border: none;
    gridline-color: #f1f5f9;
    selection-background-color: #f1f5f9;
    selection-color: #0f172a;
    border-radius: 12px;
}

QTableView::item {
    padding: 10px;
    border-bottom: 1px solid #f1f5f9;
}

QTableView::item:selected {
    background-color: rgba(79, 70, 229, 0.1);
    color: #4f46e5;
    border-left: 3px solid #4f46e5;
    font-weight: 500;
}

QHeaderView::section {
    background-color: #f8fafc;
    color: #64748b;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #e2e8f0;
    font-weight: bold;
}

/* Barra de Rolagem Moderna */
QScrollBar:vertical {
    border: none;
    background: #f8fafc;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Abas (Tab Widget) */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    background: #ffffff;
}

QTabBar::tab {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 6px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    color: #64748b;
}

QTabBar::tab:selected {
    background: #ffffff;
    border-bottom-color: #ffffff;
    color: #4f46e5;
    font-weight: bold;
}
"""
