import asyncio

from hive_agent import HiveAgent, HiveSwarm
from hive_agent.llms import ClaudeLLM, MistralLLM, OpenAILLM

from dotenv import load_dotenv
# load environment variables from .env file
load_dotenv()

# initialize the LLMs
claude = ClaudeLLM()
mistral = MistralLLM()
gpt = OpenAILLM()

# initialize your agents
pm_agent = HiveAgent(
    name="Project Manager Agent",
    description="This agent acts like a Project Manager on a team",
    instruction="You are a project manager on a software development team and you should provide guidance, "
                "planning, clarity and instruction on how to build the project",
    role="project manager",
    functions=[],
    config_path="./hive_config_example.toml",
)

frontend_developer_agent = HiveAgent(
    name="Frontend Developer Agent",
    description="This agent acts like a Frontend Software Developer on a team and can write React code.",
    instruction="You are a frontend developer on a team that produces clean, working React code in Typescript.",
    role="frontend developer",
    functions=[],
    llm=mistral,
    config_path="./hive_config_example.toml",
)

backend_developer_agent = HiveAgent(
    name="Backend Developer Agent",
    description="This agent acts like a Backend Software Developer on a team and can write server code.",
    instruction="You are a backend developer on a team that produces clean, working server code in Express.js. You "
                "use Typescript as much as possible rather than Javascript.",
    role="backend developer",
    functions=[],
    llm=mistral,
    config_path="./hive_config_example.toml",
)

solidity_developer_agent = HiveAgent(
    name="Smart Contract Engineer Agent",
    description="This agent acts like a Solidity Engineer on a team developing Solidity code.",
    instruction="You are a Solidity smart contract developer on a team that produces clean, working smart contracts in Solidity.",
    role="smart contract developer",
    functions=[],
    llm=claude,
    config_path="./hive_config_example.toml",
)

qa_agent = HiveAgent(
    name="Quality Assurance Engineer Agent",
    description="This agent acts like a QA Engineer on a team and can review code before it is committed",
    instruction="You are a Quality Assurance Engineer on a software team, you need to find bugs in the code given to "
                "you so that the developers can fix them.",
    role="qa engineer",
    functions=[],
    llm=claude,
    config_path="./hive_config_example.toml",
)

# create the swarm
startup_swarm = HiveSwarm(
    name="DeFi Startup",
    description="A swarm of agents that collaborate as members of a DeFi (Decentralized Finance) startup.",
    instruction="You are a DeFi Startup whose goal is to create new DeFi products for your customers.",
    agents=[pm_agent, frontend_developer_agent, backend_developer_agent, solidity_developer_agent, qa_agent],
    config_path="./hive_config_example.toml",
    llm=gpt,
)


async def main():
    print("Welcome to the HiveNetwork.ai CLI. Type 'exit' to quit.")
    while True:
        prompt = input("\n\nEnter your prompt: \n\n")
        if prompt.lower() == "exit":
            break
        response = await startup_swarm.chat(prompt)
        print(response)

if __name__ == "__main__":
    asyncio.run(main())
