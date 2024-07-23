from setuptools import setup, find_packages

setup(
    name="hive-agent",
    version="0.0.1",
    author="Tomisin Jenrola",
    description="Hive Network's Agent Node & SDK",
    packages=find_packages(include=["hive_agent", "hive_agent.*"]),
    install_requires=[
        "fastapi==0.109.1",
        "uvicorn==0.23.2",
        "python-dotenv==1.0.1",
        "llama-index==0.10.35",
        "llama-index-llms-anthropic==0.1.11",
        "llama-index-llms-mistralai==0.1.12",
        "llama-index-llms-ollama==0.1.5",
        "llama-index-llms-openai==0.1.27",
        "langtrace-python-sdk",
    ],
    extras_require={
        "web3": ["web3==6.15.1", "py-solc-x==2.0.2", "eth-account==0.11.0"],
    },
    python_requires=">=3.11",
)
