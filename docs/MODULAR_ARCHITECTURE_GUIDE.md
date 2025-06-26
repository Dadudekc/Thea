# Modular Architecture Guide

## Overview

This guide explains the modular architecture of the Dream.OS scraper system, demonstrating how the `ScraperOrchestrator` provides a clean interface for both GUI and CLI components while maintaining the 300-350 LOC requirement.

## Architecture Principles

### 1. **Single Responsibility**
- Each module does one thing well
- No monolithic scripts
- Clear separation of concerns

### 2. **Reusability**
- All logic in one place
- Called by both GUI and CLI
- No code duplication

### 3. **LOC Discipline**
- Maximum 350 lines per file
- Average below 250 lines
- Concise, focused modules

### 4. **Professional Structure**
- Clean interfaces
- Proper error handling
- Comprehensive documentation

## Core Components

### 1. **ScraperOrchestrator** (`core/scraper_orchestrator.py`)
**Lines: ~350** - Central coordination point

```python
class ScraperOrchestrator:
    """Central orchestrator for ChatGPT scraping operations."""
    
    def __init__(self, headless: bool = False, use_undetected: bool = True):
        # Initialize all component managers
        self._initialize_components()
    
    def login_and_save_cookies(self, username: str, password: str) -> ScrapingResult:
        # Coordinate login process
    
    def extract_conversations(self, max_conversations: int) -> ScrapingResult:
        # Coordinate conversation extraction
    
    def extract_conversation_content(self, url: str) -> ScrapingResult:
        # Coordinate content extraction
    
    def generate_blog_post(self, conversations: List[ConversationData]) -> ScrapingResult:
        # Coordinate blog generation
```

**Key Features:**
- **Facade Pattern**: Hides complexity behind clean interface
- **Result Objects**: Consistent error handling and metadata
- **Thread Safety**: Safe for GUI and CLI usage
- **Resource Management**: Proper cleanup with context managers

### 2. **ScraperPanel** (`gui/panels/scraper_panel.py`)
**Lines: ~320** - GUI integration example

```python
class ScraperPanel(ttk.Frame):
    """GUI panel for ChatGPT scraping operations."""
    
    def __init__(self, parent, **kwargs):
        self.orchestrator: Optional[ScraperOrchestrator] = None
        self._setup_ui()
        self._setup_threading()
    
    def _login(self):
        # Handle login button click
        self.worker_thread = threading.Thread(target=self._login_worker)
    
    def _handle_thread_result(self, result_tuple):
        # Process results from worker threads
```

**Key Features:**
- **Threading**: Non-blocking GUI operations
- **Error Handling**: User-friendly error messages
- **Status Updates**: Real-time progress feedback
- **Resource Management**: Proper cleanup on destroy

### 3. **CLI Demo** (`scripts/scraper_cli_demo.py`)
**Lines: ~340** - Command-line integration example

```python
def main():
    parser = argparse.ArgumentParser(description="ChatGPT Scraper CLI Demo")
    
    # Commands: login, extract-conversations, generate-blog, etc.
    subparsers = parser.add_subparsers(dest="command")
    
    # Each command uses the orchestrator
    if args.command == "login":
        success = login_command(orchestrator, args.username, args.password)
```

**Key Features:**
- **Argument Parsing**: Clean CLI interface
- **Command Structure**: Modular command handlers
- **Workflow Support**: Complete end-to-end workflows
- **File Output**: Automatic content saving

## Integration Patterns

### 1. **GUI Integration**

```python
# In ScraperPanel
def _login(self):
    # Start background thread
    self.worker_thread = threading.Thread(target=self._login_worker)
    self.worker_thread.start()

def _login_worker(self, username: str, password: str):
    # Use orchestrator in background
    result = self.orchestrator.login_and_save_cookies(username, password)
    self.thread_queue.put(("login", result))
```

### 2. **CLI Integration**

```python
# In CLI script
def login_command(orchestrator: ScraperOrchestrator, username: str, password: str):
    result = orchestrator.login_and_save_cookies(username, password)
    if result.success:
        print(f"✅ Login successful via {result.metadata['method']}")
    else:
        print(f"❌ Login failed: {result.error}")
```

### 3. **Error Handling**

```python
# Consistent across GUI and CLI
@dataclass
class ScrapingResult:
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None
```

## Data Flow

### 1. **Login Flow**
```
User Input → GUI/CLI → Orchestrator → LoginHandler → CookieManager
                ↓
            Result Object → GUI/CLI → User Feedback
```

### 2. **Extraction Flow**
```
User Request → GUI/CLI → Orchestrator → ConversationListManager
                ↓
            ConversationData[] → GUI/CLI → Display Results
```

### 3. **Generation Flow**
```
Conversations → GUI/CLI → Orchestrator → ContentGenerator
                ↓
            Generated Content → File Output → User Notification
```

## Benefits of This Architecture

### 1. **Maintainability**
- **Single Source of Truth**: All scraping logic in orchestrator
- **Clear Interfaces**: Well-defined method signatures
- **Consistent Error Handling**: Unified result objects

### 2. **Testability**
- **Isolated Components**: Each module can be tested independently
- **Mock Support**: Easy to mock orchestrator for testing
- **Integration Tests**: Full workflow testing possible

### 3. **Extensibility**
- **New Commands**: Easy to add new CLI commands
- **New GUI Features**: Simple to add new GUI panels
- **New Generators**: Plug-in new content generators

### 4. **User Experience**
- **Responsive GUI**: Threading prevents blocking
- **Clear Feedback**: Consistent status updates
- **Error Recovery**: Graceful error handling

## Usage Examples

### 1. **GUI Usage**
```python
# Run the integration example
python examples/scraper_integration_example.py
```

### 2. **CLI Usage**
```bash
# Login
python scripts/scraper_cli_demo.py login --username user@example.com --password pass

# Extract conversations
python scripts/scraper_cli_demo.py extract-conversations --max 50

# Generate blog
python scripts/scraper_cli_demo.py generate-blog

# Complete workflow
python scripts/scraper_cli_demo.py workflow --username user@example.com --password pass --max 10
```

### 3. **Programmatic Usage**
```python
from core.scraper_orchestrator import ScraperOrchestrator

# Initialize
orchestrator = ScraperOrchestrator(headless=False)

# Login
result = orchestrator.login_and_save_cookies(username, password)

# Extract conversations
result = orchestrator.extract_conversations(max_conversations=50)

# Generate content
result = orchestrator.generate_blog_post(conversations)
```

## Best Practices

### 1. **Always Use the Orchestrator**
- Don't call scraping modules directly
- Use the orchestrator for all operations
- Maintain the facade pattern

### 2. **Handle Results Properly**
- Check `result.success` before using `result.data`
- Display `result.error` when operations fail
- Use `result.metadata` for additional information

### 3. **Manage Resources**
- Use context managers when possible
- Call `orchestrator.close()` when done
- Clean up threads in GUI applications

### 4. **Thread Safety**
- Use background threads for long operations
- Communicate results via queues
- Don't block the main thread

## Conclusion

This modular architecture provides:

✅ **Clean separation** between GUI, CLI, and business logic  
✅ **Reusable components** that work in multiple contexts  
✅ **Consistent interfaces** across all entry points  
✅ **Professional code structure** that's easy to maintain  
✅ **LOC compliance** with focused, concise modules  

The `ScraperOrchestrator` serves as the single point of coordination, ensuring that all scraping operations are consistent, reliable, and maintainable across both GUI and CLI interfaces. 