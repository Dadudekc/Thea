#!/usr/bin/env python3
"""
Thea Main Window - Dreamscape MMORPG Platform GUI
"""

import sys
import os
import logging
from pathlib import Path
from typing import Any

# Restore UTF-8 console encoding on Windows prior to configuring logging
if sys.platform.startswith("win") and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        # Fallback for older consoles
        try:
            os.system("chcp 65001 > nul")
        except Exception:
            pass

# EDIT START: ensure root logger streams text as UTF-8 (avoids UnicodeEncodeError on Windows)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
    encoding="utf-8",
    force=True,
)
# EDIT END

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QStatusBar, QMessageBox, QProgressDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Import core systems
from core.memory_manager import MemoryManager
from core.memory_api import MemoryAPI
from core.dreamscape_memory import DreamscapeMemory
from core.discord_manager import DiscordManager
from core.mmorpg_engine import MMORPGEngine
from core.dreamscape_processor import DreamscapeProcessor
from scripts.multi_model_prompt_agent import MultiModelPromptAgent
from core.prompt_deployer import PromptDeployer
from core.settings_manager import settings_manager
from core.live_processor import initialize_live_processor, get_live_processor

# Import modular panels
from .panels.dashboard_panel import DashboardPanel
from .panels.conversations_panel import ConversationsPanel
from .panels.templates_panel import TemplatesPanel
from .panels.multi_model_panel import MultiModelPanel
from .panels.settings_panel import SettingsPanel
from gui.panels.analytics_panel import AnalyticsPanel
from gui.panels.resume_panel import ResumePanel
from gui.panels.scraper_panel import ScraperPanel
from gui.panels.task_panel import TaskPanel
from gui.panels.quest_log_panel import QuestLogPanel
from gui.panels.export_panel import ExportPanel

logger = logging.getLogger(__name__)

