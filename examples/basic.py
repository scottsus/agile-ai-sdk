import asyncio

from agile_ai_sdk import AgentTeam, EventType, print_event


async def main():
    """Run a simple task with the agent team."""

    team = AgentTeam()

    async for event in team.execute(
        "I'm just testing something. List all the files inside the src/agile_ai_sdk folder?"
    ):
        print_event(event)

        if event.type in (EventType.RUN_FINISHED, EventType.RUN_ERROR):
            break


if __name__ == "__main__":
    asyncio.run(main())
