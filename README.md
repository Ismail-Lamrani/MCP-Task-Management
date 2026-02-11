# 📋 MCP Task Manager

A simple **Task Management** application built with the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) using [FastMCP](https://gofastmcp.com/).

This project demonstrates how to build an MCP **server** that exposes tools, and an MCP **client** that connects to the server and calls those tools interactively.

---

## 📁 Project Structure

```
MCP-Task-Management/
├── task_server.py   # MCP server — exposes task management tools
├── mcp_client.py    # MCP client — interactive CLI to manage tasks
└── README.md
```

---

## ⚙️ Prerequisites

- **Python 3.10+**
- **FastMCP** — install with:
  ```bash
  pip install fastmcp
  ```
- **Node.js** *(optional)* — only needed if you want to use the MCP Inspector

---

## 🚀 Getting Started

### Option 1: Use the Interactive Client

The client spawns the server automatically via **stdio** — no need to start the server separately.

```bash
python mcp_client.py
```

You'll see a menu like this:

```
✅ Connected to Task Management Server!
📦 Available tools: ['add_task', 'remove_task', 'list_tasks', 'complete_task']

========================================
  📋 Task Manager - MCP Client
========================================
  1. Add a task
  2. Remove a task
  3. List all tasks
  4. Complete a task
  5. Exit
========================================
```

### Option 2: Use the MCP Inspector (Visual UI)

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) provides a web-based UI to test your server.

```bash
npx @modelcontextprotocol/inspector python task_server.py
```

Then open the URL shown in the terminal (usually `http://localhost:6274`).

> **⚠️ Important:** The Inspector uses **stdio** transport. Make sure `task_server.py` is set to `mcp.run()` (not HTTP transport).

### Option 3: Run the Server with HTTP Transport

If you want to connect via HTTP (e.g., from a web app or using curl):

```python
# In task_server.py, change the last line to:
mcp.run(transport="http", host="localhost", port=8000)
```

```bash
python task_server.py
# Server will be available at http://localhost:8000/mcp
```

---

## 🛠️ Available Tools

| Tool | Parameters | Description |
|------|-----------|-------------|
| `add_task` | `task_name: str` | Add a new task |
| `remove_task` | `task_id: int` | Remove a task by its ID |
| `list_tasks` | *none* | List all tasks with their status |
| `complete_task` | `task_id: int` | Mark a task as completed |

---

## 🔌 Transport Modes

| Mode | Use Case | How to Run |
|------|----------|------------|
| **stdio** *(default)* | Client / Inspector spawns the server as a subprocess | `mcp.run()` |
| **HTTP** | Browser, curl, or remote clients | `mcp.run(transport="http", host="localhost", port=8000)` |

---

