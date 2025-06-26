# Theme System for Dream.OS GUI

## Overview

The Dream.OS GUI now features a comprehensive theme system with **dark mode** support and **runtime theme switching**. The system provides a modern, professional appearance that adapts to user preferences and maintains consistency across all components.

## Features

### 🎨 **Theme Options**
- **Dark Mode**: Professional dark theme with VS Code-inspired colors
- **Light Mode**: Clean light theme with modern styling
- **System Theme**: Follows OS theme preferences (future enhancement)

### 🔄 **Runtime Switching**
- **Sidebar Button**: Quick theme toggle button in the sidebar
- **Settings Panel**: Theme dropdown in General Settings
- **Instant Application**: Themes apply immediately without restart

### 🎯 **Comprehensive Styling**
- **All Components**: Buttons, tables, forms, text areas, etc.
- **Navigation**: Sidebar, menus, tabs, scrollbars
- **Interactive Elements**: Hover effects, focus states, selections
- **Consistent Colors**: Professional color palette throughout

## Implementation Details

### Theme Architecture

```python
# Main theme system in gui/main_window.py
class TheaMainWindow(QMainWindow):
    def apply_theme(self, theme: str):
        """Apply a specific theme to the application."""
        if theme == 'Dark':
            self.apply_dark_theme()
        elif theme == 'Light':
            self.apply_light_theme()
        else:  # System theme
            self.apply_system_theme()
    
    def switch_theme(self, theme: str):
        """Switch to a different theme at runtime."""
        self.apply_theme(theme)
        self.update_theme_switcher_text(theme)
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        current_theme = self.get_current_theme()
        new_theme = "Light" if current_theme == "Dark" else "Dark"
        self.switch_theme(new_theme)
```

### Settings Integration

```python
# Theme setting in gui/panels/settings/general_settings.py
class GeneralSettingsWidget(QWidget):
    def init_ui(self):
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        self.theme_combo.setCurrentText("Dark")  # Default to dark
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
    
    def _on_theme_changed(self):
        """Handle theme changes specifically."""
        theme = self.theme_combo.currentText()
        self.theme_changed.emit(theme)
```

### Signal Connections

```python
# Connect theme changes in main window
def setup_connections(self):
    # Connect theme changes from settings
    self.settings_panel.general_settings.theme_changed.connect(self.switch_theme)
```

## Dark Theme Colors

### Primary Colors
- **Background**: `#1e1e1e` (Main window)
- **Sidebar**: `#252526` (Navigation area)
- **Content**: `#2d2d30` (Alternate rows, headers)
- **Borders**: `#3e3e42` (Dividers, frames)

### Text Colors
- **Primary Text**: `#cccccc` (Main content)
- **Secondary Text**: `#6a6a6a` (Disabled elements)
- **White Text**: `#ffffff` (High contrast areas)

### Interactive Elements
- **Primary Button**: `#0e639c` (Main actions)
- **Button Hover**: `#1177bb` (Hover state)
- **Button Pressed**: `#0c5a8b` (Active state)
- **Selection**: `#094771` (Selected items)

### Form Elements
- **Input Background**: `#3c3c3c` (Text fields, dropdowns)
- **Input Border**: `#3e3e42` (Default state)
- **Input Focus**: `#007acc` (Focused state)
- **Checkbox**: `#007acc` (Checked state)

## Light Theme Colors

### Primary Colors
- **Background**: `#f5f5f5` (Main window)
- **Sidebar**: `#ffffff` (Navigation area)
- **Content**: `#f9f9f9` (Alternate rows)
- **Borders**: `#ddd` (Dividers, frames)

### Text Colors
- **Primary Text**: `#333333` (Main content)
- **Secondary Text**: `#666666` (Disabled elements)
- **White Text**: `#ffffff` (High contrast areas)

### Interactive Elements
- **Primary Button**: `#0078d4` (Main actions)
- **Button Hover**: `#106ebe` (Hover state)
- **Button Pressed**: `#005a9e` (Active state)
- **Selection**: `#0078d4` (Selected items)

### Form Elements
- **Input Background**: `#ffffff` (Text fields, dropdowns)
- **Input Border**: `#ddd` (Default state)
- **Input Focus**: `#0078d4` (Focused state)
- **Checkbox**: `#0078d4` (Checked state)

## Usage

