"""
Templates Panel for Thea GUI
Manages prompt templates and template operations.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QTextEdit, QLineEdit,
    QSplitter, QMessageBox, QInputDialog, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Dict
import os

class TemplatesPanel(QWidget):
    """Panel for managing prompt templates."""
    
    # Signals
    template_selected = pyqtSignal(dict)
    template_saved = pyqtSignal(dict)
    template_deleted = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.templates = []
        self.current_template = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the templates UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        self.create_header(layout)
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - template list
        self.create_template_list(splitter)
        
        # Right side - template editor
        self.create_template_editor(splitter)
        
        # Set splitter proportions
        splitter.setSizes([300, 700])
    
    def create_header(self, parent_layout):
        """Create the header section."""
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("📝 Templates")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Action buttons
        self.new_btn = QPushButton("➕ New Template")
        self.new_btn.clicked.connect(self.create_new_template)
        header_layout.addWidget(self.new_btn)
        
        self.import_btn = QPushButton("📥 Import")
        self.import_btn.clicked.connect(self.import_template)
        header_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self.export_template)
        header_layout.addWidget(self.export_btn)
        
        parent_layout.addLayout(header_layout)
    
    def create_template_list(self, parent):
        """Create the template list."""
        # Container widget
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search templates...")
        self.search_box.textChanged.connect(self.filter_templates)
        list_layout.addWidget(self.search_box)
        
        # Template list
        self.template_list = QListWidget()
        self.template_list.itemSelectionChanged.connect(self.on_template_selected)
        list_layout.addWidget(self.template_list)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self.delete_template)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)
        
        self.duplicate_btn = QPushButton("📋 Duplicate")
        self.duplicate_btn.clicked.connect(self.duplicate_template)
        self.duplicate_btn.setEnabled(False)
        button_layout.addWidget(self.duplicate_btn)
        
        list_layout.addLayout(button_layout)
        
        parent.addWidget(list_widget)
    
    def create_template_editor(self, parent):
        """Create the template editor."""
        # Container widget
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        
        # Editor header
        editor_header = QHBoxLayout()
        
        self.editor_title = QLabel("Select a template to edit")
        self.editor_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        editor_header.addWidget(self.editor_title)
        
        editor_header.addStretch()
        
        # Save button
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self.save_template)
        self.save_btn.setEnabled(False)
        editor_header.addWidget(self.save_btn)
        
        editor_layout.addLayout(editor_header)
        
        # Template name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Template name...")
        self.name_edit.textChanged.connect(self.on_template_modified)
        name_layout.addWidget(self.name_edit)
        
        editor_layout.addLayout(name_layout)
        
        # Template content
        content_label = QLabel("Content:")
        editor_layout.addWidget(content_label)
        
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Enter template content here...")
        self.content_edit.textChanged.connect(self.on_template_modified)
        editor_layout.addWidget(self.content_edit)
        
        parent.addWidget(editor_widget)
    
    def load_templates(self, templates: List[Dict]):
        """Load templates into the list."""
        self.templates = templates
        self.template_list.clear()
        
        for template in templates:
            item = QListWidgetItem(template.get('name', 'Untitled'))
            item.setData(Qt.ItemDataRole.UserRole, template)
            self.template_list.addItem(item)
    
    def on_template_selected(self):
        """Handle template selection."""
        current_item = self.template_list.currentItem()
        if current_item:
            template = current_item.data(Qt.ItemDataRole.UserRole)
            self.edit_template(template)
        else:
            self.clear_editor()
    
    def edit_template(self, template: Dict):
        """Edit a template in the editor."""
        self.current_template = template
        
        # Update editor
        self.name_edit.setText(template.get('name', ''))
        self.content_edit.setPlainText(template.get('content', ''))
        
        # Update title
        self.editor_title.setText(f"Editing: {template.get('name', 'Untitled')}")
        
        # Enable buttons
        self.save_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.duplicate_btn.setEnabled(True)
        
        # Emit signal
        self.template_selected.emit(template)
    
    def clear_editor(self):
        """Clear the template editor."""
        self.current_template = None
        self.name_edit.clear()
        self.content_edit.clear()
        self.editor_title.setText("Select a template to edit")
        
        # Disable buttons
        self.save_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.duplicate_btn.setEnabled(False)
    
    def create_new_template(self):
        """Create a new template."""
        name, ok = QInputDialog.getText(self, "New Template", "Template name:")
        if ok and name:
            new_template = {
                'name': name,
                'content': '',
                'created_at': self._get_current_timestamp()
            }
            
            # Add to list
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, new_template)
            self.template_list.addItem(item)
            
            # Select the new template
            self.template_list.setCurrentItem(item)
    
    def save_template(self):
        """Save the current template."""
        if not self.current_template:
            return
        
        # Update template data
        self.current_template['name'] = self.name_edit.text()
        self.current_template['content'] = self.content_edit.toPlainText()
        self.current_template['updated_at'] = self._get_current_timestamp()
        
        # Update list item
        current_item = self.template_list.currentItem()
        if current_item:
            current_item.setText(self.current_template['name'])
            current_item.setData(Qt.ItemDataRole.UserRole, self.current_template)
        
        # Emit signal
        self.template_saved.emit(self.current_template)
        
        QMessageBox.information(self, "Success", "Template saved successfully!")
    
    def delete_template(self):
        """Delete the current template."""
        if not self.current_template:
            return
        
        reply = QMessageBox.question(
            self, "Delete Template", 
            f"Are you sure you want to delete '{self.current_template['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from list
            current_row = self.template_list.currentRow()
            if current_row >= 0:
                self.template_list.takeItem(current_row)
            
            # Emit signal
            self.template_deleted.emit(self.current_template.get('name', ''))
            
            # Clear editor
            self.clear_editor()
    
    def duplicate_template(self):
        """Duplicate the current template."""
        if not self.current_template:
            return
        
        name, ok = QInputDialog.getText(
            self, "Duplicate Template", 
            "New template name:", 
            text=f"{self.current_template['name']} (Copy)"
        )
        
        if ok and name:
            # Create duplicate
            duplicate = self.current_template.copy()
            duplicate['name'] = name
            duplicate['created_at'] = self._get_current_timestamp()
            
            # Add to list
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, duplicate)
            self.template_list.addItem(item)
            
            # Select the duplicate
            self.template_list.setCurrentItem(item)
    
    def import_template(self):
        """Import a template from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Template", "", "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract name from filename
                name = os.path.splitext(os.path.basename(file_path))[0]
                
                new_template = {
                    'name': name,
                    'content': content,
                    'created_at': self._get_current_timestamp()
                }
                
                # Add to list
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, new_template)
                self.template_list.addItem(item)
                
                QMessageBox.information(self, "Success", "Template imported successfully!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import template: {e}")
    
    def export_template(self):
        """Export the current template to file."""
        if not self.current_template:
            QMessageBox.warning(self, "Warning", "No template selected")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Template", 
            f"{self.current_template['name']}.txt", 
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.current_template['content'])
                
                QMessageBox.information(self, "Success", "Template exported successfully!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export template: {e}")
    
    def filter_templates(self, text: str):
        """Filter templates based on search text."""
        for i in range(self.template_list.count()):
            item = self.template_list.item(i)
            template = item.data(Qt.ItemDataRole.UserRole)
            name = template.get('name', '').lower()
            should_show = not text or text.lower() in name
            item.setHidden(not should_show)
    
    def on_template_modified(self):
        """Handle template modification."""
        if self.current_template:
            self.save_btn.setEnabled(True)
    
    def _get_current_timestamp(self):
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_current_template(self) -> Dict:
        """Get the currently selected template."""
        return self.current_template or {} 