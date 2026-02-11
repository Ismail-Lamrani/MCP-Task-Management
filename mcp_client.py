# in this phase you can just use the npx @modelcontextprotocol/inspector python task_server.py to test your server in the UI of MCP 

import asyncio
from fastmcp import Client


async def main():
    # Connect to the task server via stdio transport
    client = Client("task_server.py")

    async with client:
        # Show available tools on startup
        tools = await client.list_tools()
        print("\n✅ Connected to Task Management Server!")
        print(f"📦 Available tools: {[t.name for t in tools]}\n")

        while True:
            print("=" * 40)
            print("  📋 Task Manager - MCP Client")
            print("=" * 40)
            print("  1. Add a task")
            print("  2. Remove a task")
            print("  3. List all tasks")
            print("  4. Complete a task")
            print("  5. Exit")
            print("=" * 40)

            choice = input("\n👉 Choose an option (1-5): ").strip()

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

            elif choice == "5":
                print("\n👋 Goodbye!")
                break

            else:
                print("\n⚠️  Invalid choice. Please select 1-5.")

            print()  # blank line for readability


if __name__ == "__main__":
    asyncio.run(main())
