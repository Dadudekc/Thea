#!/usr/bin/env python3
"""
Simple Dream.OS Scraper CLI Tool
Core functionality for fixing imports and health checking.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SimpleScraperCLI:
    """Simplified CLI class for scraper operations."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.scrapers_dir = self.project_root / "scrapers"
    
    def fix_imports(self, target_file: str = None):
        """Fix import paths in scraper modules."""
        print("🔧 Fixing import paths...")
        
        if target_file:
            files_to_fix = [Path(target_file)]
        else:
            files_to_fix = list(self.scrapers_dir.glob("*.py"))
        
        for file_path in files_to_fix:
            if not file_path.exists():
                print(f"❌ File not found: {file_path}")
                continue
                
            print(f"📝 Processing: {file_path.name}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if sys.path.insert is already present
            if "sys.path.insert(0," not in content:
                # Add import and sys.path.insert at the top
                import_block = """import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
                # Find the first import line
                lines = content.split('\n')
                insert_index = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        insert_index = i
                        break
                
                lines.insert(insert_index, import_block)
                content = '\n'.join(lines)
                
                # Convert relative imports to absolute
                content = content.replace('from .', 'from scrapers.')
                content = content.replace('from ..', 'from ')
                
                # Write back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Fixed imports in {file_path.name}")
            else:
                print(f"⏭️  Imports already fixed in {file_path.name}")
    
    def health_check(self, target_dir: str = "scrapers"):
        """Perform health check on modules."""
        print("🏥 Performing health check...")
        
        target_path = self.project_root / target_dir
        if not target_path.exists():
            print(f"❌ Directory not found: {target_path}")
            return
        
        stats = {
            'total_files': 0,
            'files_with_imports': 0,
            'files_with_sys_path': 0,
            'files_over_300_lines': 0,
            'files_with_errors': 0
        }
        
        for py_file in target_path.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            stats['total_files'] += 1
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # Check imports
                if 'import ' in content or 'from ' in content:
                    stats['files_with_imports'] += 1
                
                # Check sys.path.insert
                if 'sys.path.insert(0,' in content:
                    stats['files_with_sys_path'] += 1
                
                # Check line count
                if len(lines) > 300:
                    stats['files_over_300_lines'] += 1
                    print(f"⚠️  {py_file.name}: {len(lines)} lines (over 300)")
                
            except Exception as e:
                stats['files_with_errors'] += 1
                print(f"❌ Error reading {py_file.name}: {e}")
        
        print(f"\n📊 Health Check Results:")
        print(f"  Total files: {stats['total_files']}")
        print(f"  Files with imports: {stats['files_with_imports']}")
        print(f"  Files with sys.path: {stats['files_with_sys_path']}")
        print(f"  Files over 300 lines: {stats['files_over_300_lines']}")
        print(f"  Files with errors: {stats['files_with_errors']}")
        
        # Recommendations
        if stats['files_with_sys_path'] < stats['total_files']:
            print(f"\n💡 Recommendation: Run 'fix-imports' to add sys.path.insert to all files")
        
        if stats['files_over_300_lines'] > 0:
            print(f"\n💡 Recommendation: Consider splitting files over 300 lines")
    
    def test_imports(self):
        """Test if all modules can be imported."""
        print("🧪 Testing module imports...")
        
        for py_file in self.scrapers_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            module_name = py_file.stem
            print(f"🔬 Testing {module_name}...")
            
            try:
                # Try to import the module
                import_cmd = f"import sys; sys.path.insert(0, '{self.project_root}'); from scrapers.{module_name} import *; print('✅ {module_name} imports successfully')"
                result = os.system(f'python -c "{import_cmd}"')
                
                if result == 0:
                    print(f"✅ {module_name} imports successfully")
                else:
                    print(f"❌ {module_name} import failed")
                    
            except Exception as e:
                print(f"❌ Error testing {module_name}: {e}")

def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Dream.OS Scraper CLI Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Fix imports command
    subparsers.add_parser('fix-imports', help='Fix import paths')
    
    # Health check command
    subparsers.add_parser('health-check', help='Perform health check')
    
    # Test imports command
    subparsers.add_parser('test-imports', help='Test module imports')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = SimpleScraperCLI()
    
    if args.command == 'fix-imports':
        cli.fix_imports()
    elif args.command == 'health-check':
        cli.health_check()
    elif args.command == 'test-imports':
        cli.test_imports()

if __name__ == "__main__":
    main() 