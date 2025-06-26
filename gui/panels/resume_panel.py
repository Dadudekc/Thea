"""
Resume Panel for Thea GUI
Handles resume generation and management.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QComboBox, QGroupBox, QFormLayout, QLineEdit,
    QSpinBox, QCheckBox, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict

class ResumePanel(QWidget):
    """Panel for resume generation and management."""
    
    # Signals
    resume_generated = pyqtSignal(dict)
    resume_exported = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the resume UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        self.create_header(layout)
        
        # Main content
        self.create_main_content(layout)
        
        # Action buttons
        self.create_action_buttons(layout)
    
    def create_header(self, parent_layout):
        """Create the header section."""
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("📄 Resume Generator")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        parent_layout.addLayout(header_layout)
    
    def create_main_content(self, parent_layout):
        """Create the main content area."""
        content_layout = QHBoxLayout()
        
        # Left side - configuration
        self.create_config_section(content_layout)
        
        # Right side - preview
        self.create_preview_section(content_layout)
        
        parent_layout.addLayout(content_layout)
    
    def create_config_section(self, parent_layout):
        """Create the configuration section."""
        config_group = QGroupBox("Resume Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Personal info
        personal_group = QGroupBox("Personal Information")
        personal_layout = QFormLayout(personal_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Your full name")
        personal_layout.addRow("Name:", self.name_edit)
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("your.email@example.com")
        personal_layout.addRow("Email:", self.email_edit)
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+1 (555) 123-4567")
        personal_layout.addRow("Phone:", self.phone_edit)
        
        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("City, State")
        personal_layout.addRow("Location:", self.location_edit)
        
        config_layout.addWidget(personal_group)
        
        # Resume settings
        settings_group = QGroupBox("Resume Settings")
        settings_layout = QFormLayout(settings_group)
        
        self.template_combo = QComboBox()
        self.template_combo.addItems(["Professional", "Creative", "Minimal", "Modern"])
        self.template_combo.setCurrentText("Professional")
        settings_layout.addRow("Template:", self.template_combo)
        
        self.include_skills = QCheckBox("Include skills from conversations")
        self.include_skills.setChecked(True)
        settings_layout.addRow("Include skills:", self.include_skills)
        
        self.include_projects = QCheckBox("Include project summaries")
        self.include_projects.setChecked(True)
        settings_layout.addRow("Include projects:", self.include_projects)
        
        self.max_length = QSpinBox()
        self.max_length.setRange(1, 5)
        self.max_length.setValue(2)
        self.max_length.setSuffix(" pages")
        settings_layout.addRow("Max length:", self.max_length)
        
        config_layout.addWidget(settings_group)
        
        parent_layout.addWidget(config_group)
    
    def create_preview_section(self, parent_layout):
        """Create the preview section."""
        preview_group = QGroupBox("Resume Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        # Preview header
        preview_header = QHBoxLayout()
        preview_header.addWidget(QLabel("Generated Resume:"))
        preview_header.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.generate_resume)
        preview_header.addWidget(self.refresh_btn)
        
        preview_layout.addLayout(preview_header)
        
        # Preview content
        self.preview_edit = QTextEdit()
        self.preview_edit.setPlaceholderText("Click 'Generate Resume' to create a preview...")
        self.preview_edit.setReadOnly(True)
        preview_layout.addWidget(self.preview_edit)
        
        parent_layout.addWidget(preview_group)
    
    def create_action_buttons(self, parent_layout):
        """Create the action buttons."""
        button_layout = QHBoxLayout()
        
        button_layout.addStretch()
        
        self.generate_btn = QPushButton("📝 Generate Resume")
        self.generate_btn.clicked.connect(self.generate_resume)
        button_layout.addWidget(self.generate_btn)
        
        self.export_pdf_btn = QPushButton("📄 Export PDF")
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        self.export_pdf_btn.setEnabled(False)
        button_layout.addWidget(self.export_pdf_btn)
        
        self.export_md_btn = QPushButton("📝 Export Markdown")
        self.export_md_btn.clicked.connect(self.export_markdown)
        self.export_md_btn.setEnabled(False)
        button_layout.addWidget(self.export_md_btn)
        
        parent_layout.addLayout(button_layout)
    
    def generate_resume(self):
        """Generate the resume based on current configuration."""
        # Validate inputs
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Warning", "Please enter your name")
            return
        
        # Collect configuration
        config = {
            'name': self.name_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'phone': self.phone_edit.text().strip(),
            'location': self.location_edit.text().strip(),
            'template': self.template_combo.currentText(),
            'include_skills': self.include_skills.isChecked(),
            'include_projects': self.include_projects.isChecked(),
            'max_length': self.max_length.value()
        }
        
        # Generate resume content (placeholder)
        resume_content = self._generate_resume_content(config)
        
        # Update preview
        self.preview_edit.setPlainText(resume_content)
        
        # Enable export buttons
        self.export_pdf_btn.setEnabled(True)
        self.export_md_btn.setEnabled(True)
        
        # Emit signal
        self.resume_generated.emit(config)
        
        QMessageBox.information(self, "Success", "Resume generated successfully!")
    
    def _generate_resume_content(self, config: Dict) -> str:
        """Generate resume content based on configuration."""
        content = f"""# {config['name']}

## Contact Information
- Email: {config['email'] or 'your.email@example.com'}
- Phone: {config['phone'] or '+1 (555) 123-4567'}
- Location: {config['location'] or 'City, State'}

## Summary
Experienced developer with expertise in AI-powered development workflows and modern software engineering practices.

## Skills
- Python Development
- AI/ML Integration
- Web Development
- Database Management
- Version Control (Git)

## Experience
### AI Development Specialist
*2023 - Present*
- Developed AI-powered conversation management systems
- Implemented multi-model testing frameworks
- Created automated workflow optimization tools

### Software Engineer
*2021 - 2023*
- Built scalable web applications
- Collaborated with cross-functional teams
- Mentored junior developers

## Education
### Bachelor of Science in Computer Science
*University Name, 2021*

## Projects
### Dreamscape MMORPG Platform
- AI-powered development environment
- Multi-model testing and optimization
- Automated conversation management

### ChatGPT Integration System
- Automated conversation extraction
- Template-based prompt management
- Advanced content indexing

---
*Generated using Thea - Dreamscape MMORPG Platform*
"""
        return content
    
    def export_pdf(self):
        """Export resume as PDF."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Resume PDF", 
            f"{self.name_edit.text()}_resume.pdf", 
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            # This would actually generate a PDF
            QMessageBox.information(self, "Success", "Resume exported as PDF!")
            self.resume_exported.emit(file_path)
    
    def export_markdown(self):
        """Export resume as Markdown."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Resume Markdown", 
            f"{self.name_edit.text()}_resume.md", 
            "Markdown Files (*.md)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.preview_edit.toPlainText())
                
                QMessageBox.information(self, "Success", "Resume exported as Markdown!")
                self.resume_exported.emit(file_path)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {e}")
    
    def load_personal_info(self, info: Dict):
        """Load personal information into the form."""
        self.name_edit.setText(info.get('name', ''))
        self.email_edit.setText(info.get('email', ''))
        self.phone_edit.setText(info.get('phone', ''))
        self.location_edit.setText(info.get('location', ''))
    
    def get_configuration(self) -> Dict:
        """Get current configuration."""
        return {
            'name': self.name_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'phone': self.phone_edit.text().strip(),
            'location': self.location_edit.text().strip(),
            'template': self.template_combo.currentText(),
            'include_skills': self.include_skills.isChecked(),
            'include_projects': self.include_projects.isChecked(),
            'max_length': self.max_length.value()
        } 