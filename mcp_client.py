# in this phase you can just use the npx @modelcontextprotocol/inspector python task_server.py to test your server in the UI of MCP
import asyncio
import os
from pathlib import Path
from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult, ElicitRequestParams, RequestContext
from fastmcp.client.sampling import (
    SamplingMessage,
    SamplingParams,
    RequestContext,
)


# Root = the project directory (where tasks.json lives)
# Roots require file:// URIs, so we convert the path using pathlib
PROJECT_ROOT = Path(os.path.dirname(os.path.abspath(__file__))).as_uri()


async def elicitation_handler(
    message: str,
    response_type: type | None,
    params: ElicitRequestParams,
    context: RequestContext
):
    """
    Handle server elicitation requests.
    """

    print("\n🟡 Server is requesting additional information.")
    print(f"📨 {message}")

    user_input = input("👉 Your answer: ").strip()

    if not user_input:
        print("⚠️  You declined to provide input.")
        return ElicitResult(action="decline")

    # Automatically return correct type (must use keyword arg value=)
    if response_type:
        return response_type(value=user_input)

    return user_input

async def sampling_handler(messages, params, context) -> str:
    """Mock sampling handler — returns a fake AI response for testing."""
    print("\n🧠 [MOCK] Server requested AI sampling...")
    for msg in messages:
        content = msg.content.text if hasattr(msg.content, "text") else str(msg.content)
        print(f"   [{msg.role}] {content}")

    return "I suggest you prioritize the highest-priority pending task first. Focus on completing it before moving to lower-priority items. (This is a mock response for testing.)"


async def main():
    # Connect to the task server with elicitation handler and roots
    client = Client(
        "task_server.py",
        elicitation_handler=elicitation_handler,
        roots=[PROJECT_ROOT], 
        sampling_handler=sampling_handler, # ← Roots: tells the server our workspace location
    )

    async with client:
        # Show available capabilities on startup
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()

        print("\n✅ Connected to Task Management Server!")
        print(f"📦 Available tools:     {[t.name for t in tools]}")
        print(f"📂 Available resources: {[r.uri for r in resources]}")
        print(f"💬 Available prompts:   {[p.name for p in prompts]}\n")

        while True:
            print("=" * 50)
            print("  📋 Task Manager - MCP Client")
            print("=" * 50)
            print("  ── Tools ──")
            print("  1. Add a task")
            print("  2. Remove a task")
            print("  3. List all tasks")
            print("  4. Complete a task")
            print()
            print("  ── Resources ──")
            print("  5. View all tasks       (resource)")
            print("  6. View task by ID      (resource template)")
            print()
            print("  ── Prompts ──")
            print("  7. Analyze a task       (prompt)")
            print("  8. Explain a concept    (prompt)")
            print()
            print("  0. Exit")
            print("=" * 50)

            choice = input("\n👉 Choose an option: ").strip()

            if choice == "1":
                task_name = input("📝 Enter task name: ").strip()
                if task_name:
                    result = await client.call_tool("add_task", {"task_name": task_name})
                    print(f"\n✅ {result}")
                else:
                    print("\n⚠️  Task name cannot be empty.")

            elif choice == "2":
                task_id = input("🔢 Enter task ID to remove: ").strip()
                try:
                    result = await client.call_tool("remove_task", {"task_id": int(task_id)})
                    print(f"\n🗑️  {result}")
                except ValueError:
                    print("\n⚠️  Please enter a valid number.")

            elif choice == "3":
                result = await client.call_tool("list_tasks", {})
                print(f"\n📋 Tasks:\n{result}")

            elif choice == "4":
                task_id = input("🔢 Enter task ID to complete: ").strip()
                try:
                    result = await client.call_tool("complete_task", {"task_id": int(task_id)})
                    print(f"\n🎉 {result}")
                except ValueError:
                    print("\n⚠️  Please enter a valid number.")

            # ── Resources ──

            elif choice == "5":
                content = await client.read_resource("resource://task-database")
                print(f"\n📊 All Tasks (JSON):\n{content}")

            elif choice == "6":
                task_id = input("🔢 Enter task ID: ").strip()
                try:
                    content = await client.read_resource(f"resource://tasks/{int(task_id)}")
                    print(f"\n� Task Details:\n{content}")
                except ValueError:
                    print("\n⚠️  Please enter a valid number.")

            # ── Prompts ──

            elif choice == "7":
                task_id = input("🔢 Enter task ID to analyze: ").strip()
                try:
                    result = await client.get_prompt("analyze_task", {"task_id": int(task_id)})
                    print("\n💬 Prompt Messages:")
                    for msg in result.messages:
                        text = msg.content.text if hasattr(msg.content, "text") else str(msg.content)
                        print(f"   [{msg.role}] {text}")
                except ValueError:
                    print("\n⚠️  Please enter a valid number.")

            elif choice == "8":
                concept = input("📖 Enter concept (priority / deadline / task completion): ").strip()
                if concept:
                    result = await client.get_prompt("explain_task_management", {"concept": concept})
                    print("\n💬 Prompt Messages:")
                    for msg in result.messages:
                        text = msg.content.text if hasattr(msg.content, "text") else str(msg.content)
                        print(f"   [{msg.role}] {text}")
                else:
                    print("\n⚠️  Concept cannot be empty.")
            
            elif choice == "9":
                result = await client.call_tool("suggest_priority", {})
                print(result)

            elif choice == "0":
                print("\n👋 Goodbye!")
                break

            else:
                print("\n⚠️  Invalid choice. Please select 0-8.")

            print()  # blank line for readability


if __name__ == "__main__":
    asyncio.run(main())