### Quick Theme Toggle
1. **Sidebar Button**: Click the theme switcher button in the sidebar
   - Shows "🌙 Dark Mode" when in light mode
   - Shows "☀️ Light Mode" when in dark mode

### Settings Panel
1. **Navigate**: Go to Settings → General
2. **Theme Dropdown**: Select from Light, Dark, or System
3. **Apply**: Theme changes immediately

### Programmatic Control
```python
# Switch to specific theme
window.switch_theme("Dark")

# Toggle between light/dark
window.toggle_theme()

# Get current theme
current_theme = window.get_current_theme()
```

## CSS Styling

### Component-Specific Styling
The theme system uses comprehensive CSS styling for all components:

```css
/* Navigation buttons */
QPushButton[class="nav"] {
    background-color: transparent;
    color: #cccccc;  /* Dark theme */
    text-align: left;
    padding: 10px 15px;
    border-radius: 0px;
    font-weight: normal;
}
QPushButton[class="nav"]:hover {
    background-color: #2a2d2e;  /* Dark theme */
}
QPushButton[class="nav"]:checked {
    background-color: #37373d;  /* Dark theme */
    color: #ffffff;
}

/* Tables */
QTableWidget {
    background-color: #252526;  /* Dark theme */
    alternate-background-color: #2d2d30;
    color: #cccccc;
    gridline-color: #3e3e42;
    border: 1px solid #3e3e42;
}
QTableWidget::item:selected {
    background-color: #094771;
    color: #ffffff;
}
```

### Responsive Design
- **Hover Effects**: All interactive elements have hover states
- **Focus States**: Form elements show focus indicators
- **Selection States**: Tables and lists show selection clearly
- **Disabled States**: Disabled elements are visually distinct

## Testing

### Automated Testing
Run the theme switching test:

```bash
python test_theme_switching.py
```

### Manual Testing
1. **Start GUI**: `python -m gui.main_window`
2. **Test Sidebar Button**: Click theme switcher in sidebar
3. **Test Settings**: Go to Settings → General → Theme dropdown
4. **Verify Components**: Check all panels and elements

### Test Coverage
- ✅ Initial theme detection
- ✅ Theme switching functionality
- ✅ Theme toggle functionality
- ✅ Theme switcher button updates
- ✅ Settings panel integration
- ✅ All UI components styled
- ✅ Hover and focus states
- ✅ Selection states

## Benefits

### 1. **User Experience**
- **Eye Comfort**: Dark mode reduces eye strain
- **Professional Appearance**: Modern, polished interface
- **Consistency**: Unified styling across all components
- **Accessibility**: High contrast and clear states

### 2. **Developer Experience**
- **Maintainable**: Centralized theme system
- **Extensible**: Easy to add new themes
- **Testable**: Comprehensive test coverage
- **Documented**: Clear implementation guide

### 3. **Performance**
- **Instant Switching**: No restart required
- **Efficient CSS**: Optimized stylesheets
- **Memory Efficient**: No image resources needed

## Future Enhancements

### 1. **System Theme Detection**
```python
def apply_system_theme(self):
    """Detect and apply OS theme preference."""
    # Detect OS dark mode setting
    # Apply appropriate theme automatically
```

### 2. **Custom Themes**
```python
def load_custom_theme(self, theme_file: str):
    """Load theme from external CSS file."""
    # Support for user-defined themes
    # Theme marketplace integration
```

### 3. **Theme Persistence**
```python
def save_theme_preference(self, theme: str):
    """Save theme preference to configuration."""
    # Persist theme choice across sessions
    # Sync with cloud settings
```

### 4. **Animation Support**
```css
/* Smooth theme transitions */
QMainWindow {
    transition: background-color 0.3s ease;
}
```

## Configuration

### Default Settings
```python
DEFAULT_THEME = "Dark"
AVAILABLE_THEMES = ["Light", "Dark", "System"]
THEME_PERSISTENCE = True
ANIMATION_ENABLED = False
```

### Customization
Users can customize themes by:
1. **Settings Panel**: Change theme via GUI
2. **Configuration File**: Edit theme settings directly
3. **CSS Override**: Add custom CSS for specific components

## Conclusion

The Dream.OS theme system provides a professional, user-friendly interface with comprehensive dark mode support. The runtime switching capability ensures users can adapt the interface to their preferences instantly, while the consistent styling maintains a polished appearance across all components.

The system is designed to be maintainable, extensible, and thoroughly tested, providing both excellent user experience and developer productivity. 