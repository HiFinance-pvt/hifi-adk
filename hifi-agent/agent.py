from google.adk.agents import Agent
from .sub_agent.tax_mitra.agent import tax_mitra
from .sub_agent.debt_squasher_agent.agent import debt_squasher_agent
from .sub_agent.sebi_agent.agent import sebi_agent
from .sub_agent.trader_agent.agent import trader_agent
from google.adk.tools.agent_tool import AgentTool

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='hifi_agent',
    description='You are the HiFi Root Agent, the main agent that coordinates the work of all other agents.',
    instruction="""
    You are a Hifi root agent that is responsible for overseeing the work of the other agents.

    Always delegate the task to the appropriate agent. Use your best judgement 
    to determine which agent to delegate to.

    You are responsible for delegating tasks to the following agent:
    - debt_squasher_agent
    - trader_agent
    - tax_mitra

    debt_squasher_agent is responsible for managing debt and financial obligations.
    trader_agent is responsible for managing stock market and financial market related tasks [Trader].
    tax_mitra is responsible for managing tax filing and tax related tasks [Tax].

    You also have access to the following tools:
    - sebi_agent

    sebi_agent is responsible for provinding financial advice according to India's [SEBI] regulations and India specific financial advice.


    """,
    sub_agents=[
        debt_squasher_agent,
        trader_agent,
        tax_mitra,
    ],
    tools=[
        AgentTool(sebi_agent)
    ]
    )