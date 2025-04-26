# Dream.OS

Dream.OS is a fully autonomous, self-healing AI operating system that orchestrates Cursor (code execution) and ChatGPT (response refinement) in a continuous feedback loop to automatically detect, diagnose, and fix issues in your codebase.

## Features

- 🚀 End-to-End Auto-Fix Loop: plan, inject, fetch, refine, apply, evaluate, repeat
- 🤖 Agent-Driven: TaskNexus integration for background `autofix` tasks
- 🖥 GUI & CLI Support: PyAutoGUI + VS Code CLI for interactive or headless modes
- 🏗 Modular Architecture: clear separation of core, interfaces, agents, and services

## Architecture

```mermaid
flowchart LR
  subgraph Dream.OS
    A[Plan Task] --> B[CursorInjector]
    E[Fetch Cursor Reply] --> F[ChatGPTResponder]
    H[Fetch GPT Refinement] --> I[CursorInjector]
    K[Fetch Final Cursor Output] --> L[Evaluator]
    L --> M{Continue?}
    M -->|Yes| A
    M -->|No| END[Done]
  end
  subgraph Cursor
    B --> C[Cursor UI / Headless CLI]
    I --> C
  end
  subgraph ChatGPT
    F --> G[ChatGPT API]
  end
```  

## Getting Started

### 1. Clone & Install
```bash
git clone <repo-url>
cd Dream.os
pip install -e .
```  

### 2. Configure
Review `src/dreamos/config.py` for AI endpoints, agent IDs, and UI settings.

### 3. Run the AutoFix Agent
```bash
dreamos-autofix
```  
This will start the background `AutoFixerAgent` that continuously processes `autofix` tasks.

### 4. Run Tests
```bash
pytest
```  

## Project Layout
```
.
├── README.md
├── requirements.txt
├── setup.py
├── src/
│   └── dreamos/
│       ├── __init__.py
│       ├── config.py
│       ├── agent_utils.py
│       ├── orchestrator.py
│       ├── cursor_interface.py
│       ├── chatgpt_interface.py
│       ├── evaluator.py
│       ├── agents/
│       │   ├── __init__.py
│       │   └── autofix_agent.py
│       └── services/
│           ├── __init__.py
│           └── autofix_service.py
└── tests/
    ├── test_orchestrator.py
    └── test_autofix_agent.py
```

## Contributing
Please open issues or pull requests. All code should follow PEP8 and include tests. 