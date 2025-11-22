from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QDockWidget,
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QWidget,
    QApplication,
)

from .actions import ActionFactory
from .designer.canvas import CanvasView
from .io.generator import generate_config
from .io.serialization import export_config_js, export_config_json
from .io.templates import default_config, default_fields, default_org
from .io.validators import validate_config
from .org.editor import OrgTreeEditor
from .preview import PreviewDialog
from .resources import icon_layout, icon_tree, icon_validate
from .settings import Settings
from .theme import apply_theme, themes
from .widgets.console import ConsoleWidget
from .widgets.hierarchy import HierarchyWidget
from .widgets.inspector import InspectorWidget
from .widgets.palette import PaletteWidget
from .widgets.ranks import RanksEditor
from .widgets.custom_fields import CustomFieldsEditor
from .widgets.events import EventTypesEditor


class MainWindow(QMainWindow):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.settings = Settings()
        self.setWindowTitle("THEMIS Configuration Studio")
        self.resize(1280, 800)
        if (geo := self.settings.window_geometry()) is not None:
            self.restoreGeometry(geo)
        if (state := self.settings.window_state()) is not None:
            self.restoreState(state)

        self.actions = ActionFactory(self)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.canvas = CanvasView()
        self.org_editor = OrgTreeEditor()
        self.ranks_editor = RanksEditor()
        self.custom_fields_editor = CustomFieldsEditor()
        self.events_editor = EventTypesEditor()
        self.console = ConsoleWidget()

        self.tabs.addTab(self.canvas, icon_layout(), "Layout Designer")
        self.tabs.addTab(self.org_editor, icon_tree(), "Organization Editor")
        self.tabs.addTab(self.ranks_editor, icon_validate(), "Ranks")
        self.tabs.addTab(self.custom_fields_editor, icon_validate(), "Custom Fields")
        self.tabs.addTab(self.events_editor, icon_validate(), "Event Types")

        self._create_docks()
        self._create_menus()
        self._create_toolbar()

        inst = QApplication.instance()
        if inst is not None:
            apply_theme(inst, str(self.settings.get("theme", "Light")))

        self._path: Optional[str] = None

        self._load_default()

    def _create_docks(self) -> None:
        dock_palette = QDockWidget("Palette", self)
        dock_palette.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.palette = PaletteWidget()
        self.palette.fieldDropped.connect(self._on_palette_field_dropped)
        dock_palette.setWidget(self.palette)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock_palette)

        dock_inspector = QDockWidget("Inspector", self)
        dock_inspector.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.inspector = InspectorWidget(self.canvas)
        dock_inspector.setWidget(self.inspector)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock_inspector)

        dock_hierarchy = QDockWidget("Hierarchy", self)
        dock_hierarchy.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.hierarchy = HierarchyWidget(self.canvas)
        dock_hierarchy.setWidget(self.hierarchy)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock_hierarchy)

        dock_console = QDockWidget("Validation", self)
        dock_console.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea)
        dock_console.setWidget(self.console)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock_console)

    def _create_menus(self) -> None:
        m_file = self.menuBar().addMenu("File")
        m_file.addAction(self.actions.file_open(self._file_open))
        m_file.addAction(self.actions.file_save(self._file_save))
        m_file.addAction(self.actions.file_save_as(self._file_save_as))

        m_edit = self.menuBar().addMenu("Edit")
        m_edit.addAction(self.actions.edit_undo(self._edit_undo))
        m_edit.addAction(self.actions.edit_redo(self._edit_redo))

        m_tools = self.menuBar().addMenu("Tools")
        a_preview = self.actions.preview(self._preview)
        m_tools.addAction(a_preview)
        a_arrange = self.actions.action("Smart Arrange", None, None, "Auto-arrange selected items", lambda: self._smart_arrange("grid"))
        m_tools.addAction(a_arrange)
        menu_theme = m_tools.addMenu("Theme")
        for name in themes().keys():
            menu_theme.addAction(self.actions.action(name, None, None, f"Switch to {name}", lambda n=name: self._apply_theme(n)))
        a_validate = self.actions.run_validate(self._run_validation)
        a_validate.setIcon(icon_validate())
        m_tools.addAction(a_validate)

    def _create_toolbar(self) -> None:
        tb = self.addToolBar("Main")
        tb.addAction(self.actions.file_open(self._file_open))
        tb.addAction(self.actions.file_save(self._file_save))
        tb.addSeparator()
        tb.addAction(self.actions.edit_undo(self._edit_undo))
        tb.addAction(self.actions.edit_redo(self._edit_redo))
        tb.addSeparator()
        tb.addAction(self.actions.preview(self._preview))
        tb.addAction(self.actions.zoom_in(self._zoom_in))
        tb.addAction(self.actions.zoom_out(self._zoom_out))
        tb.addSeparator()
        act_validate = self.actions.run_validate(self._run_validation)
        act_validate.setIcon(icon_validate())
        tb.addAction(act_validate)

    def _on_palette_field_dropped(self, key: str, label: str) -> None:
        r = len([x for x in self.canvas.scene().items() if hasattr(x, "key")])
        self.canvas.add_field(key, label, r, 0)
        self.hierarchy.refresh()
        self.inspector._on_selection()

    def _config_dict(self) -> Dict[str, Any]:
        fields = self.canvas.export_fields()
        ranks = self.ranks_editor.ranks()
        custom_fields: List[Dict[str, Any]] = self.custom_fields_editor.fields()
        events = self.events_editor.event_types()
        rules = default_config().get("VALIDATION_RULES", {})
        org = self.org_editor.to_dict()
        return generate_config(org, fields, ranks, custom_fields, events, rules)

    def _file_open(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open Configuration", self.settings.last_opened_path() or os.getcwd(), "Config Files (*.json *.js)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            if path.endswith(".json"):
                data = json.loads(text)
            else:
                if text.startswith("const THEMIS_CONFIG = "):
                    text = text[len("const THEMIS_CONFIG = ") :]
                if text.endswith(";"):
                    text = text[:-1]
                data = json.loads(text)
            orgs = data.get("ORGANIZATION_HIERARCHY", [default_org()])
            self.org_editor.set_root(self.org_editor.root().from_dict(orgs[0]))
            offsets = data.get("LAYOUT_BLUEPRINTS", {}).get("BILLET_OFFSETS", {}).get("offsets", {})
            fields = []
            for k, v in offsets.items():
                fields.append({"key": k, "label": k, "row": int(v.get("row", 0)), "col": int(v.get("col", 0))})
            self.canvas.load_fields(fields)
            self.ranks_editor.set_ranks(data.get("RANK_HIERARCHY", default_config().get("RANK_HIERARCHY", [])))
            self.custom_fields_editor.set_fields(data.get("CUSTOM_FIELDS", []))
            self.events_editor.set_event_types(data.get("EVENT_TYPE_DEFINITIONS", default_config().get("EVENT_TYPE_DEFINITIONS", [])))
            self._path = path
            self.settings.set_last_opened_path(os.path.dirname(path))
        except Exception as e:
            QMessageBox.critical(self, "Open Failed", f"Failed to open file:\n{e}")

    def _file_save(self) -> None:
        if self._path is None:
            self._file_save_as()
            return
        self._save_to_path(self._path)

    def _file_save_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Configuration", self.settings.last_opened_path() or os.getcwd(), "JSON (*.json);;JavaScript (*.js)")
        if not path:
            return
        self._save_to_path(path)
        self._path = path
        self.settings.set_last_opened_path(os.path.dirname(path))

    def _save_to_path(self, path: str) -> None:
        data = self._config_dict()
        try:
            with open(path, "w", encoding="utf-8") as f:
                if path.endswith(".json"):
                    f.write(export_config_json(data))
                else:
                    f.write(export_config_js(data))
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Failed to save file:\n{e}")

    def _edit_undo(self) -> None:
        self.canvas.command_stack().undo()

    def _edit_redo(self) -> None:
        self.canvas.command_stack().redo()

    def _run_validation(self) -> None:
        config = self._config_dict()
        issues = validate_config(config)
        self.console.show_issues(issues)
        if not issues:
            QMessageBox.information(self, "Validation", "No issues found.")

    def _smart_arrange(self, strategy: str = "grid") -> None:
        self.canvas.smart_arrange_selected(strategy)

    def _preview(self) -> None:
        dlg = PreviewDialog(self)
        dlg.set_fields(self.canvas.export_fields())
        dlg.exec()

    def _zoom_in(self) -> None:
        self.canvas.zoom_in()

    def _zoom_out(self) -> None:
        self.canvas.zoom_out()

    def _apply_theme(self, name: str) -> None:
        inst = QApplication.instance()
        if inst is not None:
            apply_theme(inst, name)
            self.settings.set("theme", name)

    def _load_default(self) -> None:
        self.canvas.add_fields_from_list(default_fields())
        self.org_editor.set_root(self.org_editor.root().from_dict(default_org()))
        self.ranks_editor.set_ranks(default_config().get("RANK_HIERARCHY", []))
        self.custom_fields_editor.set_fields([])
        self.events_editor.set_event_types(default_config().get("EVENT_TYPE_DEFINITIONS", []))

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.settings.set_window_geometry(self.saveGeometry())
        self.settings.set_window_state(self.saveState())
        super().closeEvent(event)
