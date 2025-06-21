# Digital Dreamscape - Standalone Project

A clean, standalone extraction of working components from the Dream.OS project.

## 🎯 What's Working (Validated)

### ✅ Core Components
- **Template Engine**: Jinja2-based template rendering system
- **ChatGPT Scraper**: Automated ChatGPT conversation extraction
- **Digital Dreamscape GUI**: PyQt6-based interface for managing conversations
- **Social Media Tools**: Basic automation and scraping capabilities

### ✅ Architecture
- **Modular Design**: Clean separation of concerns
- **Error Handling**: Robust error recovery and logging
- **Configuration**: Environment-based configuration management
- **Testing**: Basic test framework with working tests

## 📁 Project Structure

```
dreamscape_standalone/
├── core/
│   ├── template_engine.py      # Jinja2 template rendering
│   ├── config.py              # Configuration management
│   └── utils/
│       ├── logger.py          # Logging utilities
│       └── helpers.py         # Common helper functions
├── scrapers/
│   ├── chatgpt_scraper.py     # ChatGPT conversation scraper
│   └── social_scraper.py      # Social media scraping tools
├── gui/
│   ├── main_window.py         # Main application window
│   ├── components/            # UI components
│   └── styles/               # UI styling
├── tests/
│   ├── test_template_engine.py
│   ├── test_scrapers.py
│   └── test_gui.py
├── requirements.txt
├── setup.py
└── README.md
```

## 🚀 Quick Start

### Installation
```bash
# Clone or extract the standalone project
cd dreamscape_standalone

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Application
```bash
# Start the GUI application
python gui/main_window.py

# Or run individual components
python core/template_engine.py  # Test template engine
python scrapers/chatgpt_scraper.py  # Test scraper
```

### Run Tests
```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_template_engine.py
pytest tests/test_scrapers.py
```

## 💡 Usage Examples

### Using Undetected ChromeDriver
```python
from scrapers.chatgpt_scraper import ChatGPTScraper

# Initialize with undetected-chromedriver (recommended)
scraper = ChatGPTScraper(
    headless=False,  # Set to True for headless mode
    timeout=30,
    use_undetected=True  # Enable anti-detection
)

# Use context manager for automatic cleanup
with scraper:
    if scraper.navigate_to_chatgpt():
        if scraper.is_logged_in():
            conversations = scraper.get_conversation_list()
            print(f"Found {len(conversations)} conversations")
```

### Running Examples
```bash
# Test undetected-chromedriver functionality
python main.py undetected_chrome

# Run scraping example
python examples/undetected_chrome_example.py scrape

# Compare regular vs undetected modes
python examples/undetected_chrome_example.py compare

# Run complete workflow demo (no browser required)
python examples/complete_scraping_workflow.py demo

# Run complete workflow (requires ChatGPT login)
python examples/complete_scraping_workflow.py full
```

## 🔧 Core Features

### Template Engine
- **Jinja2 Integration**: Full Jinja2 template support
- **Error Handling**: Graceful error recovery
- **Custom Filters**: Extensible filter system
- **File System Loading**: Template discovery and loading

### ChatGPT Scraper
- **Automated Scraping**: Extract conversation history
- **Cookie Management**: Persistent login sessions
- **Multi-Model Support**: GPT-3.5, GPT-4, etc.
- **Export Formats**: JSON, CSV, Markdown
- **Anti-Detection**: Undetected-chromedriver support for enhanced stealth
- **Conversation Entry**: Navigate to specific conversations
- **Templated Prompts**: Send Jinja2-templated prompts to ChatGPT
- **Response Extraction**: Capture and analyze ChatGPT responses
- **Complete Workflow**: Full pipeline from login to analysis

### Undetected ChromeDriver Support
- **Enhanced Stealth**: Bypass bot detection mechanisms
- **Automatic Fallback**: Graceful degradation to regular selenium
- **Configurable**: Toggle between undetected and regular modes
- **Browser Automation**: Improved success rates for web scraping
- **Anti-Detection Features**:
  - Removes webdriver properties
  - Disables automation flags
  - Masks automation indicators
  - Custom user agent handling

### GUI Application
- **Modern Interface**: PyQt6-based UI
- **Real-time Updates**: Live conversation monitoring
- **Export Tools**: Multiple export formats
- **Configuration**: User-friendly settings

## 📋 Requirements

- **Python**: 3.11+
- **PyQt6**: GUI framework
- **Selenium**: Web scraping
- **Jinja2**: Template engine
- **Requests**: HTTP client
- **BeautifulSoup**: HTML parsing

## 🎯 Use Cases

### Content Management
- Extract and organize ChatGPT conversations
- Generate reports from conversation history
- Create templates for content generation

### Social Media Automation
- Scrape social media content
- Generate automated responses
- Monitor conversation trends

### Development Tools
- Template-based code generation
- Automated testing frameworks
- Documentation generation

## 🔄 Migration from Dream.OS

This standalone project extracts the working components from the larger Dream.OS system:

1. **Template Engine**: From `core_bak/template_engine.py`
2. **ChatGPT Scraper**: From `social/utils/chatgpt_scraper.py`
3. **GUI Application**: From `social/digital_dreamscape/app.py`
4. **Configuration**: Simplified from complex Dream.OS config

### What's Excluded
- Broken agent coordination system
- Non-functional dashboard components
- Complex multi-agent architecture
- Unvalidated features

## 📊 Validation Status

### ✅ Working Components
- Template engine (4 tests pass)
- Basic scraper functionality
- GUI application startup
- Configuration management

### 🔄 Needs Testing
- End-to-end scraping workflows
- Template rendering with complex data
- GUI component interactions
- Export functionality

### ❌ Excluded (Broken)
- Agent coordination system
- Complex dashboard components
- Multi-agent communication
- Unvalidated features

## 🚀 Next Steps

### Immediate (Week 1)
1. **Extract Core Components**: Move working code to standalone structure
2. **Fix Dependencies**: Resolve import and path issues
3. **Validate Functionality**: Test all components end-to-end
4. **Documentation**: Complete setup and usage guides

### Short-term (Week 2-3)
1. **Enhance GUI**: Improve user experience
2. **Add Features**: Expand scraping capabilities
3. **Testing**: Comprehensive test coverage
4. **Packaging**: Create distributable package

### Long-term (Month 2+)
1. **Plugin System**: Extensible architecture
2. **Cloud Integration**: Remote data storage
3. **Advanced Analytics**: Conversation analysis
4. **API Development**: RESTful API interface

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Test** your changes thoroughly
4. **Submit** a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Digital Dreamscape Standalone** - Clean, working components extracted from Dream.OS 