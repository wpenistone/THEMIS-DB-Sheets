from __future__ import annotations

from typing import Dict

from PyQt6.QtWidgets import QApplication


def themes() -> Dict[str, str]:
    light = """
    QMainWindow { background: #f8f9fa; }
    QToolBar { background: #f1f3f5; spacing: 6px; border-bottom: 1px solid #dee2e6; }
    QStatusBar { background: #f1f3f5; }
    QDockWidget::title { background: #dee2e6; padding: 4px; }
    QDockWidget { titlebar-close-icon: url(none); titlebar-normal-icon: url(none); }
    QTreeWidget, QListWidget, QPlainTextEdit, QTextEdit, QTableWidget, QLineEdit { background: white; selection-background-color: #d0ebff; }
    QGroupBox { border: 1px solid #dee2e6; border-radius: 4px; margin-top: 10px; }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }
    QPushButton { background: #339af0; color: white; border: 0; padding: 6px 10px; border-radius: 4px; }
    QPushButton:hover { background: #228be6; }
    QPushButton:disabled { background: #ced4da; color: #495057; }
    QTabBar::tab { background: #e9ecef; border: 1px solid #dee2e6; padding: 6px 12px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
    QTabBar::tab:selected { background: white; }
    QHeaderView::section { background: #e9ecef; padding: 4px; border: 1px solid #dee2e6; }
    QMenu { background: white; border: 1px solid #dee2e6; }
    QMenu::item:selected { background: #d0ebff; }
    """
    dark = """
    QMainWindow { background: #212529; color: #ced4da; }
    QToolBar { background: #343a40; spacing: 6px; border-bottom: 1px solid #495057; }
    QStatusBar { background: #343a40; color: #ced4da; }
    QDockWidget::title { background: #343a40; padding: 4px; color: #ced4da; }
    QDockWidget { titlebar-close-icon: url(none); titlebar-normal-icon: url(none); color: #ced4da; }
    QTreeWidget, QListWidget, QPlainTextEdit, QTextEdit, QTableWidget, QLineEdit { background: #343a40; color: #f1f3f5; selection-background-color: #495057; }
    QGroupBox { border: 1px solid #495057; border-radius: 4px; margin-top: 10px; color: #f1f3f5; }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }
    QPushButton { background: #339af0; color: white; border: 0; padding: 6px 10px; border-radius: 4px; }
    QPushButton:hover { background: #228be6; }
    QPushButton:disabled { background: #495057; color: #adb5bd; }
    QTabBar::tab { background: #343a40; color: #e9ecef; border: 1px solid #495057; padding: 6px 12px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
    QTabBar::tab:selected { background: #495057; }
    QHeaderView::section { background: #343a40; color: #e9ecef; padding: 4px; border: 1px solid #495057; }
    QMenu { background: #343a40; border: 1px solid #495057; color: #e9ecef; }
    QMenu::item:selected { background: #495057; }
    QTableWidget { gridline-color: #495057; }
    QScrollBar:vertical { background: #343a40; width: 12px; }
    QScrollBar::handle:vertical { background: #495057; }
    QScrollBar:horizontal { background: #343a40; height: 12px; }
    QScrollBar::handle:horizontal { background: #495057; }
    """
    blue = """
    QMainWindow { background: #e7f5ff; }
    QToolBar { background: #d0ebff; spacing: 6px; border-bottom: 1px solid #74c0fc; }
    QStatusBar { background: #d0ebff; }
    QDockWidget::title { background: #a5d8ff; padding: 4px; }
    QTreeWidget, QListWidget, QPlainTextEdit, QTextEdit, QTableWidget, QLineEdit { background: white; }
    QGroupBox { border: 1px solid #a5d8ff; border-radius: 4px; margin-top: 10px; }
    QPushButton { background: #4dabf7; color: white; border: 0; padding: 6px 10px; border-radius: 4px; }
    QPushButton:hover { background: #339af0; }
    QTabBar::tab { background: #a5d8ff; border: 1px solid #74c0fc; padding: 6px 12px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
    QTabBar::tab:selected { background: white; }
    QHeaderView::section { background: #a5d8ff; padding: 4px; border: 1px solid #74c0fc; }
    """
    green = """
    QMainWindow { background: #ebfbee; }
    QToolBar { background: #d3f9d8; spacing: 6px; border-bottom: 1px solid #8ce99a; }
    QStatusBar { background: #d3f9d8; }
    QDockWidget::title { background: #b2f2bb; padding: 4px; }
    QTreeWidget, QListWidget, QPlainTextEdit, QTextEdit, QTableWidget, QLineEdit { background: white; }
    QGroupBox { border: 1px solid #b2f2bb; border-radius: 4px; margin-top: 10px; }
    QPushButton { background: #51cf66; color: white; border: 0; padding: 6px 10px; border-radius: 4px; }
    QPushButton:hover { background: #40c057; }
    QTabBar::tab { background: #b2f2bb; border: 1px solid #8ce99a; padding: 6px 12px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
    QTabBar::tab:selected { background: white; }
    QHeaderView::section { background: #b2f2bb; padding: 4px; border: 1px solid #8ce99a; }
    """
    return {"Light": light, "Dark": dark, "Blue": blue, "Green": green}


def apply_theme(app: QApplication, name: str) -> None:
    theme_map = themes()
    css = theme_map.get(name) or theme_map["Light"]
    app.setStyleSheet(css)
