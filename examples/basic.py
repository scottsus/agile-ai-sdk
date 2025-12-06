import asyncio

from agile_ai_sdk import AgentTeam, EventType, print_event


async def main():
    """Run a simple task with the agent team."""

    team = AgentTeam()

    @team.on_any_event
    async def log_all_events(event):
        """Log all events to console."""
        print_event(event)

    @team.on(EventType.RUN_FINISHED)
    async def on_complete(event):
        """Handle completion."""
        print("\n✅ Task completed successfully!")
        await team.stop()

    @team.on(EventType.RUN_ERROR)
    async def on_error(event):
        """Handle errors."""
        print(f"\n❌ Error: {event.data.get('error', 'Unknown error')}")
        await team.stop()

    await team.start()
    await team.drop_message("I'm just testing something. List all the files inside the src/agile_ai_sdk folder?")

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        await team.stop()


if __name__ == "__main__":
    asyncio.run(main())
