# Dream.OS Tool Catalog

This catalog lists all available tools in the Dream.OS toolbelt system, organized by category.

Status indicators:
- ✅ Stable: Production-ready tools
- 🔨 Beta: Tools under active development/testing
- 🧪 Experimental: Proof-of-concept or experimental tools

## Core Infrastructure

- ✅ `universal_toolbelt.py` - Core tool management system
- ✅ `dreamos_cli.py` - Main CLI interface for Dream.OS

## CLI Tools

- ✅ `scraper_cli.py` - Command-line interface for web scraping
- ✅ `simple_scraper_cli.py` - Simplified scraping interface
- 🔨 `devlog_tool.py` - Create and post development updates to Discord
  - Dependencies: discord_manager, devlog_generator, template_engine
  - Features:
    - Create structured devlog posts with title, description, content
    - Include code snippets, challenges, solutions, and learnings
    - Auto-format for Discord with emojis and markdown
    - Save locally and post to Discord channels
    - Support for tags and categorization
  - Usage:
    ```bash
    # Create and post a new devlog
    python tools/devlog_tool.py create \
      --title "Feature Update" \
      --description "Added new functionality" \
      --content "Detailed update..." \
      --tags feature update \
      --code "print('hello')" \
      --code-lang python \
      --challenge "Issue found" \
      --solution "Fixed by..."
      
    # Post existing devlog file
    python tools/devlog_tool.py post path/to/devlog.md
    ```

## Setup & Configuration

- ✅ `discord_wizard.py` - Interactive Discord bot setup
- ✅ `module_generator.py` - Generate new Dream.OS modules

## Development Tools

- ✅ `add_tools.py` - Add new tools to the toolbelt
- 🧪 `hello_tool.py` - Example/template tool

## Utility Tools

- ✅ `simple_runner.py` - Simple tool execution wrapper

---

*Note: This catalog is automatically updated when tools are added or modified through the toolbelt system.*

## Documentation

| Document | Description | Location |
|----------|-------------|----------|
| CLI Tools Proposal | Detailed proposal for CLI tool architecture | tools/CLI_TOOLS_PROPOSAL.md |
| Toolbelt README | Universal toolbelt usage guide | tools/README.md |
| Tool Catalog | This comprehensive catalog | tools/TOOL_CATALOG.md |
| Requirements | Toolbelt dependencies | tools/requirements_toolbelt.txt |

## Usage Instructions

1. List all tools:
```bash
python tools/universal_toolbelt.py list
```

2. Get tool details:
```bash
python tools/universal_toolbelt.py get <tool_name>
```

3. Run a tool:
```bash
python tools/simple_runner.py <tool_name> [args...]
```

4. Add new tools:
```bash
python tools/add_tools.py
```

## Tool Dependencies

Tools may have dependencies on each other. Here are the main dependency relationships:

- `universal_toolbelt.py` - Core tool that others depend on
- `add_tools.py` - Uses universal_toolbelt
- `run_tool.py` - Uses universal_toolbelt
- `simple_runner.py` - Standalone runner
- `module_generator.py` - Can be used independently
- `discord_wizard.py` - Can be used independently
- `scraper_cli.py` - May depend on core scraping modules
- `simple_scraper_cli.py` - Simplified version of scraper_cli

## For Agents

When using these tools, agents should:

1. Check the catalog first to find the most appropriate tool
2. Use the most specific tool for the task
3. Prefer stable tools over experimental ones
4. Check tool dependencies before use
5. Use the universal toolbelt to access tools from any location

## Tool Status

- ✅ Stable: Production ready
- 🔨 Beta: Testing required
- 🧪 Experimental: Use with caution

| Tool | Status |
|------|--------|
| universal_toolbelt | ✅ |
| dreamos_cli | ✅ |
| scraper_cli | ✅ |
| simple_scraper_cli | 🔨 |
| discord_wizard | ✅ |
| module_generator | ✅ |
| add_tools | ✅ |
| run_tool | 🔨 |
| simple_runner | ✅ |
| devlog_tool | 🔨 | 