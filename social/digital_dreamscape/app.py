"""
Digital Dreamscape Chronicles - A GUI application for managing ChatGPT conversations.
"""
import sys
print("DEBUG: app.py - sys imported")
import os
print("DEBUG: app.py - os imported")
import json
print("DEBUG: app.py - json imported")
from datetime import datetime
from typing import List, Dict, Optional
print("DEBUG: app.py - typing imported")
import asyncio
from pathlib import Path

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QListWidget, QListWidgetItem, QSplitter,
        QTextEdit, QMessageBox, QProgressBar, QComboBox, QCheckBox,
        QFileDialog, QStatusBar, QLineEdit
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
    from PyQt6.QtGui import QIcon, QFont, QPixmap
    print("DEBUG: app.py - PyQt6 imported successfully")
except ImportError as e:
    print(f"FATAL ERROR: Failed to import PyQt6 - {e}")
    sys.exit(1)

try:
    from ..utils.chatgpt_scraper import ChatGPTScraper
    print("DEBUG: app.py - ChatGPTScraper imported successfully")
except ImportError as e:
    print(f"FATAL ERROR: Failed to import ChatGPTScraper - {e}")
    sys.exit(1)
except Exception as e:
    print(f"FATAL ERROR: Unexpected error importing ChatGPTScraper - {type(e).__name__}: {e}")
    sys.exit(1)

# Add basic logging setup for config utils
import logging
logger = logging.getLogger("DigitalDreamscapeApp")
# Configure logging minimally if not done elsewhere
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

print("DEBUG: app.py - Imports completed, defining classes...")


