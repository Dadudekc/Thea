# Undetected ChromeDriver Integration

## Overview

The Digital Dreamscape project now includes support for `undetected-chromedriver`, a powerful library that enhances web scraping capabilities by bypassing bot detection mechanisms. This integration provides improved success rates when scraping websites that employ anti-bot measures.

## Features

### 🛡️ Anti-Detection Capabilities
- **WebDriver Property Removal**: Automatically removes `navigator.webdriver` property
- **Automation Flag Disabling**: Disables Chrome's automation flags
- **User Agent Masking**: Masks automation indicators in user agent strings
- **Stealth Mode**: Operates in a way that mimics human browsing behavior

### 🔄 Automatic Fallback
- **Graceful Degradation**: Falls back to regular selenium if undetected-chromedriver is unavailable
- **Import Safety**: Handles missing dependencies without breaking functionality
- **Configuration Control**: Allows users to choose between modes

### ⚙️ Configurable Options
- **Mode Selection**: Toggle between undetected and regular modes
- **Headless Support**: Works in both headless and GUI modes
- **Timeout Control**: Configurable timeout settings
- **Browser Options**: Customizable Chrome options

## Installation

The `undetected-chromedriver` dependency is already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install undetected-chromedriver>=3.5.0
```

## Usage

### Basic Usage

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

### Advanced Configuration

```python
# Force regular selenium mode
scraper_regular = ChatGPTScraper(use_undetected=False)

# Headless mode with undetected-chromedriver
scraper_headless = ChatGPTScraper(
    headless=True,
    use_undetected=True,
    timeout=60
)
```

## Testing

### Run Tests

```bash
# Test undetected-chromedriver functionality
python main.py undetected_chrome

# Run comprehensive tests
python main.py test

# Run example scripts
python examples/undetected_chrome_example.py scrape
python examples/undetected_chrome_example.py compare
```

### Test Output

When running tests, you should see output like:

```
✅ Undetected-chromedriver import successful!
INFO:scrapers.chatgpt_scraper:Using undetected-chromedriver for enhanced anti-detection
✅ Undetected mode: True
INFO:scrapers.chatgpt_scraper:Using regular selenium webdriver
✅ Regular mode: True
```

## Implementation Details

### Import Strategy

The implementation uses a layered import strategy:

1. **Primary**: Try to import `undetected_chromedriver`
2. **Fallback**: If unavailable, fall back to regular `selenium`
3. **Graceful**: If neither is available, provide clear error messages

### Driver Initialization

```python
if self.use_undetected:
    # Use undetected-chromedriver
    options = uc.ChromeOptions()
    # ... configure options ...
    self.driver = uc.Chrome(options=options)
    
    # Remove webdriver property
    self.driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
else:
    # Fallback to regular selenium
    chrome_options = Options()
    # ... configure options ...
    self.driver = webdriver.Chrome(options=chrome_options)
```

### Anti-Detection Features

The undetected-chromedriver integration includes several anti-detection measures:

- **Chrome Options**:
  - `--disable-blink-features=AutomationControlled`
  - `--excludeSwitches=["enable-automation"]`
  - `--useAutomationExtension=false`

- **JavaScript Execution**:
  - Removes `navigator.webdriver` property
  - Masks automation indicators

## Troubleshooting

### Common Issues

1. **Import Error**: `undetected-chromedriver` not found
   ```bash
   pip install undetected-chromedriver
   ```

2. **Chrome Version Mismatch**: Ensure Chrome browser is up to date
   ```bash
   # Check Chrome version
   google-chrome --version
   ```

3. **Permission Issues**: Run with appropriate permissions
   ```bash
   # On Linux/Mac
   sudo python main.py undetected_chrome
   ```

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

scraper = ChatGPTScraper(use_undetected=True)
```

## Performance Considerations

### Memory Usage
- Undetected-chromedriver may use slightly more memory than regular selenium
- Consider using headless mode for production environments

### Speed
- Initial startup may be slower due to anti-detection measures
- Subsequent operations should be comparable to regular selenium

### Reliability
- Higher success rates on sites with bot detection
- More stable for long-running scraping sessions

## Best Practices

1. **Use Context Managers**: Always use `with` statements for automatic cleanup
2. **Handle Exceptions**: Implement proper error handling for network issues
3. **Respect Rate Limits**: Add delays between requests to avoid overwhelming servers
4. **Monitor Logs**: Check logs for any detection or error messages
5. **Test Both Modes**: Verify functionality with both undetected and regular modes

## Examples

See the `examples/undetected_chrome_example.py` file for complete working examples:

- Basic scraping with undetected-chromedriver
- Comparison between regular and undetected modes
- Error handling and recovery
- Configuration options

## Contributing

When contributing to the undetected-chromedriver integration:

1. Test both modes (undetected and regular)
2. Ensure backward compatibility
3. Add appropriate error handling
4. Update documentation
5. Include test cases

## License

This integration follows the same license as the main project (MIT License). 