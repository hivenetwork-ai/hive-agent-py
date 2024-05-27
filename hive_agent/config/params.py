from dotenv import load_dotenv
import os
load_dotenv()
cache_folder = "cache_folder"
embedding_model_folder = os.path.join(cache_folder,"embedding_model")

# Embedding model params
# Define params
embedding_service = "COHERE"
embedding_model_name = "embed-english-light-v3.0"

# Model config
AI21_KEY = os.getenv("AI21_KEY")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY") # Max usage 10$
CLARIFAI_KEY = os.getenv("CLARIFAI_KEY")
COHERE_KEY = os.getenv("COHERE_KEY") # Cohere limited calls per minutes
GRADIENT_KEY = os.getenv("GRADIENT_KEY") # Cohere limited calls per minutes
GROQ_KEY = os.getenv("GROQ_KEY") # 30 requests/min
KONKO_KEY = os.getenv("KONKO_KEY") # 5$ starter bundle
LLAMAAPI_KEY = os.getenv("LLAMAAPI_KEY") # 5$ starter bundle
OPENAI_KEY = os.getenv("OPENAI_KEY") # 5$ starter bundle
PERPLEXITY_KEY = os.getenv("PERPLEXITY_KEY") # Required payment
TOGETHER_KEY = os.getenv("TOGETHER_KEY") # 25$ starter bundle
GEMINI_KEY = os.getenv("GEMINI_KEY") # Free to use
VOYAGE_KEY = os.getenv("VOYAGE_KEY") # Free for 50M first tokens
NOMIC_KEY = os.getenv("NOMIC_KEY") # Free for 50M first tokens
LLAMAPARSE_KEY = os.getenv("LLAMAPARSE_KEY") # https://cloud.llamaindex.ai/parse


# Define service
supported_services = {
    "AI21":{
        "CHAT_MODELS":[],
        "EMBBEDDING_MODELS":[],
        "KEY" : AI21_KEY
    },
    "ANTHROPIC":{
        "CHAT_MODELS":["claude-3-opus-20240229","claude-3-sonnet-20240229","claude-3-haiku-20240307"],
        "EMBBEDDING_MODELS":[],
        "KEY": ANTHROPIC_KEY
        # List models: https://docs.anthropic.com/claude/docs/models-overview
    },
    "CLARIFAI":{
        "CHAT_MODELS":[],
        "EMBBEDDING_MODELS":[],
        "KEY": CLARIFAI_KEY
    },
    "COHERE":{
        "CHAT_MODELS":["command-light","command","command-r","command-r-plus"],
        # List models: https://docs.cohere.com/docs/command-beta
        "EMBBEDDING_MODELS":["embed-english-v3.0","embed-multilingual-v3.0","embed-english-light-v3.0","embed-multilingual-light-v3.0"],
        # List embbeding: https://docs.cohere.com/reference/embed
        "KEY": COHERE_KEY

    },
    "GRADIENT":{
        "CHAT_MODELS":[],
        "EMBBEDDING_MODELS":[],
        "KEY": GRADIENT_KEY
    },
    "GROQ":{
        "CHAT_MODELS":["llama2-70b-4096","mixtral-8x7b-32768","gemma-7b-it","llama3-8b-8192"],
        "EMBBEDDING_MODELS":[],
        "KEY": GROQ_KEY
    },

    "KONKO":{
        "CHAT_MODELS":["meta-llama/llama-2-13b-chat","mistralai/mixtral-8x7b-instruct-v0.1","zero-one-ai/yi-34b-chat"],
        "EMBBEDDING_MODELS":[],
        "KEY": KONKO_KEY
        # List model: https://docs.konko.ai/docs/list-of-models
    },
    "LLAMAAPI":{
        "CHAT_MODELS":[],
        "EMBBEDDING_MODELS":[],
        "KEY": LLAMAAPI_KEY
    },
    "OPENAI":{
        "CHAT_MODELS":["gpt-4-turbo-2024-04-09","gpt-4-0125-preview","gpt-4-32k","gpt-4","gpt-3.5-turbo-0125","gpt-3.5-turbo-instruct"],
        "EMBBEDDING_MODELS":["text-embedding-3-large","text-embedding-3-small","text-embedding-ada-002"],
        "KEY": OPENAI_KEY
        # List model: https://platform.openai.com/docs/models/continuous-model-upgrades
        # List embedding: https://platform.openai.com/docs/models/embeddings
    },
    "PERPLEXITY":{
        "CHAT_MODELS":["llama-2-13b-chat","llama-2-70b-chat","mistral-7b-instruct","pplx-7b-chat-alpha","pplx-70b-chat-alpha"],
        "EMBBEDDING_MODELS":[],
        "KEY": PERPLEXITY_KEY
        # List model: https://docs.perplexity.ai/docs/model-cards
    },
    "TOGETHER":{
        "CHAT_MODELS":["zero-one-ai/Yi-34B-Chat","cognitivecomputations/dolphin-2.5-mixtral-8x7b","mistralai/Mistral-7B-Instruct-v0.2","NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO","Qwen/Qwen1.5-32B-Chat"],
        # List model: https://docs.together.ai/docs/inference-models
        "EMBBEDDING_MODELS":["togethercomputer/m2-bert-80M-8k-retrieval","togethercomputer/m2-bert-80M-32k-retrieval","BAAI/bge-large-en-v1.5","BAAI/bge-base-en-v1.5","sentence-transformers/msmarco-bert-base-dot-v5"],
        # List embbeding: https://docs.together.ai/docs/embedding-models
        "KEY": TOGETHER_KEY

    },
    "GEMINI":{
        "CHAT_MODELS":["models/gemini-1.5-pro-latest","models/gemini-pro","models/gemini-pro-vision"],
        "EMBBEDDING_MODELS":[],
        "KEY": GEMINI_KEY
        # List model: https://ai.google.dev/models/gemini
        # Gemini Pro 60 requests/min
    },
    "QDRANT":{
        "CHAT_MODELS":[],
        "EMBBEDDING_MODELS":["BAAI/bge-small-en-v1.5","sentence-transformers/all-MiniLM-L6-v2","nomic-ai/nomic-embed-text-v1.5","BAAI/bge-base-en-v1.5","mixedbread-ai/mxbai-embed-large-v1"],
        "KEY": ""
        # Qdrant Embedding: https://qdrant.github.io/fastembed/examples/Supported_Models/
    },
    "VOYAGE":{
        "CHAT_MODELS":[],
        "EMBBEDDING_MODELS":["voyage-2","voyage-large-2","voyage-law-2","voyage-code-2"],
        "KEY": VOYAGE_KEY
        # Embedding: https://docs.voyageai.com/docs/pricing
    },
    "NOMIC":{
        "CHAT_MODELS":[],
        "EMBBEDDING_MODELS":["nomic-embed-text-v1","nomic-embed-text-v1.5"],
        "KEY": NOMIC_KEY
        # Embedding: https://docs.nomic.ai/atlas/models/text-embedding
    }
}