class TheaMainWindow(QMainWindow):
    """Main window for Thea - Dreamscape MMORPG Platform."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thea - Dreamscape MMORPG Platform")
        self.setMinimumSize(1400, 900)
        
        # Initialize systems
        self.init_systems()
        self.init_ui()
        self.setup_connections()
        self.load_initial_data()
        
    def init_systems(self):
        """Initialize core systems."""
        try:
            # Initialize memory systems
            self.memory_manager = MemoryManager()
            self.memory_api = MemoryAPI()
            self.dreamscape_memory = DreamscapeMemory()
            
            # Initialize MMORPG and processing systems
            self.mmorpg_engine = MMORPGEngine()
            self.dreamscape_processor = DreamscapeProcessor()
            
            # Initialize Discord manager
            self.discord_manager = DiscordManager()
            
            # Initialize other systems
            self.multi_model_agent = MultiModelPromptAgent()
            self.prompt_deployer = PromptDeployer()
            
            # Initialize live processor
            self.live_processor = initialize_live_processor(
                memory_manager=self.memory_manager,
                dreamscape_processor=self.dreamscape_processor,
                mmorpg_engine=self.mmorpg_engine,
                discord_manager=self.discord_manager
            )
            
            # Test MMORPG engine functionality
            try:
                test_player = self.mmorpg_engine.get_player()
                test_skills = self.mmorpg_engine.get_skills()
                logger.info(f"MMORPG engine test: Player={test_player.name}, Skills count={len(test_skills)}")
            except Exception as e:
                logger.error(f"MMORPG engine test failed: {e}")
            
            # --- OPTIONAL FIRST-RUN INGESTION -----------------------------------
            try:
                stats = self.memory_manager.get_conversation_stats()
                if stats.get("total_conversations", 0) == 0:
                    conv_dir = Path("data/conversations")
                    if conv_dir.exists() and any(conv_dir.glob("*.json")):
                        pd = QProgressDialog(
                            "Importing conversations (first run)…", None, 0, 0, self
                        )
                        pd.setWindowTitle("Initializing Database")
                        pd.setWindowModality(Qt.WindowModality.ApplicationModal)
                        pd.setMinimumDuration(0)
                        pd.show()

                        ingested = self.memory_manager.ingest_conversations_async(
                            str(conv_dir), max_workers=8
                        )

                        pd.close()
                        logger.info(f"First-run ingestion completed – {ingested} conversations added")
            except Exception as ingest_exc:
                logger.warning(f"Startup ingestion skipped: {ingest_exc}")
            
            logger.info("All core systems initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize systems: {e}")
            raise
        
    def init_ui(self):
        """Initialize the main UI."""
        self.setWindowTitle("Thea - Dreamscape MMORPG Platform")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.create_sidebar()
        main_layout.addWidget(self.sidebar_frame)
        
        # Create main content area
        self.create_main_content()
        main_layout.addWidget(self.main_content)
        
        # Apply saved theme
        saved_theme = settings_manager.get_theme()
        self.apply_theme(saved_theme)
        
        # Apply styling
        self.apply_styling()
        
        # Set up status bar and styling
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def create_sidebar(self):
        """Create the sidebar navigation."""
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("sidebar")
        self.sidebar_frame.setMaximumWidth(250)
        self.sidebar_frame.setMinimumWidth(200)
        self.sidebar_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        
        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(5)
        
        # Logo/Title
        title_label = QLabel("Thea")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Dreamscape MMORPG")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(subtitle_label)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("🏠 Dashboard", "dashboard"),
            ("💬 Conversations", "conversations"),
            ("🧠 Multi-Model Testing", "multi_model"),
            ("📝 Templates", "templates"),
            ("📋 Quest Log", "tasks"),
            ("📄 Resume", "resume"),
            ("📊 Analytics", "analytics"),
            ("📤 Export", "export"),
            ("📢 Discord/Devlog", "discord"),
            ("⚙️ Settings", "settings")
        ]
        
        for text, key in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            btn.setProperty("class", "nav")
            btn.clicked.connect(lambda checked, k=key: self.switch_panel(k))
            self.nav_buttons[key] = btn
            sidebar_layout.addWidget(btn)
        
        self.nav_buttons["dashboard"].setChecked(True)
        
        sidebar_layout.addStretch()
        
        # Player info
        self.player_info = QLabel("Loading player info...")
        self.player_info.setWordWrap(True)
        sidebar_layout.addWidget(self.player_info)
        
    def _create_placeholder_panel(self, title: str) -> QWidget:
        """Return a simple QWidget with a large centered 'Coming Soon' message."""
        placeholder = QWidget()
        layout = QVBoxLayout(placeholder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel(f"{title} – Coming Soon")
        label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return placeholder

    def create_main_content(self):
        """Create the main content area with stacked panels."""
        self.main_content = QStackedWidget()
        self.panel_indices = {}

        def _add_panel(key: str, widget: QWidget):
            self.main_content.addWidget(widget)
            self.panel_indices[key] = self.main_content.count() - 1

        # Core implemented panels
        self.dashboard_panel = DashboardPanel()
        self.conversations_panel = ConversationsPanel()
        self.multi_model_panel = MultiModelPanel()
        self.templates_panel = TemplatesPanel()

        _add_panel("dashboard", self.dashboard_panel)
        _add_panel("conversations", self.conversations_panel)
        _add_panel("multi_model", self.multi_model_panel)
        _add_panel("templates", self.templates_panel)

        # Placeholders for not-yet implemented panels
        self.task_panel = self._create_placeholder_panel("Quest Log")
        self.resume_panel = self._create_placeholder_panel("Resume Builder")
        self.analytics_panel = self._create_placeholder_panel("Analytics")
        self.export_panel = self._create_placeholder_panel("Export")
        self.discord_panel = self._create_placeholder_panel("Discord / Devlog")

        _add_panel("tasks", QuestLogPanel(self.mmorpg_engine))
        _add_panel("resume", self.resume_panel)
        self.analytics_panel = AnalyticsPanel()
        _add_panel("analytics", self.analytics_panel)
        _add_panel("export", ExportPanel())
        _add_panel("discord", self.discord_panel)

        # Settings panel
        self.settings_panel = SettingsPanel()
        _add_panel("settings", self.settings_panel)

        # Set dashboard as default
        self.main_content.setCurrentIndex(self.panel_indices["dashboard"])
        
    def add_placeholder_panels(self):
        """Add placeholder panels for unimplemented sections."""
        placeholder_texts = [
            "📄 Resume - Coming Soon", 
            "📊 Analytics - Coming Soon",
            "📤 Export - Coming Soon",
            "📢 Discord/Devlog - Coming Soon"
        ]
        
        for text in placeholder_texts:
            placeholder = QWidget()
            layout = QVBoxLayout(placeholder)
            label = QLabel(text)
            label.setFont(QFont("Arial", 16))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            self.main_content.addWidget(placeholder)
        
    def setup_connections(self):
        """Set up signal connections between components."""
        self.conversations_panel.refresh_requested.connect(self.refresh_conversations)
        self.conversations_panel.process_conversations_requested.connect(self.process_conversations)
        self.conversations_panel.update_statistics_requested.connect(self.update_conversation_statistics)
        self.conversations_panel.conversation_selected.connect(self.on_conversation_selected)
        self.templates_panel.template_saved.connect(self.on_template_saved)
        self.templates_panel.template_deleted.connect(self.on_template_deleted)
        self.multi_model_panel.test_completed.connect(self.on_test_completed)
        self.settings_panel.settings_saved.connect(self.on_settings_saved)
        
        # Connect theme changes
        self.settings_panel.general_settings.theme_changed.connect(self.switch_theme)
        
        # Refresh analytics when tab opened
        self.main_content.currentChanged.connect(self._on_stack_changed)
        
        # Connect analytics panel refresh_requested to update its overview using unified stats updater
        from core.conversation_stats_updater import ConversationStatsUpdater
        self.analytics_panel.refresh_requested.connect(
            lambda: self.analytics_panel.update_overview(
                ConversationStatsUpdater(self.memory_manager).get_conversation_stats_summary(trend=True)
            )
        )
        
    def switch_panel(self, panel_name: str):
        """Switch to a different panel using the dynamic index map."""
        if hasattr(self, 'panel_indices') and panel_name in self.panel_indices:
            self.main_content.setCurrentIndex(self.panel_indices[panel_name])
            for key, btn in self.nav_buttons.items():
                btn.setChecked(key == panel_name)
        else:
            logger.warning(f"Panel '{panel_name}' not available in stack")
    
    def load_initial_data(self):
        """Load initial data for the application."""
        try:
            self.refresh_conversations()
            self.load_templates()
            self.update_dashboard()
        except Exception as e:
            self.show_error(f"Failed to load initial data: {e}")
    
    def refresh_conversations(self):
        """Refresh the conversations list with pagination and ingest new files."""
        # EDIT START – auto-ingest new JSON files dropped into data/conversations/
        try:
            ingested = 0
            try:
                ingested = self.memory_manager.ingest_conversations("data/conversations")
            except Exception as ingest_err:
                logger.warning(f"Conversation ingestion skipped/failed during refresh: {ingest_err}")

            # Reload the table view
            self.conversations_panel.load_all_conversations()

            # User-facing message
            suffix = f" — {ingested} new file{'s' if ingested != 1 else ''} ingested" if ingested else ""
            self.status_bar.showMessage(f"Conversations refreshed{suffix}", 5000)
        except Exception as e:
            self.show_error(f"Failed to refresh conversations: {e}")
        # EDIT END
    
    def process_conversations(self):
        """Process ALL conversations through the dreamscape system in chronological order."""
        try:
            # Create dreamscape processor
            processor = DreamscapeProcessor()
            
            # Get total conversation count
            total_count = self.memory_api.get_conversations_count()
            
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                "Process All Conversations",
                f"This will process ALL {total_count} conversations through the dreamscape system.\n\n"
                "This may take several minutes. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Show progress dialog
            progress = QProgressDialog(f"Processing ALL {total_count} conversations through dreamscape in chronological order...", "Cancel", 0, 100, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setAutoClose(True)
            progress.setValue(0)
            
            # Process ALL conversations in chronological order (oldest first)
            result = processor.process_conversations_chronological(limit=None)  # None = process all
            
            progress.setValue(100)
            
            if result.get("error"):
                self.show_error(f"Failed to process conversations: {result['error']}")
                return
            
            processed_count = result.get("processed_count", 0)
            total_conversations = result.get("total_conversations", 0)
            conversations_processed = result.get("conversations_processed", 0)
            
            processor.close()
            
            # Update status
            self.status_bar.showMessage(f"Processed {processed_count}/{conversations_processed} conversations through dreamscape", 5000)
            
            # Refresh dashboard to show updated stats
            self.update_dashboard()
            
            # Show completion message
            message = f"Successfully processed {processed_count}/{conversations_processed} conversations through the dreamscape system!\n\n"
            message += f"Total conversations in database: {total_conversations}\n\n"
            message += "Your MMORPG storyline has been updated with new quests, skills, and domains.\n\n"
            message += "Conversations were processed in chronological order (oldest first) to ensure proper storyline progression."
            
            if result.get("errors"):
                message += f"\n\nErrors encountered: {len(result['errors'])}"
                for error in result["errors"][:5]:  # Show first 5 errors
                    message += f"\n• {error}"
                if len(result["errors"]) > 5:
                    message += f"\n• ... and {len(result['errors']) - 5} more errors"
            
            QMessageBox.information(self, "Processing Complete", message)
            
        except Exception as e:
            self.show_error(f"Failed to process conversations: {e}")
    
    def update_conversation_statistics(self):
        """Update conversation statistics by extracting messages and updating counts."""
        try:
            from core.conversation_stats_updater import ConversationStatsUpdater
            
            # Create stats updater
            stats_updater = ConversationStatsUpdater(self.memory_manager)
            
            # Get total conversation count
            total_count = self.memory_api.get_conversations_count()
            
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                "Update Conversation Statistics",
                f"This will update statistics for ALL {total_count} conversations by extracting messages and updating counts.\n\n"
                "This will ensure accurate message counts and word counts. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Show progress dialog
            progress = QProgressDialog(f"Updating statistics for ALL {total_count} conversations...", "Cancel", 0, 100, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setAutoClose(True)
            progress.setValue(0)
            
            # Update all conversation statistics
            result = stats_updater.update_all_conversation_stats(limit=None)  # None = update all
            
            progress.setValue(100)
            
            if result.get("error"):
                self.show_error(f"Failed to update conversation statistics: {result['error']}")
                return
            
            updated_count = result.get("updated_count", 0)
            total_conversations = result.get("total_conversations", 0)
            
            # Get updated stats summary
            stats_summary = stats_updater.get_conversation_stats_summary()
            
            # Update status
            self.status_bar.showMessage(f"Updated statistics for {updated_count}/{total_conversations} conversations", 5000)
            
            # Refresh conversations panel to show updated counts
            self.refresh_conversations()
            
            # Show completion message
            message = f"Successfully updated statistics for {updated_count}/{total_conversations} conversations!\n\n"
            message += f"Total conversations: {stats_summary.get('total_conversations', 0)}\n"
            message += f"Total messages: {stats_summary.get('total_messages', 0)}\n"
            message += f"Total words: {stats_summary.get('total_words', 0)}\n"
            message += f"Accuracy: {stats_summary.get('accuracy', 'Unknown')}\n\n"
            message += "Message counts and word counts are now accurate and up-to-date."
            
            if result.get("errors"):
                message += f"\n\nErrors encountered: {len(result['errors'])}"
                for error in result["errors"][:5]:  # Show first 5 errors
                    message += f"\n• {error}"
                if len(result["errors"]) > 5:
                    message += f"\n• ... and {len(result['errors']) - 5} more errors"
            
            QMessageBox.information(self, "Statistics Update Complete", message)
            
        except Exception as e:
            self.show_error(f"Failed to update conversation statistics: {e}")
    
    def process_conversations_with_stats_update(self):
        """Process conversations and update statistics in one operation."""
        try:
            # First update statistics
            self.update_conversation_statistics()
            
            # Then process through dreamscape
            self.process_conversations()
            
        except Exception as e:
            self.show_error(f"Failed to process conversations with stats update: {e}")
    
    def load_templates(self):
        """Load templates from the template engine."""
        try:
            templates = []  # Placeholder - would load from template engine
            self.templates_panel.load_templates(templates)
        except Exception as e:
            self.show_error(f"Failed to load templates: {e}")
    
    def update_dashboard(self):
        """Update the dashboard with current data."""
        try:
            # Get player info
            player = self.mmorpg_engine.get_player()
            self.dashboard_panel.update_player_info(player)
            
            # Get skills
            skills = self.mmorpg_engine.get_skills()
            logger.debug(f"Skills type: {type(skills)}, Skills value: {skills}")
            self.dashboard_panel.update_skills(skills)
            
            # Get game stats
            game_stats = self.mmorpg_engine.get_game_status()
            self.dashboard_panel.update_stats(game_stats)
            
            # Update player info in sidebar
            self.player_info.setText(f"{player.name}\n{player.architect_tier}\n{player.xp} XP")
            
            # Check live processor status
            self.dashboard_panel.check_live_processor_status()
            
        except Exception as e:
            logger.error(f"Failed to update dashboard: {e}")
            self.show_error(f"Failed to update dashboard: {e}")
    
    def on_conversation_selected(self, conversation): pass
    def on_template_saved(self, template): self.status_bar.showMessage(f"Template '{template.get('name', 'Unknown')}' saved")
    def on_template_deleted(self, template_name): self.status_bar.showMessage(f"Template '{template_name}' deleted")
    def on_test_completed(self, result): self.status_bar.showMessage(f"Test completed: {result.get('models_tested', 0)} models tested")
    def on_settings_saved(self, settings): self.status_bar.showMessage("Settings saved successfully")
    
    def apply_styling(self):
        """Apply modern styling to the application."""
        # Get current theme from settings
        theme = self.get_current_theme()
        self.apply_theme(theme)
    
    def get_current_theme(self) -> str:
        """Get the current theme setting."""
        return settings_manager.get_theme()
    
    def apply_theme(self, theme: str):
        """Apply a specific theme to the application."""
        if theme == 'Dark':
            self.apply_dark_theme()
        elif theme == 'Light':
            self.apply_light_theme()
        else:  # System theme
            self.apply_system_theme()
    
    def apply_dark_theme(self):
        """Apply dark theme styling."""
        self.setStyleSheet("""
            /* Main Window */
            QMainWindow { 
                background-color: #1e1e1e; 
                color: #ffffff;
            }
            
            /* Sidebar */
            QFrame#sidebar { 
                background-color: #252526; 
                border: 1px solid #3e3e42; 
                border-radius: 5px; 
            }
            
            /* Buttons */
            QPushButton { 
                background-color: #0e639c; 
                color: white; 
                border: none; 
                padding: 8px 16px; 
                border-radius: 4px; 
                font-weight: bold; 
            }
            QPushButton:hover { 
                background-color: #1177bb; 
            }
            QPushButton:pressed { 
                background-color: #0c5a8b; 
            }
            QPushButton:checked { 
                background-color: #1177bb; 
            }
            QPushButton:disabled {
                background-color: #3e3e42;
                color: #6a6a6a;
            }
            
            /* Navigation buttons */
            QPushButton[class="nav"] {
                background-color: transparent;
                color: #cccccc;
                text-align: left;
                padding: 10px 15px;
                border-radius: 0px;
                font-weight: normal;
            }
            QPushButton[class="nav"]:hover {
                background-color: #2a2d2e;
            }
            QPushButton[class="nav"]:checked {
                background-color: #37373d;
                color: #ffffff;
            }
            
            /* Labels */
            QLabel { 
                color: #cccccc; 
            }
            
            /* Group boxes */
            QGroupBox { 
                font-weight: bold; 
                border: 2px solid #3e3e42; 
                border-radius: 5px; 
                margin-top: 1ex; 
                padding-top: 10px; 
                color: #cccccc;
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 10px; 
                padding: 0 5px 0 5px; 
                color: #cccccc;
            }
            
            /* Tables */
            QTableWidget {
                background-color: #252526;
                alternate-background-color: #2d2d30;
                color: #cccccc;
                gridline-color: #3e3e42;
                border: 1px solid #3e3e42;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #094771;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #2d2d30;
                color: #cccccc;
                padding: 5px;
                border: 1px solid #3e3e42;
                font-weight: bold;
            }
            
            /* Text areas */
            QTextEdit, QPlainTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                border: 1px solid #3e3e42;
                border-radius: 4px;
            }
            
            /* Line edits */
            QLineEdit {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
            
            /* Combo boxes */
            QComboBox {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #cccccc;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #3e3e42;
                selection-background-color: #094771;
            }
            
            /* Spin boxes */
            QSpinBox {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                padding: 5px;
            }
            
            /* Check boxes */
            QCheckBox {
                color: #cccccc;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                background-color: #3c3c3c;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc;
                border: 1px solid #007acc;
            }
            
            /* Tab widget */
            QTabWidget::pane {
                border: 1px solid #3e3e42;
                background-color: #252526;
            }
            QTabBar::tab {
                background-color: #2d2d30;
                color: #cccccc;
                padding: 8px 16px;
                border: 1px solid #3e3e42;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #252526;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #3e3e42;
            }
            
            /* Scroll bars */
            QScrollBar:vertical {
                background-color: #2d2d30;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3e3e42;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4e4e52;
            }
            
            /* Progress bars */
            QProgressBar {
                border: 1px solid #3e3e42;
                border-radius: 4px;
                text-align: center;
                background-color: #2d2d30;
                color: #cccccc;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 3px;
            }
            
            /* Status bar */
            QStatusBar {
                background-color: #007acc;
                color: #ffffff;
            }
            
            /* Menu bar */
            QMenuBar {
                background-color: #2d2d30;
                color: #cccccc;
                border-bottom: 1px solid #3e3e42;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #3e3e42;
            }
            QMenu {
                background-color: #2d2d30;
                color: #cccccc;
                border: 1px solid #3e3e42;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
        """)
    
    def apply_light_theme(self):
        """Apply light theme styling."""
        self.setStyleSheet("""
            /* Main Window */
            QMainWindow { 
                background-color: #f5f5f5; 
                color: #333333;
            }
            
            /* Sidebar */
            QFrame#sidebar { 
                background-color: #ffffff; 
                border: 1px solid #ddd; 
                border-radius: 5px; 
            }
            
            /* Buttons */
            QPushButton { 
                background-color: #0078d4; 
                color: white; 
                border: none; 
                padding: 8px 16px; 
                border-radius: 4px; 
                font-weight: bold; 
            }
            QPushButton:hover { 
                background-color: #106ebe; 
            }
            QPushButton:pressed { 
                background-color: #005a9e; 
            }
            QPushButton:checked { 
                background-color: #106ebe; 
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            /* Navigation buttons */
            QPushButton[class="nav"] {
                background-color: transparent;
                color: #333333;
                text-align: left;
                padding: 10px 15px;
                border-radius: 0px;
                font-weight: normal;
            }
            QPushButton[class="nav"]:hover {
                background-color: #f0f0f0;
            }
            QPushButton[class="nav"]:checked {
                background-color: #e1f5fe;
                color: #0078d4;
            }
            
            /* Labels */
            QLabel { 
                color: #333333; 
            }
            
            /* Group boxes */
            QGroupBox { 
                font-weight: bold; 
                border: 2px solid #ddd; 
                border-radius: 5px; 
                margin-top: 1ex; 
                padding-top: 10px; 
                color: #333333;
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 10px; 
                padding: 0 5px 0 5px; 
                color: #333333;
            }
            
            /* Tables */
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                color: #333333;
                gridline-color: #ddd;
                border: 1px solid #ddd;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                color: #333333;
                padding: 5px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
            
            /* Text areas */
            QTextEdit, QPlainTextEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            
            /* Line edits */
            QLineEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
            
            /* Combo boxes */
            QComboBox {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #333333;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #ddd;
                selection-background-color: #0078d4;
            }
            
            /* Spin boxes */
            QSpinBox {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
            
            /* Check boxes */
            QCheckBox {
                color: #333333;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #0078d4;
            }
            
            /* Tab widget */
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                color: #333333;
                padding: 8px 16px;
                border: 1px solid #ddd;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #0078d4;
            }
            QTabBar::tab:hover {
                background-color: #e9e9e9;
            }
            
            /* Scroll bars */
            QScrollBar:vertical {
                background-color: #f5f5f5;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c1c1c1;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a8a8a8;
            }
            
            /* Progress bars */
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
                background-color: #f5f5f5;
                color: #333333;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
            
            /* Status bar */
            QStatusBar {
                background-color: #0078d4;
                color: #ffffff;
            }
            
            /* Menu bar */
            QMenuBar {
                background-color: #f5f5f5;
                color: #333333;
                border-bottom: 1px solid #ddd;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #e9e9e9;
            }
            QMenu {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #ddd;
            }
            QMenu::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
        """)
    
    def apply_system_theme(self):
        """Apply system theme (follows OS theme)."""
        # For now, default to light theme
        # In a full implementation, this would detect the OS theme
        self.apply_light_theme()
    
    def switch_theme(self, theme: str):
        """Switch to a specific theme."""
        settings_manager.set_theme(theme)
        self.apply_theme(theme)
        
    def show_error(self, message: str):
        """Show an error message."""
        QMessageBox.critical(self, "Error", message)
        self.status_bar.showMessage(f"Error: {message}")

    def _handle_scraper_event(self, event_type: str, data: Any):
        """Handle events from the scraper panel."""
        if event_type == "conversations_extracted":
            # AI Interaction panel disabled; placeholder for future integration
            pass
        
        # ... existing event handling code ...

    def _on_stack_changed(self, index: int):
        # If analytics panel is shown, refresh its data using unified stats updater
        if hasattr(self, 'analytics_panel') and index == self.panel_indices.get("analytics"):
            try:
                from core.conversation_stats_updater import ConversationStatsUpdater
                stats = ConversationStatsUpdater(self.memory_manager).get_conversation_stats_summary(trend=True)
                self.analytics_panel.update_overview(stats)
            except Exception as e:
                logger.warning(f"Failed to refresh analytics: {e}")

def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Thea - Dreamscape MMORPG Platform")
    app.setApplicationVersion("1.0.0")
    
    window = TheaMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 