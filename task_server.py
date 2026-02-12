import json
from fastmcp import FastMCP, Context

# Créer l'instance du serveur MCP
mcp = FastMCP(name="Task Management Server")

# Fichier JSON pour stocker les tâches
TASKS_FILE = "tasks.json"


# ── Helper functions (internal, not exposed to MCP) ──

def load_tasks() -> dict:
    """Load tasks from the JSON file."""
    try:
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_tasks(tasks: dict):
    """Save tasks to the JSON file."""
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)


# ═══════════════════════════════════════════════════
#  RESOURCES — read-only data exposed to clients
#  Client reads them with: client.read_resource("resource://...")
# ═══════════════════════════════════════════════════

@mcp.resource("resource://task-database")
def task_database() -> str:
    """Resource that exposes the full task database as JSON (read-only)."""
    return json.dumps(load_tasks())


@mcp.resource("resource://tasks/{task_id}")
def get_task_by_id(task_id: int) -> str:
    """Resource template — returns JSON details for a specific task by ID."""
    tasks = load_tasks()
    task_id_str = str(task_id)
    if task_id_str in tasks:
        task = tasks[task_id_str]
        return json.dumps({
            "id": task_id,
            "name": task["name"],
            "completed": task["completed"],
            "priority": task.get("priority", "Medium"),
        })
    return json.dumps({"error": f"Task ID {task_id} not found."})


# ═══════════════════════════════════════════════════
#  TOOLS — actions the client can invoke
# ═══════════════════════════════════════════════════

@mcp.tool()
async def add_task(task_name: str, ctx: Context) -> str:
    """
    Add a task. Uses elicitation to ask the user for priority and deadline.
    """
    # Ask the user for priority using ctx.elicit()
    priority_result = await ctx.elicit(
        message="What is the priority? (High / Medium / Low)",
        response_type=["High", "Medium", "Low"],
    )
    priority = priority_result.data if priority_result.action == "accept" else "Medium"

    # Ask the user for deadline using ctx.elicit()
    deadline_result = await ctx.elicit(
        message="What is the deadline? (e.g. 2026-02-15)",
        response_type=str,
    )
    deadline = deadline_result.data if deadline_result.action == "accept" else "No deadline"

    # Save to JSON file
    tasks = load_tasks()
    task_id = len(tasks) + 1
    tasks[str(task_id)] = {
        "name": task_name,
        "priority": priority,
        "deadline": deadline,
        "completed": False,
    }
    save_tasks(tasks)

    return f"Task '{task_name}' added with ID {task_id} (priority: {priority}, deadline: {deadline})."


@mcp.tool()
def remove_task(task_id: int) -> str:
    """Remove a task by its ID."""
    tasks = load_tasks()
    task_id_str = str(task_id)
    if task_id_str in tasks:
        del tasks[task_id_str]
        save_tasks(tasks)
        return f"Task ID {task_id} removed."
    return f"Task ID {task_id} not found."


@mcp.tool()
def list_tasks() -> str:
    """List all tasks with their status."""
    tasks = load_tasks()
    if not tasks:
        return "No tasks available."
    task_list = ""
    for task_id, task in tasks.items():
        status = "Completed" if task["completed"] else "Pending"
        task_list += f"ID: {task_id}, Task: {task['name']}, Status: {status}\n"
    return task_list


@mcp.tool()
def complete_task(task_id: int) -> str:
    """Mark a task as completed."""
    tasks = load_tasks()
    task_id_str = str(task_id)
    if task_id_str in tasks:
        tasks[task_id_str]["completed"] = True
        save_tasks(tasks)
        return f"Task ID {task_id} marked as completed."
    return f"Task ID {task_id} not found."


# ═══════════════════════════════════════════════════
#  PROMPTS — reusable LLM message templates
#  Client reads them with: client.get_prompt("name", {args})
# ═══════════════════════════════════════════════════

@mcp.prompt()
def analyze_task(task_id: int) -> str:
    """Analyze a task to determine if it's overdue or incomplete."""
    tasks = load_tasks()
    task_id_str = str(task_id)
    if task_id_str not in tasks:
        return f"Task ID {task_id} not found."

    task = tasks[task_id_str]
    if task["completed"]:
        return f"Task '{task['name']}' (ID {task_id}) is completed. Good job!"
    else:
        return (
            f"Task '{task['name']}' (ID {task_id}) is still pending "
            f"(priority: {task.get('priority', 'Medium')}). "
            "Please analyze why this task is not yet done and suggest next steps."
        )


@mcp.prompt()
def explain_task_management(concept: str) -> str:
    """Explain a task management concept."""
    explanations = {
        "priority": "Task priority refers to the importance level of a task (High, Medium, Low). It helps in organizing tasks.",
        "deadline": "A deadline is the final date or time by which a task must be completed.",
        "task completion": "Task completion means that all necessary actions for a task have been finished and the task is marked as done.",
    }
    return explanations.get(concept.lower(), f"Sorry, I don't have an explanation for '{concept}'.")


# ═══════════════════════════════════════════════════
#  RUN
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    mcp.run()  # default: stdio | HTTP: mcp.run(transport="http", host="localhost", port=8000)
