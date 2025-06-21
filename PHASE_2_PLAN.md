# Phase 2 Implementation Plan: Data Management & GUI Enhancement

## 🎯 Phase 2 Overview

**Goal**: Transform Digital Dreamscape from a basic scraper into a full-featured conversation management platform with persistent storage and enhanced GUI.

**Timeline**: 4-6 weeks
**Priority**: High (Foundation for all future features)

## 📊 Current Status

### ✅ Completed (Phase 1)
- ChatGPT scraper with undetected-chromedriver
- Automated login with .env support
- Template engine for prompt generation
- Basic PyQt6 GUI framework
- Cookie management and session persistence

### 🔄 In Progress (Phase 2)
- Database schema design
- GUI enhancement planning
- Data model architecture

### 📋 Planned (Phase 2)
- SQLite database integration
- Enhanced GUI components
- Search and filter functionality
- Settings and configuration management

## 🗄️ Database Integration (Week 1-2)

### 2.1 Database Schema Design

#### Core Tables

**1. Conversations Table**
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT UNIQUE,
    content TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scraped_at TIMESTAMP,
    is_analyzed BOOLEAN DEFAULT FALSE
);
```

**2. Analysis Results Table**
```sql
CREATE TABLE analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER,
    analysis_type TEXT NOT NULL,
    results JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

**3. Templates Table**
```sql
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**4. Settings Table**
```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 SQLAlchemy Integration

#### Dependencies to Add
```bash
pip install sqlalchemy alembic
```

#### Model Implementation
```python
# models/database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True)
    content = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    scraped_at = Column(DateTime)
    is_analyzed = Column(Boolean, default=False)
    
    # Relationships
    analysis_results = relationship("AnalysisResult", back_populates="conversation")

class AnalysisResult(Base):
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    analysis_type = Column(String, nullable=False)
    results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="analysis_results")

class Template(Base):
    __tablename__ = 'templates'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Setting(Base):
    __tablename__ = 'settings'
    
    key = Column(String, primary_key=True)
    value = Column(Text)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 2.3 Database Manager

#### Database Connection
```python
# core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path="data/dreamscape.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        """Get database session."""
        return self.SessionLocal()
        
    def close_session(self, session):
        """Close database session."""
        session.close()
```

## 🖥️ GUI Enhancement (Week 3-4)

### 2.4 Main Dashboard Redesign

#### Dashboard Components
```python
# gui/dashboard.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Digital Dreamscape Dashboard")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Statistics Cards
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(self.create_stat_card("Total Conversations", "0"))
        stats_layout.addWidget(self.create_stat_card("Analyzed", "0"))
        stats_layout.addWidget(self.create_stat_card("Templates", "0"))
        layout.addLayout(stats_layout)
        
        # Quick Actions
        actions_layout = QHBoxLayout()
        actions_layout.addWidget(QPushButton("Scrape Conversations"))
        actions_layout.addWidget(QPushButton("Run Analysis"))
        actions_layout.addWidget(QPushButton("Export Data"))
        layout.addLayout(actions_layout)
        
        self.setLayout(layout)
        
    def create_stat_card(self, title, value):
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(title))
        layout.addWidget(QLabel(value))
        card.setLayout(layout)
        
        return card
```

### 2.5 Conversation Browser

#### Tree View Implementation
```python
# gui/conversation_browser.py
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal

class ConversationBrowser(QWidget):
    conversation_selected = pyqtSignal(int)  # conversation_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search conversations...")
        self.search_bar.textChanged.connect(self.filter_conversations)
        layout.addWidget(self.search_bar)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Conversations"])
        self.tree.itemClicked.connect(self.on_conversation_selected)
        layout.addWidget(self.tree)
        
        self.setLayout(layout)
        
    def load_conversations(self, conversations):
        """Load conversations into tree view."""
        self.tree.clear()
        
        for conv in conversations:
            item = QTreeWidgetItem([conv.title])
            item.setData(0, Qt.ItemDataRole.UserRole, conv.id)
            self.tree.addTopLevelItem(item)
            
    def filter_conversations(self, text):
        """Filter conversations based on search text."""
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            item.setHidden(text.lower() not in item.text(0).lower())
            
    def on_conversation_selected(self, item, column):
        """Handle conversation selection."""
        conv_id = item.data(0, Qt.ItemDataRole.UserRole)
        self.conversation_selected.emit(conv_id)
```

### 2.6 Settings Panel

#### Settings Management
```python
# gui/settings_panel.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QCheckBox, QSpinBox

class SettingsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Credentials Section
        credentials_group = QGroupBox("ChatGPT Credentials")
        credentials_layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        
        credentials_layout.addRow("Username:", self.username_edit)
        credentials_layout.addRow("Password:", self.password_edit)
        credentials_group.setLayout(credentials_layout)
        layout.addWidget(credentials_group)
        
        # Scraper Settings
        scraper_group = QGroupBox("Scraper Settings")
        scraper_layout = QFormLayout()
        
        self.headless_checkbox = QCheckBox()
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(10, 120)
        self.timeout_spinbox.setValue(30)
        
        scraper_layout.addRow("Headless Mode:", self.headless_checkbox)
        scraper_layout.addRow("Timeout (seconds):", self.timeout_spinbox)
        scraper_group.setLayout(scraper_layout)
        layout.addWidget(scraper_group)
        
        self.setLayout(layout)
