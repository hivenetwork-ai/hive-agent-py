from hive_agent import HiveAgent
from dotenv import load_dotenv
load_dotenv()
my_agent = HiveAgent(
    name="my_agent",
    functions=[],
    instruction="your instructions for this agent's goal",
)
my_agent.run()