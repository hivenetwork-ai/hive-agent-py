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
        "llama-index==0.10.59",
        "llama-index-llms-anthropic==0.1.16",
        "llama-index-llms-mistralai==0.1.19",
        "llama-index-llms-ollama==0.2.2",
        "llama-index-llms-openai==0.1.27",
        "chromadb==0.5.5",
        "langtrace-python-sdk",
        "llama-index-vector-stores-chroma==0.1.10",
        "llama-index-vector-stores-pinecone==0.1.8",
        "llama-index-multi-modal-llms-openai==0.1.8"
    ],
    extras_require={
        "web3": ["web3==6.15.1", "py-solc-x==2.0.2", "eth-account==0.11.0"],
    },
    python_requires=">=3.11",
)
