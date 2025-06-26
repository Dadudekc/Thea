# Universal Toolbelt

A powerful CLI tool for managing and accessing Python utilities across all your projects. Store your frequently used Python scripts in a central database and access them from anywhere!

## Installation

1. Make sure you have Python 3.6+ installed
2. Install the required dependencies:
```bash
pip install click sqlite3
```

3. Add the toolbelt to your PATH or create a symlink to make it globally accessible:
```bash
# Option 1: Add to PATH
export PATH="$PATH:/path/to/tools"

# Option 2: Create symlink (recommended)
ln -s /path/to/tools/universal_toolbelt.py ~/.local/bin/toolbelt
```

## Usage

The toolbelt provides several commands to manage your Python utilities:

### Adding a Tool

```bash
toolbelt add <name> <file_path> [options]

Options:
  -d, --description TEXT  Tool description
  -t, --tags TEXT        Tags for categorizing the tool (can be used multiple times)
  -c, --category TEXT    Category for the tool
```

Example:
```bash
toolbelt add file_processor scripts/process_files.py -d "Process files in bulk" -t "files" -t "utility" -c "file-ops"
```

### Listing Tools

```bash
toolbelt list [options]

Options:
  -c, --category TEXT  Filter by category
  -t, --tag TEXT      Filter by tag
```

### Getting a Tool

```bash
toolbelt get <name>
```

This will display the tool's details and code.

### Exporting a Tool

```bash
toolbelt export <name> <output_path>
```

This exports the tool to a Python file at the specified path.

### Deleting a Tool

```bash
toolbelt delete <name>
```

## Database Location

The toolbelt stores all tools in a SQLite database at:
```
~/.dreamscape/toolbelt.db
```

## Features

- ✨ Central storage for all your Python utilities
- 🏷️ Tag-based organization
- 📁 Category management
- 🔍 Easy search and retrieval
- 📤 Export capabilities
- 🔄 Automatic version tracking (via file hashing)
- 🔒 Safe updates and deletions

## Example Workflow

1. Create a useful Python script:
```python
# process_files.py
def process_files(directory):
    # Your processing logic here
    pass
```

2. Add it to your toolbelt:
```bash
toolbelt add file_processor process_files.py -d "Process files in bulk" -t "files"
```

3. Use it in another project:
```bash
toolbelt export file_processor ./scripts/process_files.py
```

4. List all your file-related tools:
```bash
toolbelt list -t files
```

## Best Practices

1. **Descriptive Names**: Use clear, descriptive names for your tools
2. **Good Documentation**: Always include a description when adding tools
3. **Proper Tagging**: Use relevant tags to make tools easily discoverable
4. **Categories**: Organize related tools into categories
5. **Regular Cleanup**: Remove outdated or unused tools

## Contributing

Feel free to contribute to this project by:
1. Adding new features
2. Improving documentation
3. Reporting bugs
4. Suggesting improvements

## License

MIT License - Feel free to use and modify as needed! 