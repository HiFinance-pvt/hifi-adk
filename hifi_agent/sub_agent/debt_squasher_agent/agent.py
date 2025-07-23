from google.adk.agents import Agent

debt_squasher_agent = Agent(
    model='gemini-2.0-flash-001',
    name='debt_squasher_agent',
    description='You are a debt squasher agent that is responsible for managing debt and financial obligations.',
    instruction='You are a debt squasher agent that is responsible for managing debt and financial obligations.',
)
