"""
Conversations Panel for Thea GUI
Displays and manages conversation history.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QTextEdit, QLineEdit,
    QSplitter, QHeaderView, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Dict

# Helper item so the "Messages" column sorts numerically
class NumericItem(QTableWidgetItem):
    def __init__(self, value: int):
        super().__init__(str(value))
        self._value = value

    def __lt__(self, other: "QTableWidgetItem") -> bool:  # type: ignore[override]
        if isinstance(other, NumericItem):
            return self._value < other._value
        # Fallback to default behavior for non-numeric items
        try:
            return float(self.text()) < float(other.text())
        except Exception:
            return super().__lt__(other)

class ConversationsPanel(QWidget):
    """Panel for managing and viewing conversations."""
    
    # Signals
    conversation_selected = pyqtSignal(dict)
    refresh_requested = pyqtSignal()
    process_conversations_requested = pyqtSignal()
    update_statistics_requested = pyqtSignal()
    import_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Pagination state
        self.current_page = 1
        self.page_size = 100
        self.total_conversations = 0
        self.total_pages = 1
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the conversations UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        self.create_header(layout)
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - conversation list
        self.create_conversation_list(splitter)
        
        # Right side - conversation viewer
        self.create_conversation_viewer(splitter)
        
        # Set splitter proportions
        splitter.setSizes([400, 600])
        
        # Pagination controls
        pagination_layout = QHBoxLayout()
        
        self.prev_page_btn = QPushButton("← Previous")
        self.prev_page_btn.clicked.connect(self.previous_page)
        self.prev_page_btn.setEnabled(False)
        pagination_layout.addWidget(self.prev_page_btn)
        
        self.page_info_label = QLabel("Page 1 of 1")
        self.page_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pagination_layout.addWidget(self.page_info_label)
        
        self.next_page_btn = QPushButton("Next →")
        self.next_page_btn.clicked.connect(self.next_page)
        self.next_page_btn.setEnabled(False)
        pagination_layout.addWidget(self.next_page_btn)
        
        # Add page size selector
        pagination_layout.addWidget(QLabel("Page Size:"))
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["50", "100", "200", "500", "All"])
        self.page_size_combo.setCurrentText("100")
        self.page_size_combo.currentTextChanged.connect(self.on_page_size_changed)
        pagination_layout.addWidget(self.page_size_combo)
        
        pagination_layout.addStretch()
        
        # Add total count label
        self.total_count_label = QLabel("Total: 0 conversations")
        pagination_layout.addWidget(self.total_count_label)
        
        layout.addLayout(pagination_layout)
    
    def create_header(self, parent_layout):
        """Create the header section."""
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("💬 Conversations")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search conversations...")
        self.search_box.setMaximumWidth(300)
        self.search_box.textChanged.connect(self.filter_conversations)
        header_layout.addWidget(self.search_box)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(self.refresh_btn)
        
        # Import button – triggers ingest of new JSON files
        self.import_btn = QPushButton("📥 Import New Files")
        self.import_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #e0a800; }
            QPushButton:pressed { background-color: #d39e00; }
        """)
        self.import_btn.clicked.connect(self.import_requested.emit)
        header_layout.addWidget(self.import_btn)
        
        # Process conversations button
        self.process_btn = QPushButton("🌌 Process Dreamscape")
        self.process_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        self.process_btn.clicked.connect(self.process_conversations_requested.emit)
        header_layout.addWidget(self.process_btn)
        
        # Update statistics button
        self.update_stats_btn = QPushButton("📊 Update Stats")
        self.update_stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:pressed {
                background-color: #117a8b;
            }
        """)
        self.update_stats_btn.clicked.connect(self.update_statistics_requested.emit)
        header_layout.addWidget(self.update_stats_btn)
        
        parent_layout.addLayout(header_layout)
    
    def create_conversation_list(self, parent):
        """Create the conversation list table."""
        # Container widget
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        # Table
        self.conversations_table = QTableWidget()
        self.conversations_table.setColumnCount(4)
        self.conversations_table.setHorizontalHeaderLabels([
            "Title", "Source", "Messages", "Date"
        ])
        
        # Configure table
        header = self.conversations_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # Allow user to sort columns (numeric sort handled via NumericItem for message count)
        self.conversations_table.setSortingEnabled(True)
        
        self.conversations_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.conversations_table.itemSelectionChanged.connect(self.on_conversation_selected)
        
        list_layout.addWidget(self.conversations_table)
        
        # Status label
        self.status_label = QLabel("No conversations loaded")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        list_layout.addWidget(self.status_label)
        
        # Add note about chronological order
        order_note = QLabel("📅 Conversations shown in chronological order (oldest first)")
        order_note.setStyleSheet("color: #888; font-size: 10px; font-style: italic;")
        list_layout.addWidget(order_note)
        
        parent.addWidget(list_widget)
    
    def create_conversation_viewer(self, parent):
        """Create the conversation viewer."""
        # Container widget
        viewer_widget = QWidget()
        viewer_layout = QVBoxLayout(viewer_widget)
        viewer_layout.setContentsMargins(0, 0, 0, 0)
        
        # Viewer header
        viewer_header = QHBoxLayout()
        
        self.viewer_title = QLabel("Select a conversation to view")
        self.viewer_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        viewer_header.addWidget(self.viewer_title)
        
        viewer_header.addStretch()
        
        # Export button
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.setEnabled(False)
        viewer_header.addWidget(self.export_btn)
        
        viewer_layout.addLayout(viewer_header)
        
        # Conversation content
        self.conversation_content = QTextEdit()
        self.conversation_content.setReadOnly(True)
        self.conversation_content.setPlaceholderText("Select a conversation from the list to view its content...")
        viewer_layout.addWidget(self.conversation_content)
        
        parent.addWidget(viewer_widget)
    
    def update_conversations_table(self, conversations: List[Dict]):
        """Update the conversations table with new data."""
        self.conversations_table.setRowCount(len(conversations))
        
        for row, conversation in enumerate(conversations):
            # Title
            title_item = QTableWidgetItem(conversation.get('title', 'Untitled'))
            title_item.setData(Qt.ItemDataRole.UserRole, conversation)
            self.conversations_table.setItem(row, 0, title_item)
            
            # Source (instead of model)
            source_item = QTableWidgetItem(conversation.get('source', 'Unknown'))
            self.conversations_table.setItem(row, 1, source_item)
            
            # Message count
            message_count = int(conversation.get('message_count', 0))
            message_item = NumericItem(message_count)
            self.conversations_table.setItem(row, 2, message_item)
            
            # Date
            created_at = conversation.get('created_at', '')
            if created_at:
                # Format date for display
                try:
                    from datetime import datetime
                    if isinstance(created_at, str):
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        dt = created_at
                    date_str = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    date_str = str(created_at)[:19]  # First 19 chars for YYYY-MM-DD HH:MM:SS
            else:
                date_str = 'Unknown'
            
            date_item = QTableWidgetItem(date_str)
            self.conversations_table.setItem(row, 3, date_item)
        
        self.status_label.setText(f"Loaded {len(conversations)} conversations in chronological order")
    
    def on_conversation_selected(self):
        """Handle conversation selection."""
        current_row = self.conversations_table.currentRow()
        if current_row >= 0:
            item = self.conversations_table.item(current_row, 0)
            if item:
                conversation = item.data(Qt.ItemDataRole.UserRole)
                self.view_conversation(conversation)
    
    def view_conversation(self, conversation: Dict):
        """Display a conversation in the viewer."""
        if not conversation:
            return
        
        # Update title
        title = conversation.get('title', 'Untitled')
        self.viewer_title.setText(title)
        
        # Update content
        content = conversation.get('content', 'No content available')
        self.conversation_content.setPlainText(content)
        
        # Enable export button
        self.export_btn.setEnabled(True)
        
        # Emit signal
        self.conversation_selected.emit(conversation)
    
    def filter_conversations(self, text: str):
        """Filter conversations based on search text."""
        for row in range(self.conversations_table.rowCount()):
            title_item = self.conversations_table.item(row, 0)
            if title_item:
                title = title_item.text().lower()
                should_show = not text or text.lower() in title
                self.conversations_table.setRowHidden(row, not should_show)
    
    def get_selected_conversation(self) -> Dict:
        """Get the currently selected conversation."""
        current_row = self.conversations_table.currentRow()
        if current_row >= 0:
            item = self.conversations_table.item(current_row, 0)
            if item:
                return item.data(Qt.ItemDataRole.UserRole)
        return {}
    
    def clear_viewer(self):
        """Clear the conversation viewer."""
        self.viewer_title.setText("Select a conversation to view")
        self.conversation_content.clear()
        self.export_btn.setEnabled(False)
    
    def previous_page(self):
        """Go to the previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_current_page()
    
    def next_page(self):
        """Go to the next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_current_page()
    
    def on_page_size_changed(self, new_size: str):
        """Handle page size change from the combo box."""
        # Special sentinel: "All" -> 0 means unlimited (fetch all rows)
        if new_size.lower() == "all":
            self.page_size = 0
        else:
            try:
                self.page_size = int(new_size)
            except ValueError:
                # Fallback to default 100 if parsing fails
                self.page_size = 100

        self.current_page = 1  # Reset to first page whenever size changes
        self.calculate_total_pages()
        self.load_current_page()
    
    def calculate_total_pages(self):
        """Calculate total number of pages."""
        if self.page_size > 0:
            self.total_pages = (self.total_conversations + self.page_size - 1) // self.page_size
        else:
            self.total_pages = 1
    
    def update_pagination_controls(self):
        """Update pagination control states."""
        # Update page info
        self.page_info_label.setText(f"Page {self.current_page} of {self.total_pages}")
        
        # Update total count
        self.total_count_label.setText(f"Total: {self.total_conversations} conversations")
        
        # Update button states
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < self.total_pages)
    
    def load_current_page(self):
        """Load the current page of conversations."""
        try:
            from core.memory_api import get_memory_api
            api = get_memory_api()

            if self.page_size == 0:
                # "All" – fetch every conversation
                conversations = api.get_conversations_chronological(limit=None, offset=0)
                offset = 0
            else:
                offset = (self.current_page - 1) * self.page_size
                conversations = api.get_conversations_chronological(limit=self.page_size, offset=offset)
            
            # Update table
            self.update_conversations_table(conversations)
            
            # Update pagination controls
            self.update_pagination_controls()
            
            # Update status
            if self.page_size == 0:
                self.status_label.setText(f"Showing all {self.total_conversations} conversations")
            else:
                start_item = offset + 1
                end_item = min(offset + self.page_size, self.total_conversations)
                self.status_label.setText(
                    f"Showing conversations {start_item}-{end_item} of {self.total_conversations}")
            
        except Exception as e:
            self.status_label.setText(f"Error loading page: {e}")
    
    def load_all_conversations(self):
        """Load all conversations with pagination."""
        try:
            # Get total count
            from core.memory_api import get_memory_api
            api = get_memory_api()
            self.total_conversations = api.get_conversations_count()
            
            # Calculate total pages
            self.calculate_total_pages()
            
            # Load first page
            self.current_page = 1
            self.load_current_page()
            
        except Exception as e:
            self.status_label.setText(f"Error loading conversations: {e}") 