```

## 🔧 Integration Tasks

### 2.7 Scraper-Database Integration

#### Update ChatGPT Scraper
```python
# scrapers/chatgpt_scraper.py (additions)
from core.database import DatabaseManager
from models.database import Conversation

class ChatGPTScraper:
    def __init__(self, db_manager=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_manager = db_manager or DatabaseManager()
        
    def save_conversations_to_db(self, conversations):
        """Save scraped conversations to database."""
        session = self.db_manager.get_session()
        try:
            for conv_data in conversations:
                # Check if conversation already exists
                existing = session.query(Conversation).filter_by(url=conv_data['url']).first()
                if not existing:
                    conv = Conversation(
                        title=conv_data['title'],
                        url=conv_data['url'],
                        content=conv_data.get('content', ''),
                        metadata=conv_data.get('metadata', {}),
                        scraped_at=datetime.utcnow()
                    )
                    session.add(conv)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save conversations to database: {e}")
            return False
        finally:
            self.db_manager.close_session(session)
```

### 2.8 GUI-Database Integration

#### Main Window Updates
```python
# gui/main_window.py (updates)
from core.database import DatabaseManager
from gui.dashboard import DashboardWidget
from gui.conversation_browser import ConversationBrowser
from gui.settings_panel import SettingsPanel

class DigitalDreamscapeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.setup_ui()
        
    def setup_ui(self):
        # Create central widget with tabs
        self.tab_widget = QTabWidget()
        
        # Dashboard tab
        self.dashboard = DashboardWidget()
        self.tab_widget.addTab(self.dashboard, "Dashboard")
        
        # Conversations tab
        self.conversation_browser = ConversationBrowser()
        self.conversation_browser.conversation_selected.connect(self.on_conversation_selected)
        self.tab_widget.addTab(self.conversation_browser, "Conversations")
        
        # Settings tab
        self.settings_panel = SettingsPanel()
        self.tab_widget.addTab(self.settings_panel, "Settings")
        
        self.setCentralWidget(self.tab_widget)
        
    def load_conversations(self):
        """Load conversations from database."""
        session = self.db_manager.get_session()
        try:
            conversations = session.query(Conversation).all()
            self.conversation_browser.load_conversations(conversations)
        finally:
            self.db_manager.close_session(session)
```

## 📋 Implementation Checklist

### Week 1: Database Foundation
- [ ] **Day 1-2**: Design database schema
- [ ] **Day 3-4**: Implement SQLAlchemy models
- [ ] **Day 5**: Create database manager class
- [ ] **Day 6-7**: Add database migration scripts

### Week 2: Database Integration
- [ ] **Day 1-2**: Update scraper to save to database
- [ ] **Day 3-4**: Create data access layer
- [ ] **Day 5-6**: Add database tests
- [ ] **Day 7**: Database performance optimization

### Week 3: GUI Enhancement
- [ ] **Day 1-2**: Redesign main dashboard
- [ ] **Day 3-4**: Implement conversation browser
- [ ] **Day 5-6**: Add search and filter functionality
- [ ] **Day 7**: Create settings panel

### Week 4: Integration & Testing
- [ ] **Day 1-2**: Integrate GUI with database
- [ ] **Day 3-4**: Add error handling and validation
- [ ] **Day 5-6**: Comprehensive testing
- [ ] **Day 7**: Performance optimization and bug fixes

## 🎯 Success Criteria

### Technical Requirements
- [ ] **Database**: All conversations stored in SQLite
- [ ] **GUI**: Responsive interface with search/filter
- [ ] **Integration**: Seamless scraper-database-GUI workflow
- [ ] **Performance**: < 2 seconds for database operations

### User Experience Requirements
- [ ] **Setup**: < 5 minutes to first conversation view
- [ ] **Navigation**: Intuitive conversation browsing
- [ ] **Search**: Fast and accurate conversation filtering
- [ ] **Settings**: Easy configuration management

### Quality Requirements
- [ ] **Testing**: > 90% code coverage
- [ ] **Documentation**: Complete API and user documentation
- [ ] **Error Handling**: Graceful error recovery
- [ ] **Performance**: < 500MB memory usage

## 🚀 Next Phase Preparation

### Phase 3 Readiness
- [ ] **Database Schema**: Extensible for analysis results
- [ ] **GUI Framework**: Modular for new features
- [ ] **API Design**: Clean interfaces for analysis engine
- [ ] **Performance**: Scalable for large datasets

### Documentation Updates
- [ ] **User Guide**: Updated for new GUI features
- [ ] **Developer Guide**: Database schema documentation
- [ ] **API Reference**: New database and GUI APIs
- [ ] **Installation Guide**: Database setup instructions

---

**Phase 2** will transform Digital Dreamscape into a professional conversation management platform, setting the foundation for advanced analysis features in Phase 3. 🚀 