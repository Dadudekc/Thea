# Thea - Digital Dreamscape Platform

**Thea** is a powerful ChatGPT conversation management and analysis platform that transforms raw conversation data into actionable insights. Built with a clean, modular architecture, Thea provides enterprise-grade tools for conversation extraction, template-based content generation, and intelligent analysis.

## 🎯 **What Thea Does**

### **Core Capabilities**
- **🤖 ChatGPT Integration**: Automated conversation extraction with anti-detection
- **📝 Template Engine**: Dynamic content generation using Jinja2 templates
- **🖥️ Modern GUI**: PyQt6-based interface for conversation management
- **💾 Data Management**: Local storage with export capabilities
- **🔍 Analysis Tools**: Conversation insights and pattern recognition

### **Key Features**
- **Undetected Scraping**: Bypass bot detection with advanced ChromeDriver
- **Template System**: Create dynamic prompts and content with Jinja2
- **Export Formats**: JSON, CSV, Markdown, and custom formats
- **Real-time Monitoring**: Live conversation tracking and analysis
- **Modular Architecture**: Extensible design for custom integrations

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.11+
- Chrome browser (for scraping)
- Git

### **Installation**
```bash
# Clone the repository
git clone https://github.com/Dadudekc/Thea.git
cd Thea

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env.example .env
# Edit .env with your ChatGPT credentials
```

### **Running Thea**
```bash
# Start the GUI application
python main.py

# Or run specific components
python main.py test          # Run all tests
python main.py scrape        # Test scraping functionality
python main.py template      # Test template engine

# List CLI tools stored in the new Tools Database
# (This does not load the GUI or any heavy modules)
dreamos tools list
```

## 📁 **Project Structure**

```
Thea/
├── core/                    # Core framework
│   ├── template_engine.py   # Jinja2 template system
│   ├── config.py           # Configuration management
│   ├── memory_manager.py   # Data persistence
│   └── models.py           # Data models
├── scrapers/               # Web scraping tools
│   ├── chatgpt_scraper.py  # ChatGPT conversation extractor
│   └── devlog_generator.py # Development log generator
├── gui/                    # User interface
│   └── main_window.py      # Main application window
├── tests/                  # Test suite
│   ├── test_template_engine.py
│   ├── test_chatgpt_scraper.py
│   └── test_memory_nexus.py
├── templates/              # Template files
├── docs/                   # Documentation
├── examples/               # Usage examples
└── main.py                 # Application entry point
```

## 🔧 **Core Components**

### **Template Engine**
The heart of Thea's content generation system, built on Jinja2:
```python
from core.template_engine import TemplateEngine

engine = TemplateEngine()
template = """
Hello {{ user.name }}!
Your conversation count: {{ stats.conversations }}
Last activity: {{ stats.last_activity }}
"""

context = {
    "user": {"name": "Alice"},
    "stats": {"conversations": 42, "last_activity": "2024-01-15"}
}

result = engine.render(template, context)
```

### **ChatGPT Scraper**
Advanced conversation extraction with anti-detection:
```python
from scrapers.chatgpt_scraper import ChatGPTScraper

scraper = ChatGPTScraper(
    headless=False,
    use_undetected=True,  # Anti-detection mode
    timeout=30
)

with scraper:
    if scraper.navigate_to_chatgpt():
        conversations = scraper.get_conversation_list()
        for conv in conversations:
            content = scraper.extract_conversation(conv['id'])
            print(f"Extracted: {len(content)} messages")
```

### **GUI Application**
Modern PyQt6 interface for conversation management:
```bash
python main.py
# Opens the main application window with:
# - Conversation browser
# - Template editor
# - Analysis dashboard
# - Export tools
```

## 📊 **Use Cases**

### **Content Creators**
- Extract ChatGPT conversations for content analysis
- Generate dynamic content using templates
- Track conversation patterns and insights
- Export data for further processing

### **Researchers**
- Analyze conversation patterns and trends
- Extract structured data from conversations
- Generate reports and visualizations
- Study AI interaction patterns

### **Developers**
- Build custom conversation analysis tools
- Integrate ChatGPT data into applications
- Create automated content generation systems
- Develop AI-powered workflows

### **Business Users**
- Monitor customer service conversations
- Analyze support ticket patterns
- Generate automated reports
- Track conversation quality metrics

## 🛠️ **Technical Stack**

### **Core Technologies**
- **Python 3.11+**: Modern Python with type hints
- **PyQt6**: Cross-platform GUI framework
- **Selenium**: Web automation and scraping
- **Jinja2**: Template engine for dynamic content
- **SQLite**: Local data storage
- **pytest**: Testing framework

