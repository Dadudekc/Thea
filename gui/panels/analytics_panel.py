"""
Analytics Panel for Thea GUI
Displays analytics and statistics about conversations and usage.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout,
    QProgressBar, QComboBox, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Dict

class AnalyticsPanel(QWidget):
    """Panel for displaying analytics and statistics."""
    
    # Signals
    refresh_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the analytics UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        self.create_header(layout)
        
        # Main content
        self.create_main_content(layout)
        
        # Detailed analytics
        self.create_detailed_analytics(layout)
    
    def create_header(self, parent_layout):
        """Create the header section."""
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("📊 Analytics")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Time period selector
        header_layout.addWidget(QLabel("Time Period:"))
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Last 7 days", "Last 30 days", "Last 90 days", "All time"])
        self.period_combo.setCurrentText("Last 30 days")
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        header_layout.addWidget(self.period_combo)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(self.refresh_btn)
        
        parent_layout.addLayout(header_layout)
    
    def create_main_content(self, parent_layout):
        """Create the main content area."""
        content_layout = QHBoxLayout()
        
        # Overview stats
        self.create_overview_stats(content_layout)
        
        # Usage trends
        self.create_usage_trends(content_layout)
        
        parent_layout.addLayout(content_layout)
    
    def create_overview_stats(self, parent_layout):
        """Create the overview statistics section."""
        overview_group = QGroupBox("Overview Statistics")
        overview_layout = QGridLayout(overview_group)
        
        # Total conversations
        self.total_conversations_label = QLabel("0")
        self.total_conversations_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.total_conversations_label.setStyleSheet("color: #0078d4;")
        overview_layout.addWidget(QLabel("Total Conversations:"), 0, 0)
        overview_layout.addWidget(self.total_conversations_label, 0, 1)
        
        # Total messages
        self.total_messages_label = QLabel("0")
        self.total_messages_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.total_messages_label.setStyleSheet("color: #107c10;")
        overview_layout.addWidget(QLabel("Total Messages:"), 1, 0)
        overview_layout.addWidget(self.total_messages_label, 1, 1)
        
        # Total words
        self.total_words_label = QLabel("0")
        self.total_words_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.total_words_label.setStyleSheet("color: #d83b01;")
        overview_layout.addWidget(QLabel("Total Words:"), 2, 0)
        overview_layout.addWidget(self.total_words_label, 2, 1)
        
        # Average conversation length
        self.avg_length_label = QLabel("0")
        self.avg_length_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.avg_length_label.setStyleSheet("color: #8661c5;")
        overview_layout.addWidget(QLabel("Avg. Messages/Conversation:"), 3, 0)
        overview_layout.addWidget(self.avg_length_label, 3, 1)
        
        parent_layout.addWidget(overview_group)
    
    def create_usage_trends(self, parent_layout):
        """Create the usage trends section."""
        trends_group = QGroupBox("Usage Trends")
        trends_layout = QVBoxLayout(trends_group)
        
        # Daily activity
        daily_label = QLabel("Daily Activity")
        daily_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        trends_layout.addWidget(daily_label)
        
        self.daily_progress = QProgressBar()
        self.daily_progress.setRange(0, 100)
        self.daily_progress.setValue(0)
        self.daily_progress.setFormat("Today: %v conversations")
        trends_layout.addWidget(self.daily_progress)
        
        # Weekly activity
        weekly_label = QLabel("Weekly Activity")
        weekly_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        trends_layout.addWidget(weekly_label)
        
        self.weekly_progress = QProgressBar()
        self.weekly_progress.setRange(0, 100)
        self.weekly_progress.setValue(0)
        self.weekly_progress.setFormat("This week: %v conversations")
        trends_layout.addWidget(self.weekly_progress)
        
        # Monthly activity
        monthly_label = QLabel("Monthly Activity")
        monthly_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        trends_layout.addWidget(monthly_label)
        
        self.monthly_progress = QProgressBar()
        self.monthly_progress.setRange(0, 100)
        self.monthly_progress.setValue(0)
        self.monthly_progress.setFormat("This month: %v conversations")
        trends_layout.addWidget(self.monthly_progress)
        
        parent_layout.addWidget(trends_group)
    
    def create_detailed_analytics(self, parent_layout):
        """Create the detailed analytics section."""
        detailed_group = QGroupBox("Detailed Analytics")
        detailed_layout = QVBoxLayout(detailed_group)
        
        # Model usage table
        model_label = QLabel("Model Usage")
        model_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        detailed_layout.addWidget(model_label)
        
        self.model_table = QTableWidget()
        self.model_table.setColumnCount(3)
        self.model_table.setHorizontalHeaderLabels([
            "Model", "Conversations", "Percentage"
        ])
        
        # Configure table
        header = self.model_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        self.model_table.setAlternatingRowColors(True)
        detailed_layout.addWidget(self.model_table)
        
        # Top topics
        topics_label = QLabel("Top Conversation Topics")
        topics_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        detailed_layout.addWidget(topics_label)
        
        self.topics_table = QTableWidget()
        self.topics_table.setColumnCount(3)
        self.topics_table.setHorizontalHeaderLabels([
            "Topic", "Frequency", "Last Used"
        ])
        
        # Configure table
        header = self.topics_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        self.topics_table.setAlternatingRowColors(True)
        detailed_layout.addWidget(self.topics_table)
        
        parent_layout.addWidget(detailed_group)
    
    def update_overview_stats(self, stats: Dict):
        """Update the overview statistics."""
        self.total_conversations_label.setText(str(stats.get('total_conversations', 0)))
        self.total_messages_label.setText(str(stats.get('total_messages', 0)))
        self.total_words_label.setText(str(stats.get('total_words', 0)))
        
        # Calculate average
        total_conv = stats.get('total_conversations', 0)
        total_msgs = stats.get('total_messages', 0)
        avg_length = total_msgs / total_conv if total_conv > 0 else 0
        self.avg_length_label.setText(f"{avg_length:.1f}")
    
    def update_usage_trends(self, trends: Dict):
        """Update the usage trends."""
        # Update progress bars
        daily_conv = trends.get('daily_conversations', 0)
        weekly_conv = trends.get('weekly_conversations', 0)
        monthly_conv = trends.get('monthly_conversations', 0)
        
        # Set reasonable max values
        self.daily_progress.setMaximum(max(daily_conv * 2, 10))
        self.weekly_progress.setMaximum(max(weekly_conv * 2, 50))
        self.monthly_progress.setMaximum(max(monthly_conv * 2, 200))
        
        self.daily_progress.setValue(daily_conv)
        self.weekly_progress.setValue(weekly_conv)
        self.monthly_progress.setValue(monthly_conv)
    
    def update_model_usage(self, model_usage: List[Dict]):
        """Update the model usage table."""
        self.model_table.setRowCount(0)
        
        if not model_usage:
            return
        
        total_conv = sum(usage.get('conversations', 0) for usage in model_usage)
        
        for usage in model_usage:
            row = self.model_table.rowCount()
            self.model_table.insertRow(row)
            
            model = usage.get('model', 'Unknown')
            conversations = usage.get('conversations', 0)
            percentage = (conversations / total_conv * 100) if total_conv > 0 else 0
            
            self.model_table.setItem(row, 0, QTableWidgetItem(model))
            self.model_table.setItem(row, 1, QTableWidgetItem(str(conversations)))
            self.model_table.setItem(row, 2, QTableWidgetItem(f"{percentage:.1f}%"))
    
    def update_topics(self, topics: List[Dict]):
        """Update the topics table."""
        self.topics_table.setRowCount(0)
        
        for topic in topics:
            row = self.topics_table.rowCount()
            self.topics_table.insertRow(row)
            
            self.topics_table.setItem(row, 0, QTableWidgetItem(topic.get('topic', 'Unknown')))
            self.topics_table.setItem(row, 1, QTableWidgetItem(str(topic.get('frequency', 0))))
            self.topics_table.setItem(row, 2, QTableWidgetItem(topic.get('last_used', 'Unknown')))
    
    def on_period_changed(self, period: str):
        """Handle time period change."""
        # This would trigger a refresh with the new period
        self.refresh_requested.emit()
    
    def get_selected_period(self) -> str:
        """Get the currently selected time period."""
        return self.period_combo.currentText()
    
    def update_overview(self, data: Dict):
        """High-level helper that refreshes all sub-sections using a single stats payload."""
        if not data:
            return
        # Overview counts
        overview_stats = {
            'total_conversations': data.get('total_conversations', 0),
            'total_messages': data.get('total_messages', 0),
            'total_words': data.get('total_words', 0)
        }
        self.update_overview_stats(overview_stats)

        # Trend metrics (may be missing in older payloads)
        trends = {
            'daily_conversations': data.get('daily_conversations', 0),
            'weekly_conversations': data.get('weekly_conversations', data.get('recent_activity', 0)),
            'monthly_conversations': data.get('monthly_conversations', 0)
        }
        self.update_usage_trends(trends)

        # Model usage analytics
        models_dict = data.get('models', {}) or {}
        model_usage = [
            {'model': model_name, 'conversations': count}
            for model_name, count in models_dict.items()
        ]
        self.update_model_usage(model_usage)

        # Topics — currently not implemented at backend. Stub for future data.
        if 'topics' in data:
            self.update_topics(data['topics']) 