from google.adk.agents import Agent
from .sub_agent.tax_mitra.agent import tax_mitra
from .sub_agent.debt_squasher_agent.agent import debt_squasher_agent
from .sub_agent.sebi_agent.agent import sebi_agent
from .sub_agent.fi_mcp_agent.agent import build_fi_mcp_agent
from .sub_agent.trader_agent.agent import trader_agent
from google.adk.tools.agent_tool import AgentTool

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='hifi_agent',
    description='You are the HiFi Root Agent, the main agent that coordinates the work of all other agents.',
    instruction="""
    You are a Hifi root agent that is responsible for overseeing the work of the other agents.
    IMPORTANT:
    - After first user message transfer to fi_mcp_agent and call all the available tools directly.
    - If the fi mcp server asks for authetication then only respond user with: "Please connect to Fi MCP by clicking on Fi Logo on the Top Bar and message done once connected"
    - Do not Provide fi_mcp authentication url to the user.
    - Always call all the fi_mcp_agent tools as soon as the user is authenticated with fi, or is already autheticated with fi.

    Always delegate the task to the appropriate agent. Use your best judgement 
    to determine which agent to delegate to.

    You are responsible for delegating tasks to the following agent:
    - debt_squasher_agent
    - trader_agent
    - tax_mitra
    - fi_mcp_agent

    debt_squasher_agent is responsible for managing debt and financial obligations.
    trader_agent is responsible for managing stock market and financial market related tasks [Trader].
    tax_mitra is responsible for managing tax filing and tax related tasks [Tax].
    fi_mcp_agent is responsible for fetching financial data of user and provide financial advice. [Financial Advisor]
    You also have access to the following tools:
    - sebi_agent

    sebi_agent is responsible for provinding financial advice according to India's [SEBI] regulations and India specific financial advice.


    """,
    sub_agents=[
        debt_squasher_agent,
        trader_agent,
        tax_mitra,
        sebi_agent,
        build_fi_mcp_agent()
    ],
    tools=[
    ]
    )