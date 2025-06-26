#!/usr/bin/env python3
"""
Test GUI Functionality
Tests all GUI components and functionality.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

def test_gui_imports():
    """Test that all GUI components can be imported."""
    print("🖥️ Testing GUI Imports...")
    
    try:
        # Test main window import
        from gui.main_window import TheaMainWindow
        print("  [OK] Main window import successful")
        
        # Test panel imports
        from gui.panels.dashboard_panel import DashboardPanel
        from gui.panels.conversations_panel import ConversationsPanel
        from gui.panels.templates_panel import TemplatesPanel
        from gui.panels.multi_model_panel import MultiModelPanel
        from gui.panels.settings_panel import SettingsPanel
        
        print("  [OK] All panel imports successful")
        
        # Test settings sub-panels
        from gui.panels.settings.general_settings import GeneralSettings
        from gui.panels.settings.api_settings import APISettings
        from gui.panels.settings.memory_settings import MemorySettings
        
        print("  [OK] All settings panel imports successful")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] GUI import test failed: {e}")
        return False

def test_gui_initialization():
    """Test that GUI can be initialized."""
    print("🚀 Testing GUI Initialization...")
    
    try:
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Test main window creation
        from gui.main_window import TheaMainWindow
        window = TheaMainWindow()
        
        print("  [OK] Main window created successfully")
        print(f"  [OK] Window title: {window.windowTitle()}")
        print(f"  [OK] Window size: {window.size().width()}x{window.size().height()}")
        
        # Test panel access
        print(f"  [OK] Dashboard panel: {type(window.dashboard_panel).__name__}")
        print(f"  [OK] Conversations panel: {type(window.conversations_panel).__name__}")
        print(f"  [OK] Templates panel: {type(window.templates_panel).__name__}")
        print(f"  [OK] Settings panel: {type(window.settings_panel).__name__}")
        
        # Test system initialization
        print(f"  [OK] Memory manager: {type(window.memory_manager).__name__}")
        print(f"  [OK] Memory API: {type(window.memory_api).__name__}")
        print(f"  [OK] MMORPG Engine: {type(window.mmorpg_engine).__name__}")
        print(f"  [OK] Dreamscape Memory: {type(window.dreamscape_memory).__name__}")
        print(f"  [OK] Discord Manager: {type(window.discord_manager).__name__}")
        
        # Clean up
        window.close()
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] GUI initialization test failed: {e}")
        return False

def test_theme_system():
    """Test the theme switching system."""
    print("🎨 Testing Theme System...")
    
    try:
        app = QApplication(sys.argv)
        from gui.main_window import TheaMainWindow
        window = TheaMainWindow()
        
        # Test theme methods
        initial_theme = window.get_current_theme()
        print(f"  [OK] Initial theme: {initial_theme}")
        
        # Test theme switching
        window.switch_theme("Light")
        light_theme = window.get_current_theme()
        print(f"  [OK] Light theme applied: {light_theme}")
        
        window.switch_theme("Dark")
        dark_theme = window.get_current_theme()
        print(f"  [OK] Dark theme applied: {dark_theme}")
        
        # Test system theme
        window.switch_theme("System")
        system_theme = window.get_current_theme()
        print(f"  [OK] System theme applied: {system_theme}")
        
        # Clean up
        window.close()
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Theme system test failed: {e}")
        return False

def test_panel_functionality():
    """Test panel functionality."""
    print("📋 Testing Panel Functionality...")
    
    try:
        app = QApplication(sys.argv)
        
        # Test dashboard panel
        from gui.panels.dashboard_panel import DashboardPanel
        dashboard = DashboardPanel()
        print("  [OK] Dashboard panel created")
        
        # Test conversations panel
        from gui.panels.conversations_panel import ConversationsPanel
        conversations = ConversationsPanel()
        print("  [OK] Conversations panel created")
        
        # Test templates panel
        from gui.panels.templates_panel import TemplatesPanel
        templates = TemplatesPanel()
        print("  [OK] Templates panel created")
        
        # Test multi-model panel
        from gui.panels.multi_model_panel import MultiModelPanel
        multi_model = MultiModelPanel()
        print("  [OK] Multi-model panel created")
        
        # Test settings panel
        from gui.panels.settings_panel import SettingsPanel
        settings = SettingsPanel()
        print("  [OK] Settings panel created")
        
        # Test settings sub-panels
        from gui.panels.settings.general_settings import GeneralSettings
        from gui.panels.settings.api_settings import APISettings
        from gui.panels.settings.memory_settings import MemorySettings
        
        general = GeneralSettings()
        api = APISettings()
        memory = MemorySettings()
        
        print("  [OK] All settings sub-panels created")
        
        # Clean up
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Panel functionality test failed: {e}")
        return False

def test_core_integration():
    """Test core system integration with GUI."""
    print("🔗 Testing Core Integration...")
    
    try:
        app = QApplication(sys.argv)
        from gui.main_window import TheaMainWindow
        window = TheaMainWindow()
        
        # Test memory API integration
        stats = window.memory_api.get_memory_stats()
        print(f"  [OK] Memory stats retrieved: {stats.get('total_conversations', 0)} conversations")
        
        # Test MMORPG engine integration
        player = window.mmorpg_engine.get_player()
        print(f"  [OK] Player info retrieved: {player.name} - {player.architect_tier}")
        
        # Test skills retrieval
        skills = window.mmorpg_engine.get_skills()
        print(f"  [OK] Skills retrieved: {len(skills)} skills")
        
        # Test dreamscape memory
        state = window.dreamscape_memory.get_current_memory_state()
        print(f"  [OK] Dreamscape state retrieved: {state.get('architect_tier', 'Unknown')}")
        
        # Test conversations retrieval
        conversations = window.memory_api.get_conversations_chronological(limit=5)
        print(f"  [OK] Conversations retrieved: {len(conversations)} conversations")
        
        # Clean up
        window.close()
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Core integration test failed: {e}")
        return False

def main():
    """Run all GUI tests."""
    print("🖥️ GUI Functionality Test Suite")
    print("=" * 50)
    
    tests = [
        test_gui_imports,
        test_gui_initialization,
        test_theme_system,
        test_panel_functionality,
        test_core_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All GUI tests passed! GUI functionality is working correctly.")
        return True
    else:
        print("⚠️ Some GUI tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 