![](./assets/logo.jpg)

# Hive Agent Kit

This library provides you with an easy way to create and run Hive Agents.

Join our Discord community for support and discussion.

[![](https://dcbadge.limes.pink/api/server/vnJvW4wZp9)](https://discord.gg/vnJvW4wZp9)

## Supported Large Language Models (LLMs)
- OpenAI
  - gpt-4o
  - gpt-4o-mini
  - gpt-4-turbo
  - gpt-4
  - gpt-3.5-turbo
  - gpt-3.5-turbo-instruct
- Anthropic
  - claude-3-opus-20240229
  - claude-3-sonnet-20240229
  - claude-3-haiku-20240307
- MistralAI
   - mistral-large-latest
   - mistral-small-latest
   - open-mixtral-8x22b
   - codestral-latest
- Popular open source LLMs
   - llama3.1:latest
   - llava
   - gemma2:2b
   - gemma2
   - gemma:7b
   - gemma:2b
   - gemma2:27b
   - codegemma
   - mistral-nemo
   - deepseek-coder-v2
   - phi3:mini
   - phi3:medium
   - command-r
   - command-r-plus
   - and any supported by [Ollama](https://ollama.com/library)

## Project Requirements

- Python >= 3.11

## Installation

You can either directly install from pip:

```sh
pip install git+https://github.com/hivenetwork-ai/hive-agent-py.git@main
```

Or add it to your _requirements.txt_ file:

```sh
hive-agent @ git+https://github.com/hivenetwork-ai/hive-agent-py@main
```

### Optional Dependencies

To install with the optional web3 dependencies, you can specify them as follows:

```sh
pip install git+https://github.com/hivenetwork-ai/hive-agent-py.git@main#egg=hive-agent[web3]
```

Or add it to your _requirements.txt_ file:

```sh
hive-agent[web3] @ git+https://github.com/hivenetwork-ai/hive-agent-py@main
```

## Environment Setup

You need to specify an `OPENAI_API_KEY` in a _.env_ file in this directory.

Make a copy of the [.env.example](.env.example) file and rename it to _.env_.

## Configuration Setup

To use a configuration file with your `HiveAgent`, follow these steps:

1. **Create a Configuration File**:

   - Create a TOML file (e.g., `hive_config.toml`) in your project directory. (See [hive_config_example.toml](./hive_config_example.toml)).

2. **Specify the Configuration Path**:

   - When creating a `HiveAgent` instance, provide the relative or absolute path to your configuration file.

   ```python
   from hive_agent import HiveAgent

   import os

   def get_config_path(filename):
       return os.path.abspath(os.path.join(os.path.dirname(__file__), filename))

   simple_agent = HiveAgent(
       name="Simple Agent",
       functions=[],
       instruction="your instructions for this agent's goal",
       config_path=get_config_path("hive_config.toml") # ./hive_config.toml works too
   )
   ```

## Usage

First import the `HiveAgent` class:

```python
from hive_agent import HiveAgent
```

Load your environment variables:

```python
from dotenv import load_dotenv
load_dotenv()
```

Then create a HiveAgent instance:

```python
my_agent = HiveAgent(
    name="my_agent",
    functions=[],
    instruction="your instructions for this agent's goal",
)
```

Then, run your agent:

```python
my_agent.run()
```

Finally, call the API endpoint, `/api/v1/chat`, to see the result:

```sh
curl --location 'localhost:8000/api/v1/chat' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "user123",
    "session_id": "session123",
    "chat_data": {
        "messages": [
            { "role": "user", "content": "Who is Satoshi Nakamoto?" }
        ]
    }
}'
```

### Adding tools

You can create tools that help your agent handle more complex tasks. Here's an example:

````python
import os
from typing import Optional, Dict
from web3 import Web3
from hive_agent import HiveAgent
from dotenv import load_dotenv

load_dotenv()

rpc_url = os.getenv("RPC_URL") # add an ETH Mainnet HTTP RPC URL to your `.env` file

def get_transaction_receipt(transaction_hash: str) -> Optional[Dict]:
    """
    Fetches the receipt of a specified transaction on the Ethereum blockchain and returns it as a dictionary.

    :param transaction_hash: The hash of the transaction to fetch the receipt for.
    :return: A dictionary containing the transaction receipt details, or None if the transaction cannot be found.
    """
    web3 = Web3(Web3.HTTPProvider(rpc_url))

    if not web3.is_connected():
        print("unable to connect to Ethereum")
        return None

    try:
        transaction_receipt = web3.eth.get_transaction_receipt(transaction_hash)
        return dict(transaction_receipt)
    except Exception as e:
        print(f"an error occurred: {e}")
        return None

if __name__ == "__main__":
    my_agent = HiveAgent(
        name="my_agent",
        functions=[get_transaction_receipt]
    )

    my_agent.run()

    """
    [1] send a request:

    ```
    curl --location 'localhost:8000/api/v1/chat' \
    --header 'Content-Type: application/json' \
    --data '{
        "user_id": "user123",
        "session_id": "session123",
        "chat_data": {
            "messages": [
                { "role": "user", "content": "Which address initiated this transaction - 0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060?" }
            ]
        }
    }'
    ```

    [2] result:

    The address that initiated the transaction with hash 0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060 is 0xA1E4380A3B1f749673E270229993eE55F35663b4.
    """
````

### Adding Retriever

You can add retriever tools to create vector embeddings and retrieve semantic information. It will create vector index for every pdf documents under 'hive-agent-data/files/user' folder and can filter files with required_exts parameter.

- Hive agent supports ".md", '.mdx' ,".txt", '.csv', '.docx', '.pdf' file types.
- Hive agent supports 4 type of retriever (basic, chroma, pinecone-serverless, pinecone-pod) and controlled with retrieval_tool parameter.

````python
import os
from typing import Optional, Dict
from web3 import Web3
from hive_agent import HiveAgent
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    my_agent = HiveAgent(
        name="retrieve-test",
        functions=[],
        retrieve = True,
        required_exts = ['.md'],
        retrieval_tool='chroma'
    )

    my_agent.run()

    """
    [1] send a request:

    ```
    curl --location 'localhost:8000/api/v1/chat' \
    --header 'Content-Type: application/json' \
    --data '{
        "user_id": "user123",
        "session_id": "session123",
        "chat_data": {
            "messages": [
                { "role": "user", "content": "Which endpoints should I call to create vector index?" }
            ]
        }
    }'
````

### Tutorial

The complete tutorial can be found at [./tutorial.md](./tutorial.md).

## Contributing

### Setup

If you want to contribute to the codebase, you would need to set up your dev environment. Follow these steps:

- Create a new file called .env
- Copy the contents of [.env.example](.env.example) into your new .env file
- API keys for third-party tools are not provided.
  - `OPENAI_API_KEY` from OpenAI
- If you don't have Poetry installed, you can install it using the following commands:

```sh
curl -sSL https://install.python-poetry.org | python3 -

export PATH="$HOME/.local/bin:$PATH"
```

- Activate the Virtual Environment created by Poetry with the following command:

```sh
poetry shell
```

- Install dependencies.

```sh
poetry install --no-root
```

### Testing

- Make sure you're in the `tests/` directory:

```sh
cd tests/
```

- Run the test suite:

```sh
pytest
```

- Run tests for a specific module:

```sh
pytest tests/path/to/test_module.py
```

- Run with verbose output:

```sh
pytest -v
```

- Run with a detailed output of each test (including print statements):

```sh
pytest -s
```

- Run with coverage report:

```sh
pip install coverage pytest-cov
pytest  --cov --cov-report=html
```

Reports file `tests/htmlcov/index.html`

## API Doc

Open [http://localhost:8000/docs](http://localhost:8000/docs) with your browser to see the Swagger UI of the API.

## Learn More

<https://hivenetwork.ai>
