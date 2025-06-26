"""
Multi-Model Testing Panel for Thea GUI
Handles multi-model prompt testing and comparison.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QComboBox, QProgressBar, QGroupBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont
from typing import List, Dict

class MultiModelPanel(QWidget):
    """Panel for multi-model prompt testing."""
    
    # Signals
    test_started = pyqtSignal()
    test_completed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.test_results = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the multi-model UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        self.create_header(layout)
        
        # Main content
        self.create_main_content(layout)
        
        # Results section
        self.create_results_section(layout)
    
    def create_header(self, parent_layout):
        """Create the header section."""
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("🧠 Multi-Model Testing")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Action buttons
        self.start_btn = QPushButton("▶️ Start Test")
        self.start_btn.clicked.connect(self.start_test)
        header_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.clicked.connect(self.stop_test)
        self.stop_btn.setEnabled(False)
        header_layout.addWidget(self.stop_btn)
        
        parent_layout.addLayout(header_layout)
    
    def create_main_content(self, parent_layout):
        """Create the main content area."""
        content_layout = QHBoxLayout()
        
        # Left side - input
        self.create_input_section(content_layout)
        
        # Right side - configuration
        self.create_config_section(content_layout)
        
        parent_layout.addLayout(content_layout)
    
    def create_input_section(self, parent_layout):
        """Create the input section."""
        input_group = QGroupBox("Test Input")
        input_layout = QVBoxLayout(input_group)
        
        # Prompt input
        prompt_label = QLabel("Prompt:")
        input_layout.addWidget(prompt_label)
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter your test prompt here...")
        self.prompt_edit.setMaximumHeight(150)
        input_layout.addWidget(self.prompt_edit)
        
        # Template selection
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("Template:"))
        
        self.template_combo = QComboBox()
        self.template_combo.addItem("No Template")
        template_layout.addWidget(self.template_combo)
        
        input_layout.addLayout(template_layout)
        
        parent_layout.addWidget(input_group)
    
    def create_config_section(self, parent_layout):
        """Create the configuration section."""
        config_group = QGroupBox("Test Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Models:"))
        
        self.models_combo = QComboBox()
        self.models_combo.addItems(["gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"])
        self.models_combo.setCurrentText("gpt-4o")
        model_layout.addWidget(self.models_combo)
        
        config_layout.addLayout(model_layout)
        
        # Test parameters
        params_layout = QHBoxLayout()
        params_layout.addWidget(QLabel("Temperature:"))
        
        self.temp_combo = QComboBox()
        self.temp_combo.addItems(["0.1", "0.3", "0.5", "0.7", "1.0"])
        self.temp_combo.setCurrentText("0.7")
        params_layout.addWidget(self.temp_combo)
        
        config_layout.addLayout(params_layout)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        config_layout.addWidget(self.progress_bar)
        
        # Status
        self.status_label = QLabel("Ready to test")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        config_layout.addWidget(self.status_label)
        
        parent_layout.addWidget(config_group)
    
    def create_results_section(self, parent_layout):
        """Create the results section."""
        results_group = QGroupBox("Test Results")
        results_layout = QVBoxLayout(results_group)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels([
            "Model", "Response", "Time", "Status"
        ])
        
        # Configure table
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.results_table.setAlternatingRowColors(True)
        results_layout.addWidget(self.results_table)
        
        parent_layout.addWidget(results_group)
    
    def start_test(self):
        """Start the multi-model test."""
        prompt = self.prompt_edit.toPlainText().strip()
        if not prompt:
            self.status_label.setText("Please enter a prompt")
            return
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Running test...")
        
        # Clear previous results
        self.results_table.setRowCount(0)
        
        # Emit signal
        self.test_started.emit()
        
        # Simulate test (replace with actual implementation)
        self.simulate_test()
    
    def stop_test(self):
        """Stop the current test."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Test stopped")
    
    def simulate_test(self):
        """Simulate a test run (placeholder)."""
        import time
        
        models = ["gpt-4o", "gpt-4o-mini"]
        self.progress_bar.setMaximum(len(models))
        
        for i, model in enumerate(models):
            # Simulate API call
            time.sleep(1)
            
            # Add result
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            self.results_table.setItem(row, 0, QTableWidgetItem(model))
            self.results_table.setItem(row, 1, QTableWidgetItem(f"Simulated response from {model}"))
            self.results_table.setItem(row, 2, QTableWidgetItem("1.2s"))
            self.results_table.setItem(row, 3, QTableWidgetItem("✅ Success"))
            
            self.progress_bar.setValue(i + 1)
        
        # Test completed
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Test completed")
        
        # Emit completion signal
        self.test_completed.emit({"models_tested": len(models)})
    
    def add_test_result(self, result: Dict):
        """Add a test result to the table."""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        self.results_table.setItem(row, 0, QTableWidgetItem(result.get('model', 'Unknown')))
        self.results_table.setItem(row, 1, QTableWidgetItem(result.get('response', 'No response')))
        self.results_table.setItem(row, 2, QTableWidgetItem(result.get('time', '0s')))
        self.results_table.setItem(row, 3, QTableWidgetItem(result.get('status', 'Unknown')))
    
    def get_test_config(self) -> Dict:
        """Get the current test configuration."""
        return {
            'prompt': self.prompt_edit.toPlainText(),
            'model': self.models_combo.currentText(),
            'temperature': float(self.temp_combo.currentText()),
            'template': self.template_combo.currentText()
        } 