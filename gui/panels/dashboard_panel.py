"""
Dashboard Panel for Thea GUI
Displays overview statistics and quick actions.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QProgressBar, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)

class DashboardPanel(QWidget):
    """Dashboard panel showing overview and statistics."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Welcome section
        self.create_welcome_section(layout)
        
        # Statistics section
        self.create_stats_section(layout)
        
        # Quick actions section
        self.create_quick_actions_section(layout)
        
        # Player progress section
        self.create_player_progress_section(layout)
        
        # Live Processing Controls
        self.create_live_processing_controls(layout)
    
    def create_welcome_section(self, parent_layout):
        """Create the welcome section."""
        welcome_frame = QFrame()
        welcome_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        welcome_layout = QVBoxLayout(welcome_frame)
        
        # Welcome title
        welcome_title = QLabel("Welcome to Thea - Dreamscape MMORPG")
        welcome_title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_title)
        
        # Welcome subtitle
        welcome_subtitle = QLabel("Your AI-powered development journey awaits")
        welcome_subtitle.setFont(QFont("Arial", 14))
        welcome_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_subtitle.setStyleSheet("color: #666;")
        welcome_layout.addWidget(welcome_subtitle)
        
        parent_layout.addWidget(welcome_frame)
    
    def create_stats_section(self, parent_layout):
        """Create the statistics section."""
        stats_group = QGroupBox("System Statistics")
        stats_layout = QGridLayout(stats_group)
        
        # Memory stats
        self.memory_stats = {
            'conversations': QLabel("0"),
            'messages': QLabel("0"),
            'words': QLabel("0"),
            'templates': QLabel("0")
        }
        
        stats_layout.addWidget(QLabel("Total Conversations:"), 0, 0)
        stats_layout.addWidget(self.memory_stats['conversations'], 0, 1)
        
        stats_layout.addWidget(QLabel("Total Messages:"), 1, 0)
        stats_layout.addWidget(self.memory_stats['messages'], 1, 1)
        
        stats_layout.addWidget(QLabel("Total Words:"), 2, 0)
        stats_layout.addWidget(self.memory_stats['words'], 2, 1)
        
        stats_layout.addWidget(QLabel("Available Templates:"), 3, 0)
        stats_layout.addWidget(self.memory_stats['templates'], 3, 1)
        
        parent_layout.addWidget(stats_group)
    
    def create_quick_actions_section(self, parent_layout):
        """Create the quick actions section."""
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        # Quick action buttons
        self.refresh_btn = QPushButton("🔄 Refresh Data")
        self.refresh_btn.setMinimumHeight(40)
        actions_layout.addWidget(self.refresh_btn)
        
        self.new_conversation_btn = QPushButton("💬 New Conversation")
        self.new_conversation_btn.setMinimumHeight(40)
        actions_layout.addWidget(self.new_conversation_btn)
        
        self.export_btn = QPushButton("📤 Export Data")
        self.export_btn.setMinimumHeight(40)
        actions_layout.addWidget(self.export_btn)
        
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.setMinimumHeight(40)
        actions_layout.addWidget(self.settings_btn)
        
        parent_layout.addWidget(actions_group)
    
    def create_player_progress_section(self, parent_layout):
        """Create the player progress section."""
        progress_group = QGroupBox("Player Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        # Player info
        self.player_info = QLabel("Loading player info...")
        self.player_info.setFont(QFont("Arial", 12))
        progress_layout.addWidget(self.player_info)
        
        # XP Progress
        xp_layout = QHBoxLayout()
        xp_layout.addWidget(QLabel("XP Progress:"))
        
        self.xp_progress = QProgressBar()
        self.xp_progress.setRange(0, 100)
        self.xp_progress.setValue(0)
        xp_layout.addWidget(self.xp_progress)
        
        self.xp_label = QLabel("0 / 0 XP")
        xp_layout.addWidget(self.xp_label)
        
        progress_layout.addLayout(xp_layout)
        
        # Skills
        skills_layout = QHBoxLayout()
        skills_layout.addWidget(QLabel("Skills:"))
        
        self.skills_label = QLabel("No skills available")
        skills_layout.addWidget(self.skills_label)
        
        progress_layout.addLayout(skills_layout)
        
        parent_layout.addWidget(progress_group)
    
    def create_live_processing_controls(self, parent_layout):
        """Create the live processing controls section."""
        live_group = QGroupBox("🚀 Live Processing")
        live_layout = QVBoxLayout(live_group)
        
        # Status display
        self.live_status_label = QLabel("Status: Not Configured")
        self.live_status_label.setStyleSheet("font-weight: bold; color: #888;")
        live_layout.addWidget(self.live_status_label)
        
        # Control buttons
        live_buttons_layout = QHBoxLayout()
        
        self.start_live_btn = QPushButton("Start Live Processing")
        self.start_live_btn.clicked.connect(self.start_live_processing)
        self.start_live_btn.setEnabled(False)
        live_buttons_layout.addWidget(self.start_live_btn)
        
        self.stop_live_btn = QPushButton("Stop Live Processing")
        self.stop_live_btn.clicked.connect(self.stop_live_processing)
        self.stop_live_btn.setEnabled(False)
        live_buttons_layout.addWidget(self.stop_live_btn)
        
        live_layout.addLayout(live_buttons_layout)
        
        # Stats display
        self.live_stats_label = QLabel("Processing Stats: Not available")
        self.live_stats_label.setWordWrap(True)
        live_layout.addWidget(self.live_stats_label)
        
        parent_layout.addWidget(live_group)
    
    def update_stats(self, stats: dict):
        """Update the statistics display."""
        try:
            # Handle MMORPG game stats
            if 'total_xp' in stats:
                self.memory_stats['words'].setText(str(stats['total_xp']))  # Use XP as word count for now
            
            if 'active_quests' in stats:
                self.memory_stats['conversations'].setText(str(stats['active_quests']))
            
            if 'completed_quests' in stats:
                self.memory_stats['messages'].setText(str(stats['completed_quests']))
            
            if 'skills' in stats:
                self.memory_stats['templates'].setText(str(len(stats['skills'])))
            
            # Handle memory stats if available (from memory manager)
            if 'total_conversations' in stats:
                self.memory_stats['conversations'].setText(str(stats['total_conversations']))
            if 'total_messages' in stats:
                self.memory_stats['messages'].setText(str(stats['total_messages']))
            if 'total_words' in stats:
                self.memory_stats['words'].setText(str(stats['total_words']))
            if 'total_templates' in stats:
                self.memory_stats['templates'].setText(str(stats['total_templates']))
                
        except Exception as e:
            logger.error(f"Error updating stats display: {e}")
            # Set default values on error
            for stat_label in self.memory_stats.values():
                stat_label.setText("0")
    
    def update_player_info(self, player: 'Player'):
        """Update player information display."""
        self.player_info.setText(f"{player.name} - {player.architect_tier}")
        
        # Calculate progress percentage
        progress = (player.xp / player.get_next_level_xp()) * 100
        self.xp_progress.setValue(int(progress))
        self.xp_label.setText(f"{player.xp} / {player.get_next_level_xp()} XP")
    
    def update_skills(self, skills: list):
        """Update the skills display."""
        try:
            # Ensure skills is a list
            if not isinstance(skills, list):
                logger.warning(f"Expected list for skills, got {type(skills)}: {skills}")
                self.skills_label.setText("No skills available")
                return
            
            if skills:
                # Safely get skill names, handling both dict and object access
                skill_names = []
                for skill in skills[:3]:  # Limit to first 3 skills
                    if isinstance(skill, dict):
                        skill_name = skill.get('name', 'Unknown')
                    elif hasattr(skill, 'name'):
                        skill_name = getattr(skill, 'name', 'Unknown')
                    else:
                        skill_name = str(skill)
                    skill_names.append(skill_name)
                
                self.skills_label.setText(", ".join(skill_names))
            else:
                self.skills_label.setText("No skills available")
                
        except Exception as e:
            logger.error(f"Error updating skills display: {e}")
            self.skills_label.setText("Error loading skills")
    
    def start_live_processing(self):
        """Start live conversation processing."""
        try:
            from core.live_processor import get_live_processor
            live_proc = get_live_processor()
            
            if not live_proc:
                QMessageBox.warning(self, "Live Processor", "Live processor not initialized")
                return
            
            if not live_proc.is_configured():
                QMessageBox.warning(self, "Live Processor", "ChatGPT API not configured. Please set OPENAI_API_KEY environment variable.")
                return
            
            # Start processing
            if live_proc.start():
                self.live_status_label.setText("Status: Running")
                self.live_status_label.setStyleSheet("font-weight: bold; color: #00ff00;")
                self.start_live_btn.setEnabled(False)
                self.stop_live_btn.setEnabled(True)
                
                # Set up status callback
                live_proc.add_status_callback(self.on_live_status_change)
                live_proc.add_progress_callback(self.on_live_progress_update)
                
                QMessageBox.information(self, "Live Processor", "Live processing started successfully!")
            else:
                QMessageBox.critical(self, "Live Processor", "Failed to start live processing")
                
        except Exception as e:
            QMessageBox.critical(self, "Live Processor", f"Error starting live processing: {e}")
    
    def stop_live_processing(self):
        """Stop live conversation processing."""
        try:
            from core.live_processor import get_live_processor
            live_proc = get_live_processor()
            
            if live_proc:
                live_proc.stop()
                self.live_status_label.setText("Status: Stopped")
                self.live_status_label.setStyleSheet("font-weight: bold; color: #ff0000;")
                self.start_live_btn.setEnabled(True)
                self.stop_live_btn.setEnabled(False)
                
                QMessageBox.information(self, "Live Processor", "Live processing stopped")
                
        except Exception as e:
            QMessageBox.critical(self, "Live Processor", f"Error stopping live processing: {e}")
    
    def on_live_status_change(self, status):
        """Handle live processing status changes."""
        status_text = f"Status: {status.value.title()}"
        self.live_status_label.setText(status_text)
        
        if status.value == "monitoring":
            self.live_status_label.setStyleSheet("font-weight: bold; color: #00ff00;")
        elif status.value == "processing":
            self.live_status_label.setStyleSheet("font-weight: bold; color: #ffaa00;")
        elif status.value == "error":
            self.live_status_label.setStyleSheet("font-weight: bold; color: #ff0000;")
        elif status.value == "stopped":
            self.live_status_label.setStyleSheet("font-weight: bold; color: #888;")
            self.start_live_btn.setEnabled(True)
            self.stop_live_btn.setEnabled(False)
    
    def on_live_progress_update(self, current: int, total: int):
        """Handle live processing progress updates."""
        if total > 0:
            progress = (current / total) * 100
            stats_text = f"Processing: {current}/{total} ({progress:.1f}%)"
        else:
            stats_text = "Processing: Waiting for conversations..."
        
        self.live_stats_label.setText(stats_text)
    
    def update_live_stats(self):
        """Update live processing statistics."""
        try:
            from core.live_processor import get_live_processor
            live_proc = get_live_processor()
            
            if live_proc:
                stats = live_proc.get_stats()
                uptime = live_proc.get_uptime()
                
                stats_text = (
                    f"Total Processed: {stats.total_conversations_processed}\n"
                    f"Today: {stats.conversations_processed_today}\n"
                    f"Errors: {stats.errors_count}\n"
                    f"Avg Time: {stats.average_processing_time:.2f}s"
                )
                
                if uptime:
                    stats_text += f"\nUptime: {uptime}"
                
                self.live_stats_label.setText(stats_text)
                
                # Update button states
                if live_proc.get_status().value == "idle":
                    self.start_live_btn.setEnabled(live_proc.is_configured())
                    self.stop_live_btn.setEnabled(False)
                elif live_proc.get_status().value in ["monitoring", "processing"]:
                    self.start_live_btn.setEnabled(False)
                    self.stop_live_btn.setEnabled(True)
                
        except Exception as e:
            self.live_stats_label.setText(f"Error updating stats: {e}")
    
    def check_live_processor_status(self):
        """Check and update live processor status."""
        try:
            from core.live_processor import get_live_processor
            live_proc = get_live_processor()
            
            if live_proc:
                if live_proc.is_configured():
                    self.live_status_label.setText("Status: Ready")
                    self.live_status_label.setStyleSheet("font-weight: bold; color: #00aa00;")
                    self.start_live_btn.setEnabled(True)
                else:
                    self.live_status_label.setText("Status: Not Configured")
                    self.live_status_label.setStyleSheet("font-weight: bold; color: #888;")
                    self.start_live_btn.setEnabled(False)
                
                self.update_live_stats()
            else:
                self.live_status_label.setText("Status: Not Available")
                self.live_status_label.setStyleSheet("font-weight: bold; color: #888;")
                self.start_live_btn.setEnabled(False)
                self.stop_live_btn.setEnabled(False)
                
        except Exception as e:
            self.live_status_label.setText(f"Status: Error - {e}")
            self.live_status_label.setStyleSheet("font-weight: bold; color: #ff0000;") 