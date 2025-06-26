#!/usr/bin/env python3
"""
Scraper CLI Tool
================

CLI tool that would have made the scraper workflow much easier.
Provides import fixing, dependency analysis, integration testing, and more.
"""

import argparse
import sys
import os
import ast
import importlib
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Optional
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)

class ScraperCLI:
    """CLI tool for scraper workflow management."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.scrapers_dir = self.project_root / "scrapers"
        self.core_dir = self.project_root / "core"
        self.gui_dir = self.project_root / "gui"
        
    def fix_imports(self):
        """Fix import path issues across the project."""
        print("🔧 Fixing import paths...")
        
        # Common import patterns to fix
        import_fixes = {
            "from scrapers.": "from scrapers.",
            "from core.": "from core.",
            "from gui.": "from gui.",
            "import scrapers.": "import scrapers.",
            "import core.": "import core.",
            "import gui.": "import gui.",
        }
        
        # Add sys.path.insert to files that need it
        files_to_fix = [
            "scripts/scraper_cli_demo.py",
            "examples/scraper_integration_example.py",
            "gui/panels/scraper_panel.py"
        ]
        
        for file_path in files_to_fix:
            full_path = self.project_root / file_path
            if full_path.exists():
                self._add_sys_path_insert(full_path)
                print(f"✅ Fixed imports in {file_path}")
        
        print("✅ Import fixes completed")
    
    def _add_sys_path_insert(self, file_path: Path):
        """Add sys.path.insert to a file if it doesn't exist."""
        content = file_path.read_text(encoding='utf-8')
        
        if "sys.path.insert" not in content:
            insert_code = f"""import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

"""
            
            # Find the right place to insert (after imports)
            lines = content.split('\n')
            insert_index = 0
            
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_index = i + 1
                elif line.strip() and not line.startswith('#'):
                    break
            
            lines.insert(insert_index, insert_code)
            file_path.write_text('\n'.join(lines), encoding='utf-8')
    
    def analyze_deps(self):
        """Analyze module dependencies and relationships."""
        print("📊 Analyzing module dependencies...")
        
        dependencies = {}
        
        # Analyze scrapers directory
        for file_path in self.scrapers_dir.rglob("*.py"):
            if file_path.name != "__init__.py":
                deps = self._analyze_file_dependencies(file_path)
                dependencies[file_path.relative_to(self.project_root)] = deps
        
        # Analyze core directory
        for file_path in self.core_dir.rglob("*.py"):
            if file_path.name != "__init__.py":
                deps = self._analyze_file_dependencies(file_path)
                dependencies[file_path.relative_to(self.project_root)] = deps
        
        # Display dependency graph
        print("\n📋 Module Dependencies:")
        print("=" * 50)
        
        for module, deps in dependencies.items():
            print(f"\n{module}:")
            if deps:
                for dep in deps:
                    print(f"  └── {dep}")
            else:
                print("  └── (no dependencies)")
        
        print(f"\n✅ Analyzed {len(dependencies)} modules")
    
    def _analyze_file_dependencies(self, file_path: Path) -> List[str]:
        """Analyze dependencies of a single file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            deps = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        deps.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        deps.append(node.module)
            
            return deps
        except Exception as e:
            logger.warning(f"Could not analyze {file_path}: {e}")
            return []
    
    def test_integration(self):
        """Test integration between modules."""
        print("🧪 Testing module integration...")
        
        test_results = []
        
        # Test orchestrator initialization
        try:
            from core.scraper_orchestrator import ScraperOrchestrator
            orchestrator = ScraperOrchestrator(headless=True)
            test_results.append(("Orchestrator Initialization", "✅ PASS"))
            orchestrator.close()
        except Exception as e:
            test_results.append(("Orchestrator Initialization", f"❌ FAIL: {e}"))
        
        # Test GUI panel import
        try:
            from gui.panels.scraper_panel import ScraperPanel
            test_results.append(("GUI Panel Import", "✅ PASS"))
        except Exception as e:
            test_results.append(("GUI Panel Import", f"❌ FAIL: {e}"))
        
        # Test CLI demo import
        try:
            import scripts.scraper_cli_demo
            test_results.append(("CLI Demo Import", "✅ PASS"))
        except Exception as e:
            test_results.append(("CLI Demo Import", f"❌ FAIL: {e}"))
        
        # Display results
        print("\n📋 Integration Test Results:")
        print("=" * 40)
        
        for test_name, result in test_results:
            print(f"{test_name}: {result}")
        
        passed = sum(1 for _, result in test_results if "PASS" in result)
        total = len(test_results)
        
        print(f"\n✅ {passed}/{total} tests passed")
    
    def health_check(self):
        """Perform health check on the project."""
        print("🏥 Performing project health check...")
        
        issues = []
        
        # Check LOC limits
        for file_path in self.project_root.rglob("*.py"):
            if file_path.name != "__init__.py":
                line_count = len(file_path.read_text(encoding='utf-8').split('\n'))
                if line_count > 350:
                    issues.append(f"⚠️  {file_path.relative_to(self.project_root)}: {line_count} lines (over 350 limit)")
        
        # Check for missing __init__.py files
        for dir_path in [self.scrapers_dir, self.core_dir, self.gui_dir]:
            if not (dir_path / "__init__.py").exists():
                issues.append(f"⚠️  Missing __init__.py in {dir_path.relative_to(self.project_root)}")
        
        # Check for common issues
        for file_path in self.project_root.rglob("*.py"):
            content = file_path.read_text(encoding='utf-8')
            
            if "TODO" in content or "FIXME" in content:
                issues.append(f"⚠️  {file_path.relative_to(self.project_root)}: Contains TODO/FIXME")
            
            if "print(" in content and "logging" not in content:
                issues.append(f"⚠️  {file_path.relative_to(self.project_root)}: Uses print() instead of logging")
        
        # Display results
        if issues:
            print("\n⚠️  Health Check Issues:")
            print("=" * 30)
            for issue in issues:
                print(issue)
        else:
            print("✅ No health issues found")
    
    def debug_module(self, module_name: str):
        """Debug a specific module."""
        print(f"🐛 Debugging module: {module_name}")
        
        try:
            # Try to import the module
            module = importlib.import_module(module_name)
            print(f"✅ Module imported successfully")
            
            # Check for common issues
            module_path = Path(module.__file__)
            content = module_path.read_text(encoding='utf-8')
            
            issues = []
            
            if "import " in content and "sys.path.insert" not in content:
                issues.append("Missing sys.path.insert for imports")
            
            if "print(" in content:
                issues.append("Uses print() instead of logging")
            
            if len(content.split('\n')) > 350:
                issues.append("File exceeds 350 line limit")
            
            if issues:
                print("\n⚠️  Issues found:")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print("✅ No issues found")
                
        except ImportError as e:
            print(f"❌ Import error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def generate_orchestrator(self):
        """Generate a proper orchestrator if missing."""
        print("🏗️  Generating ScraperOrchestrator...")
        
        orchestrator_path = self.core_dir / "scraper_orchestrator.py"
        
        if orchestrator_path.exists():
            print("✅ ScraperOrchestrator already exists")
            return
        
        # Generate orchestrator template
        template = '''#!/usr/bin/env python3
"""
Scraper Orchestrator for Dream.OS
=================================

