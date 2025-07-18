from google.adk.agents import Agent

hifi_agent = Agent(
    model='gemini-2.0-flash-001',
    name='hifi_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
