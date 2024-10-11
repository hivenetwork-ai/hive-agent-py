from setuptools import setup, find_packages

setup(
    name="hive-agent",
    version="0.0.1",
    author="Tomisin Jenrola",
    description="Hive Network's Agent Node & SDK",
    packages=find_packages(include=["hive_agent", "hive_agent.*"]),
    install_requires=[
        "fastapi==0.115.0",
        "uvicorn==0.30.6",
        "python-dotenv==1.0.1",
        "llama-index==0.11.14",
        "llama-index-llms-anthropic==0.3.4",
        "llama-index-llms-mistralai==0.2.5",
        "llama-index-llms-ollama==0.3.3",
        "llama-index-llms-openai==0.2.9",
        "llama-index-llms-gemini==0.3.5",
        "llama-index-multi-modal-llms-openai==0.2.1",
        "llama-index-vector-stores-chroma==0.2.0",
        "llama-index-vector-stores-pinecone==0.2.1",
        "llama-index-readers-s3==0.2.0",
        "chromadb==0.5.5",
        "langtrace-python-sdk",
        "asyncpg==0.29.0",
        "openpyxl==3.1.5",
        "docx2txt==0.8",
        "xlrd==2.0.1",
    ],
    extras_require={
        "web3": ["web3==7.2.0", "py-solc-x==2.0.3", "eth-account==0.13.3"],
    },
    python_requires=">=3.11",
)
