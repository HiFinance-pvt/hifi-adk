from google.adk.agents import Agent
from google.adk.tools import google_search

sebi_agent = Agent(
    model='gemini-2.0-flash-001',
    name='sebi_agent',
    description='You are a sebi agent that is responsible for providing financial advice according to India\'s [SEBI] regulations and India specific financial advice.',
    instruction='You are a sebi agent that is responsible for providing financial advice according to India\'s [SEBI] regulations and India specific financial advice.',
    tools=[google_search],
)
