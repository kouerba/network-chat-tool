DARK_STYLESHEET = """
QMainWindow {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

QLineEdit, QTextEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 5px;
    padding: 5px;
    font-size: 11pt;
}

QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #89b4fa;
    outline: none;
}

QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 5px;
    padding: 8px 15px;
    font-weight: bold;
    font-size: 11pt;
}

QPushButton:hover {
    background-color: #a6e3a1;
}

QPushButton:pressed {
    background-color: #74c7ec;
}

QListWidget, QListView {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 5px;
}

QListWidget::item, QListView::item {
    padding: 8px;
    border-radius: 3px;
}

QListWidget::item:selected, QListView::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}

QListWidget::item:hover, QListView::item:hover {
    background-color: #45475a;
}

QLabel {
    color: #cdd6f4;
}

QScrollBar:vertical {
    background-color: #313244;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}

QTabWidget::pane {
    border: 1px solid #45475a;
}

QTabBar::tab {
    background-color: #313244;
    color: #cdd6f4;
    padding: 5px 20px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}

QTabBar::tab:hover {
    background-color: #45475a;
}

QDialog {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

QMessageBox {
    background-color: #1e1e2e;
}

QMessageBox QLabel {
    color: #cdd6f4;
}

QMessageBox QPushButton {
    min-width: 60px;
}
"""