Central orchestrator for all ChatGPT scraping operations.
Provides a clean interface for both GUI and CLI components.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ConversationData:
    """Data structure for conversation information."""
    id: str
    title: str
    url: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    message_count: int = 0
    content: Optional[str] = None
    processed: bool = False

@dataclass
class ScrapingResult:
    """Result structure for scraping operations."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None

class ScraperOrchestrator:
    """Central orchestrator for ChatGPT scraping operations."""
    
    def __init__(self, headless: bool = False, use_undetected: bool = True):
        self.headless = headless
        self.use_undetected = use_undetected
        self.driver = None
        self.is_initialized = False
        self._initialize_components()
        logger.info("ScraperOrchestrator initialized")
    
    def _initialize_components(self):
        """Initialize all scraping components."""
        # TODO: Initialize your scraping components here
        pass
    
    def login_and_save_cookies(self, username: Optional[str] = None, 
                              password: Optional[str] = None) -> ScrapingResult:
        """Handle login process and save cookies."""
        # TODO: Implement login logic
        return ScrapingResult(success=False, error="Not implemented")
    
    def extract_conversations(self, max_conversations: Optional[int] = None) -> ScrapingResult:
        """Extract list of conversations."""
        # TODO: Implement conversation extraction
        return ScrapingResult(success=False, error="Not implemented")
    
    def extract_conversation_content(self, conversation_url: str) -> ScrapingResult:
        """Extract content from a specific conversation."""
        # TODO: Implement content extraction
        return ScrapingResult(success=False, error="Not implemented")
    
    def generate_blog_post(self, conversations: List[ConversationData]) -> ScrapingResult:
        """Generate a blog post from conversations."""
        # TODO: Implement blog generation
        return ScrapingResult(success=False, error="Not implemented")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status."""
        return {
            "initialized": self.is_initialized,
            "headless": self.headless,
            "use_undetected": self.use_undetected,
            "driver_active": self.driver is not None
        }
    
    def close(self):
        """Close the browser and clean up resources."""
        if self.driver:
            # TODO: Implement cleanup
            pass
'''
        
        orchestrator_path.write_text(template, encoding='utf-8')
        print(f"✅ Generated {orchestrator_path}")
    
    def run(self, args):
        """Run the CLI tool."""
        if args.command == "fix-imports":
            self.fix_imports()
        elif args.command == "analyze-deps":
            self.analyze_deps()
        elif args.command == "test-integration":
            self.test_integration()
        elif args.command == "health-check":
            self.health_check()
        elif args.command == "debug-module":
            self.debug_module(args.module_name)
        elif args.command == "generate-orchestrator":
            self.generate_orchestrator()

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Scraper CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Fix imports command
    subparsers.add_parser("fix-imports", help="Fix import path issues")
    
    # Analyze dependencies command
    subparsers.add_parser("analyze-deps", help="Analyze module dependencies")
    
    # Test integration command
    subparsers.add_parser("test-integration", help="Test module integration")
    
    # Health check command
    subparsers.add_parser("health-check", help="Perform project health check")
    
    # Debug module command
    debug_parser = subparsers.add_parser("debug-module", help="Debug a specific module")
    debug_parser.add_argument("module_name", help="Name of the module to debug")
    
    # Generate orchestrator command
    subparsers.add_parser("generate-orchestrator", help="Generate ScraperOrchestrator")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = ScraperCLI()
    cli.run(args)

if __name__ == "__main__":
    main() 