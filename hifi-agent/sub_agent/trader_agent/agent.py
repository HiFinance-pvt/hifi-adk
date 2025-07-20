from google.adk.agents import Agent

trader_agent = Agent(
    model='gemini-2.0-flash-001',
    name='trader_agent',
    description='You are a trader agent that is responsible for managing stock market and financial market related tasks.',
    instruction='You are a trader agent that is responsible for managing stock market and financial market related tasks.',
)