class ChatScraperWorker(QThread):
    """Worker thread for running the ChatGPT scraper."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, model: str = "", username: Optional[str] = None, password: Optional[str] = None):
        super().__init__()
        self.model = model
        self.username = username
        self.password = password
        
    def run(self):
        """Executes the scraper logic, handling the async run_scraper method."""
        scraper = None # Define scraper outside try block for potential cleanup
        try:
            # Instantiate the scraper
            scraper = ChatGPTScraper(username=self.username, password=self.password)
            # __enter__ (setup_browser) will be called implicitly by run_scraper now via asyncio.to_thread

            self.progress.emit(25) # Initial progress

            # Run the async scraper method using asyncio.run()
            # This blocks the thread until the async method completes
            success = asyncio.run(scraper.run_scraper(
                model_append=f"?model={self.model}" if self.model else "",
                output_file="temp_chats.json"
            ))

            if not success:
                self.error.emit("Failed to scrape chats (scraper returned False)")
                # Cleanup might be handled in run_scraper's finally block
                return

            self.progress.emit(75) # Progress after successful scrape

            # Load the scraped chats (sync file I/O okay in thread)
            try:
                with open("temp_chats.json", "r") as f:
                    chats = json.load(f)
            except FileNotFoundError:
                 logger.warning("temp_chats.json not found after scraping.")
                 chats = [] # Assume no chats if file missing
            except json.JSONDecodeError as e:
                 logger.error(f"Error decoding temp_chats.json: {e}")
                 self.error.emit("Failed to read scraped chat data.")
                 return
                 
            # Cleanup temporary file
            try:
                if os.path.exists("temp_chats.json"):
                     os.remove("temp_chats.json")
            except OSError as e:
                 logger.warning(f"Could not remove temp_chats.json: {e}")

            self.progress.emit(100) # Final progress
            self.finished.emit(chats)

        except Exception as e:
            # Log the exception with traceback for better debugging
            logger.error("Error in ChatScraperWorker run method", exc_info=True)
            print(f"ERROR in ChatScraperWorker.run: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self.error.emit(f"Worker thread error: {str(e)}")
        # finally:
            # Ensure cleanup happens even on error
            # if scraper: 
            #     asyncio.run(asyncio.to_thread(scraper.cleanup)) # Run cleanup if needed (run_scraper finally should handle this)

print("DEBUG: app.py - ChatScraperWorker defined")


class DigitalDreamscapeWindow(QMainWindow):
    """Main window for the Digital Dreamscape Chronicles application."""

    CONFIG_FILE_NAME = ".digital_dreamscape_config.json"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Dreamscape Chronicles")
        self.setMinimumSize(1200, 800)
        
        self.init_ui()
        
        # Initialize data
        self.chats = []
        self.selected_chats = set()
        
        # Load saved credentials after UI is initialized
        self._load_and_apply_credentials()
        
    def _get_config_path(self) -> Path:
        """Gets the path to the configuration file in the user's home directory."""
        return Path.home() / self.CONFIG_FILE_NAME

    def _load_credentials(self) -> tuple[Optional[str], Optional[str]]:
        """Loads credentials from the config file."""
        config_path = self._get_config_path()
        if not config_path.exists():
            return None, None
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            creds = config_data.get("credentials", {})
            username = creds.get("username")
            password = creds.get("password") # Load password directly
            logger.info(f"Loaded credentials from {config_path}")
            return username, password
        except (json.JSONDecodeError, IOError, Exception) as e:
            logger.error(f"Failed to load credentials from {config_path}: {e}")
            return None, None
            
    def _load_and_apply_credentials(self):
        """Loads credentials and applies them to the UI."""
        username, password = self._load_credentials()
        if username:
            self.email_input.setText(username)
        if password:
            self.password_input.setText(password)
            self.save_creds_cb.setChecked(True) # Check the box if password was loaded
        else:
             self.save_creds_cb.setChecked(False)

    def _save_credentials(self, username: str, password: str):
        """Saves credentials to the config file."""
        if not username: # Don't save if username is empty
             return
             
        config_path = self._get_config_path()
        config_data = {}
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
            except (json.JSONDecodeError, IOError, Exception) as e:
                logger.warning(f"Could not read existing config file {config_path} before saving: {e}")

        config_data["credentials"] = {"username": username, "password": password}

        try:
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            logger.info(f"Saved credentials to {config_path}")
        except (IOError, Exception) as e:
            logger.error(f"Failed to save credentials to {config_path}: {e}")
            QMessageBox.warning(self, "Save Failed", f"Could not save credentials:\n{e}")

    def _delete_credentials(self):
        """Removes credentials from the config file."""
        config_path = self._get_config_path()
        if not config_path.exists():
            return # Nothing to delete
            
        config_data = {}
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)

            if "credentials" in config_data:
                del config_data["credentials"]
                logger.info(f"Removed credentials section from {config_path}")
            else:
                 logger.info(f"No credentials section found in {config_path} to delete.")
                 return # No changes needed

            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            logger.info(f"Config file updated after deleting credentials.")

        except (json.JSONDecodeError, IOError, Exception) as e:
            logger.error(f"Failed to update config file after deleting credentials: {e}")
            # Optionally notify user

    def init_ui(self):
        """Initialize the user interface."""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create header
        header_layout = QHBoxLayout()
        title_label = QLabel("Digital Dreamscape Chronicles")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch(1) # Push controls to the right
        
        # Add login credentials
        login_group_layout = QHBoxLayout()
        login_group_layout.addWidget(QLabel("ChatGPT Email:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email...")
        login_group_layout.addWidget(self.email_input)
        
        login_group_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password...")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        login_group_layout.addWidget(self.password_input)
        
        # Add Save Credentials checkbox
        self.save_creds_cb = QCheckBox("Save")
        self.save_creds_cb.setToolTip("Save email and password locally (insecurely)")
        login_group_layout.addWidget(self.save_creds_cb)
        
        header_layout.addLayout(login_group_layout)
        header_layout.addSpacing(20)
        
        # Add model selector
        header_layout.addWidget(QLabel("Model:"))
        self.model_selector = QComboBox()
        self.model_selector.addItems(["", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"])
        self.model_selector.setCurrentText("")
        header_layout.addWidget(self.model_selector)
        
        # Add refresh button
        refresh_btn = QPushButton("Refresh Chats")
        refresh_btn.clicked.connect(self.refresh_chats)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Create splitter for chat list and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Chat list panel
        chat_panel = QWidget()
        chat_layout = QVBoxLayout(chat_panel)
        
        # Add chat list
        self.chat_list = QListWidget()
        self.chat_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.chat_list.itemSelectionChanged.connect(self.update_selection)
        chat_layout.addWidget(self.chat_list)
        
        # Add selection controls
        selection_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all_chats)
        clear_selection_btn = QPushButton("Clear Selection")
        clear_selection_btn.clicked.connect(self.clear_selection)
        selection_layout.addWidget(select_all_btn)
        selection_layout.addWidget(clear_selection_btn)
        chat_layout.addLayout(selection_layout)
        
        splitter.addWidget(chat_panel)
        
        # Preview panel
        preview_panel = QWidget()
        preview_layout = QVBoxLayout(preview_panel)
        
        preview_label = QLabel("Preview")
        preview_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        preview_layout.addWidget(preview_label)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        splitter.addWidget(preview_panel)
        
        main_layout.addWidget(splitter)
        
        # Add export controls
        export_layout = QHBoxLayout()
        export_selected_btn = QPushButton("Export Selected")
        export_selected_btn.clicked.connect(self.export_selected)
        export_layout.addWidget(export_selected_btn)
        
        self.include_content_cb = QCheckBox("Include Chat Content")
        export_layout.addWidget(self.include_content_cb)
        
        main_layout.addLayout(export_layout)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
    def refresh_chats(self):
        """Refresh the chat list using the scraper."""
        # Get credentials from input fields
        username = self.email_input.text().strip()
        password = self.password_input.text() # Get password (don't strip)

        # Check checkbox state *after* getting credentials
        save_credentials = self.save_creds_cb.isChecked()

        # Handle saving/deleting based on checkbox
        if save_credentials:
            if username:
                self._save_credentials(username, password)
            else:
                 # Maybe warn user they need to enter email to save?
                 logger.warning("Save credentials checked, but email is empty.")
        else:
            self._delete_credentials()

        # --- Validation before starting worker --- 
        if not username:
            QMessageBox.warning(self, "Input Required", "Please enter your ChatGPT email.")
            return
        # If not saving, password could be empty if user relies on cookies/manual login
        # if not password and not save_credentials: # Or maybe always require password if not saving?
            # QMessageBox.warning(self, "Input Required", "Please enter your ChatGPT password.")
            # return
        # --- End Validation --- 
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Create and start worker thread, passing credentials
        self.worker = ChatScraperWorker(
            model=self.model_selector.currentText(),
            username=username,
            password=password
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.update_chat_list)
        self.worker.error.connect(self.show_error)
        self.worker.start()
        
    def update_progress(self, value: int):
        """Update the progress bar."""
        self.progress_bar.setValue(value)
        
    def update_chat_list(self, chats: List[Dict]):
        """Update the chat list with new data."""
        self.chats = chats
        self.chat_list.clear()
        
        for chat in chats:
            item = QListWidgetItem(chat["title"])
            item.setData(Qt.ItemDataRole.UserRole, chat)
            self.chat_list.addItem(item)
            
        self.status_bar.showMessage(f"Loaded {len(chats)} chats")
        self.progress_bar.setVisible(False)
        
    def show_error(self, message: str):
        """Show error message."""
        QMessageBox.critical(self, "Error", message)
        self.progress_bar.setVisible(False)
        
    def update_selection(self):
        """Update the preview based on selection."""
        selected_items = self.chat_list.selectedItems()
        self.selected_chats = {item.data(Qt.ItemDataRole.UserRole)["url"] for item in selected_items}
        
        preview_text = f"Selected {len(selected_items)} chats:\n\n"
        for item in selected_items:
            chat = item.data(Qt.ItemDataRole.UserRole)
            preview_text += f"• {chat['title']}\n"
            preview_text += f"  URL: {chat['url']}\n"
            if chat.get('timestamp'):
                preview_text += f"  Timestamp: {chat['timestamp']}\n"
            preview_text += "\n"
            
        self.preview_text.setText(preview_text)
        
    def select_all_chats(self):
        """Select all chats in the list."""
        self.chat_list.selectAll()
        
    def clear_selection(self):
        """Clear the current selection."""
        self.chat_list.clearSelection()
        
    def export_selected(self):
        """Export selected chats."""
        if not self.selected_chats:
            QMessageBox.warning(self, "Warning", "No chats selected")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Chats",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
            
        selected_data = [
            chat for chat in self.chats
            if chat["url"] in self.selected_chats
        ]
        
        try:
            with open(file_path, 'w') as f:
                json.dump(selected_data, f, indent=2)
            QMessageBox.information(
                self,
                "Success",
                f"Successfully exported {len(selected_data)} chats to {file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")

print("DEBUG: app.py - DigitalDreamscapeWindow defined")


def main():
    """Application entry point."""
    print("DEBUG: app.py - main() called")
    try:
        print("DEBUG: app.py - Creating QApplication...")
        app = QApplication(sys.argv)
        print("DEBUG: app.py - QApplication created")

        # Set application style
        app.setStyle("Fusion")

        print("DEBUG: app.py - Creating DigitalDreamscapeWindow...")
        window = DigitalDreamscapeWindow()
        print("DEBUG: app.py - DigitalDreamscapeWindow created")
        window.show()

        print("DEBUG: app.py - Starting app.exec()...")
        exit_code = app.exec()
        print(f"DEBUG: app.py - app.exec() finished with code {exit_code}")
        return exit_code
    except Exception as e:
        print(f"FATAL ERROR in main(): {type(e).__name__}: {e}")
        # Potentially log the exception trace here too
        return 1

if __name__ == "__main__":
    print("DEBUG: app.py - In __main__ block")
    exit_code = main()
    print(f"DEBUG: app.py - Exiting with code {exit_code}")
    sys.exit(exit_code) 