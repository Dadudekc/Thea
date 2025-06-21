"""
Simplified Template Engine for Digital Dreamscape Standalone
Handles rendering of Jinja2 templates without external dependencies.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound, TemplateSyntaxError

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATE_DIR = PROJECT_ROOT / "templates"

# Ensure template directory exists
TEMPLATE_DIR.mkdir(exist_ok=True)

# Initialize Jinja2 environment
env = None
_template_env_ready = False

try:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(enabled_extensions=('html', 'xml', 'j2'), default_for_string=True, default=True),
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    # Add custom filters
    env.filters['tojson'] = lambda value: str(value)  # Simplified JSON filter
    
    print(f"[TemplateEngine] Jinja2 Environment Initialized - Template dir: {TEMPLATE_DIR}")
    _template_env_ready = True

except Exception as e:
    print(f"[TemplateEngine] Failed to initialize Jinja2 Environment: {e}")
    # env remains None

def render_template(template_name: str, context: Dict[str, Any]) -> Optional[str]:
    """
    Render a Jinja2 template with the given context.
    
    Args:
        template_name: The name of the template file or template string
        context: Dictionary containing variables for the template
        
    Returns:
        The rendered template content, or None if rendering fails
    """
    if not _template_env_ready or env is None:
        print(f"[TemplateEngine] Error: Jinja2 environment not ready")
        return None

    try:
        # Check if template_name is a file path or template string
        if os.path.exists(template_name) or template_name.endswith(('.j2', '.html', '.txt')):
            # It's a file path
            template = env.get_template(template_name)
        else:
            # It's a template string
            template = env.from_string(template_name)
            
        rendered_content = template.render(**context)
        print(f"[TemplateEngine] Successfully rendered template")
        return rendered_content
        
    except TemplateNotFound:
        print(f"[TemplateEngine] Error: Template '{template_name}' not found")
        return None
    except TemplateSyntaxError as e:
        print(f"[TemplateEngine] Error: Template syntax error at line {e.lineno}: {e.message}")
        return None
    except Exception as e:
        print(f"[TemplateEngine] Error: Template rendering failed - {e}")
        return None

def create_template_file(template_name: str, content: str) -> bool:
    """
    Create a template file in the template directory.
    
    Args:
        template_name: Name of the template file
        content: Template content
        
    Returns:
        True if successful, False otherwise
    """
    try:
        template_path = TEMPLATE_DIR / template_name
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[TemplateEngine] Created template file: {template_path}")
        return True
    except Exception as e:
        print(f"[TemplateEngine] Error creating template file: {e}")
        return False

def list_templates() -> list:
    """
    List all available templates.
    
    Returns:
        List of template file names
    """
    try:
        return [f.name for f in TEMPLATE_DIR.glob('*') if f.is_file()]
    except Exception as e:
        print(f"[TemplateEngine] Error listing templates: {e}")
        return []

# Test function
def test_template_engine():
    """Test the template engine functionality."""
    print("🧪 Testing Template Engine...")
    
    # Test 1: String template
    test_template = """
    Hello {{ name }}!
    Your value is {{ data.value }}.
    Current time: {{ timestamp }}
    """
    
    context = {
        "name": "World", 
        "data": {"value": 123},
        "timestamp": "2025-01-20"
    }
    
    result = render_template(test_template, context)
    if result:
        print("✅ String template rendering: PASSED")
        print(f"Result: {result.strip()}")
    else:
        print("❌ String template rendering: FAILED")
        return False
    
    # Test 2: File template
    test_file_content = """
    # {{ title }}
    
    Welcome to {{ app_name }}!
    
    ## Features:
    {% for feature in features %}
    - {{ feature }}
    {% endfor %}
    """
    
    if create_template_file("test_template.md", test_file_content):
        file_context = {
            "title": "Test Document",
            "app_name": "Digital Dreamscape",
            "features": ["Template Engine", "ChatGPT Scraper", "GUI Interface"]
        }
        
        file_result = render_template("test_template.md", file_context)
        if file_result:
            print("✅ File template rendering: PASSED")
            print(f"Result: {file_result.strip()}")
        else:
            print("❌ File template rendering: FAILED")
            return False
    
    print("✅ Template Engine tests completed successfully!")
    return True

if __name__ == "__main__":
    test_template_engine() 