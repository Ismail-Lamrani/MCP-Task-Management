from fastmcp import FastMCP

# Create the MCP server instance
mcp = FastMCP(name="Task Management Server")

# In-memory task list to keep track of tasks
tasks = {}

# Tool to add a new task
@mcp.tool()
def add_task(task_name: str) -> str:
    task_id = len(tasks) + 1  # Create a simple unique ID for the task
    tasks[task_id] = {"name": task_name, "completed": False}
    return f"Task '{task_name}' added with ID {task_id}."

# Tool to remove a task by ID
@mcp.tool()
def remove_task(task_id: int) -> str:
    if task_id in tasks:
        del tasks[task_id]
        return f"Task ID {task_id} removed."
    return f"Task ID {task_id} not found."

# Tool to list all tasks
@mcp.tool()
def list_tasks() -> str:
    if not tasks:
        return "No tasks available."
    task_list = ""
    for task_id, task in tasks.items():
        status = "Completed" if task["completed"] else "Pending"
        task_list += f"ID: {task_id}, Task: {task['name']}, Status: {status}\n"
    return task_list

# Tool to mark a task as completed
@mcp.tool()
def complete_task(task_id: int) -> str:
    if task_id in tasks:
        tasks[task_id]["completed"] = True
        return f"Task ID {task_id} marked as completed."
    return f"Task ID {task_id} not found."

# Run the MCP server
if __name__ == "__main__":
    mcp.run() #by default is stdio but if i want to use an hhtps i need to usethis command (transport="http",host="localhost",port=8000)
