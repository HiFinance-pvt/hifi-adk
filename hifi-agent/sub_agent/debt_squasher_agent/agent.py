from google.adk.agents import Agent

debt_squasher_agent = Agent(
    model='gemini-2.0-flash-001',
    name='debt_squasher_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