### **Key Dependencies**
- **undetected-chromedriver**: Anti-detection web scraping
- **python-dotenv**: Environment configuration
- **requests**: HTTP client library
- **beautifulsoup4**: HTML parsing

## 🧪 **Testing**

Thea includes comprehensive testing to ensure reliability:

```bash
# Run all tests
pytest tests/

# Run specific test suites
pytest tests/test_template_engine.py
pytest tests/test_chatgpt_scraper.py
pytest tests/test_memory_nexus.py

# Run with coverage
pytest --cov=core --cov=scrapers tests/
```

## 📈 **Performance**

### **Current Metrics**
- **Scraping Speed**: ~2-5 seconds per conversation
- **Template Rendering**: <100ms for complex templates
- **Memory Usage**: <200MB for typical usage
- **GUI Responsiveness**: <50ms for common operations

### **Scalability**
- **Conversation Storage**: Unlimited local storage
- **Template Complexity**: No practical limits
- **Export Formats**: Extensible format system
- **Concurrent Operations**: Thread-safe design

## 🔒 **Security & Privacy**

### **Data Protection**
- **Local Storage**: All data stored locally
- **No Cloud Dependencies**: Complete privacy control
- **Encrypted Configuration**: Secure credential storage
- **Audit Logging**: Track all operations

### **Anti-Detection**
- **Undetected ChromeDriver**: Bypass bot detection
- **Request Throttling**: Respect rate limits
- **User Agent Rotation**: Dynamic browser fingerprinting
- **Session Management**: Persistent login handling

## 🚀 **Development Roadmap**

### **Phase 1: Foundation** ✅ **Complete**
- ✅ Core template engine
- ✅ ChatGPT scraper with anti-detection
- ✅ Basic GUI interface
- ✅ Local data storage
- ✅ Testing framework

### **Phase 2: Enhancement** 🔄 **In Progress**
- 🔄 Advanced conversation analysis
- 🔄 Enhanced GUI features
- 🔄 Export format expansion
- 🔄 Performance optimization

### **Phase 3: Advanced Features** 📋 **Planned**
- 📋 Machine learning analysis
- 📋 Cloud integration options
- 📋 API development
- 📋 Plugin architecture

### **Phase 4: Enterprise** 📋 **Future**
- 📋 Multi-user support
- 📋 Advanced security features
- 📋 Enterprise integrations
- 📋 Professional support

## 🤝 **Contributing**

We welcome contributions! Thea is designed to be extensible and community-driven.

### **Getting Started**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### **Development Setup**
```bash
git clone https://github.com/Dadudekc/Thea.git
cd Thea
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
pre-commit install  # Install git hooks
```

### **Code Standards**
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive tests
- Update documentation for new features

## 📚 **Documentation**

- **[Roadmap](ROADMAP.md)**: Detailed development phases and plans
- **[Project Status](PROJECT_STATUS.md)**: Current project status and achievements
- **[Phase 2 Plan](PHASE_2_PLAN.md)**: Detailed Phase 2 implementation plan
- **[Examples](examples/)**: Usage examples and tutorials

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 **Support**

### **Getting Help**
- **Issues**: Report bugs and request features on GitHub
- **Discussions**: Ask questions and share ideas
- **Documentation**: Check the docs folder for detailed guides

### **Community**
- **Contributors**: Join our growing community
- **Examples**: Share your use cases and examples
- **Feedback**: Help shape the future of Thea

## 🛠️ Tools Database CLI
As of Phase&nbsp;3 we ship a lightweight **Tools Database** that stores reusable
utility scripts inside `data/tools.db`.  You can interact with those tools via
the Dream.OS Toolbelt without keeping the physical `.py` files around.

| Command | Description |
|---------|-------------|
| `dreamos tools list` | Show all available tools |
| `dreamos tools show <name>` | View a tool's source code pulled from the DB |
| `dreamos tools run <name> [-- <args>]` | Execute a tool dynamically |
| `dreamos tools ingest [--force]` | Import / refresh on-disk tools into the DB |
| `dreamos discord ids [--guild <id>]` | Print your guild and channel IDs for env setup |
| `dreamos discord set --interactive` | Fill or update the Discord env variables |

Environment variable `TOOLS_DB_PATH` (default `data/tools.db`) controls the
exact DB location.

> **Heads-up:** Phase 3 introduces a live Discord bot.  Copy `.env.example` → `.env`
> and fill in `DISCORD_BOT_TOKEN`, `DISCORD_APPLICATION_ID`, `DISCORD_GUILD_ID`,
> and `DISCORD_CHANNEL_*` variables (see `.env.example`) to enable bot commands through the `dreamos discord …`
> CLI group.

---

**Thea** - Transforming ChatGPT conversations into actionable insights.

**Built with ❤️ by the Thea community** 