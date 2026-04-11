import os
import sys
import json
from dotenv import load_dotenv
from multi_doc_chat.utils.config_loader import load_config
from langchain_groq import ChatGroq
from multi_doc_chat.logger import GLOBAL_LOGGER as log
from multi_doc_chat.exceptions.custom_exception import DocumentPortalException
from langchain_huggingface import HuggingFaceEmbeddings


class ApiKeyManager:
    REQUIRED_KEYS = ["GROQ_API_KEY"]

    def __init__(self):
        self.api_keys = {}
        raw = os.getenv("GROQ_API_KEY")

        if raw:
            try:
                parsed = json.loads(raw)
                if not isinstance(parsed, dict):
                    raise ValueError("API_KEYS is not a valid JSON object")
                self.api_keys = parsed
                log.info("Loaded API_KEYS from ECS secret")
            except Exception as e:
                log.warning("Failed to parse API_KEYS as JSON", error=str(e))


        for key in self.REQUIRED_KEYS:
            if not self.api_keys.get(key):
                env_val = os.getenv(key)
                if env_val:
                    self.api_keys[key] = env_val
                    log.info(f"Loaded {key} from individual env var")

        # Final check
        missing = [k for k in self.REQUIRED_KEYS if not self.api_keys.get(k)]
        if missing:
            log.error("Missing required API keys", missing_keys=missing)
            raise DocumentPortalException("Missing API keys", sys)

        log.info("API keys loaded", keys={k: v[:6] + "..." for k, v in self.api_keys.items()})


    def get(self, key: str) -> str:
        val = self.api_keys.get(key)
        if not val:
            raise KeyError(f"API key for {key} is missing")
        return val


class ModelLoader:
    """
    Loads embedding models and LLMs based on config and environment.
    """

    def __init__(self):
        if os.getenv("ENV", "local").lower() != "production":
            load_dotenv()
            log.info("Running in LOCAL mode: .env loaded")
        else:
            log.info("Running in PRODUCTION mode")

        self.api_key_mgr = ApiKeyManager()
        self.config = load_config()
        log.info("YAML config loaded", config_keys=list(self.config.keys()))


    def load_embeddings(self):
        """
        Load and return embedding model from Hugging Face Embeddings.
        """
        try:
            model_name = self.config["embedding_model"]["model_name"]
            log.info("Loading embedding model", model=model_name)
            return HuggingFaceEmbeddings(model=model_name) # check for error here 
        except Exception as e:
            log.error("Error loading embedding model", error=str(e))
            raise DocumentPortalException("Failed to load embedding model", sys)

    def load_llm(self):
        """
        Load and return the configured LLM model.
        """
        # This correctly gets the 'groq' dictionary from your YAML
        llm_config = self.config.get('llm', {}).get('groq', {})
        
        # Check if the dictionary actually contains data
        provider = llm_config.get("provider")
        
        if not provider:
            log.error("LLM provider not found in config", provider=provider)
            raise ValueError(f"LLM provider '{provider}' not found in config")

        # Pull values directly from llm_config
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature", 0.2)
        max_tokens = llm_config.get("max_output_tokens", 2048)

        log.info("Loading LLM", provider=provider, model=model_name)

        if provider == "groq":
            return ChatGroq(
                model=model_name,
                api_key=self.api_key_mgr.get("GROQ_API_KEY"),
                temperature=temperature,
                max_tokens=max_tokens
            )

        else:
            log.error("Unsupported LLM provider", provider=provider)
            raise ValueError(f"Unsupported LLM provider: {provider}")


if __name__ == "__main__":
    loader = ModelLoader()

    # Test Embedding
    embeddings = loader.load_embeddings()
    print(f"Embedding Model Loaded: {embeddings}")
    result = embeddings.embed_query("Hello, how are you?")
    print(f"Embedding Result: {result}")

    # Test LLM
    llm = loader.load_llm()
    print(f"LLM Loaded: {llm}")
    result = llm.invoke("Hello, how are you?")
    print(f"LLM Result: {result.content}")

"""This is the "Orchestrator" boilerplate. While the previous files were individual tools (the Logger, the Error Investigator, the Config Loader), this code is the Manager that brings them all together to actually start the AI.
What it does in simple words:
The Key Master (ApiKeyManager): It hunts for your secret API keys (like Groq). It's smart enough to look in two places: a JSON file (common in professional cloud setups like AWS) or your basic .env file. It even hides the middle of your keys in the logs so they stay secret.
The Environment Checker: It looks to see if you are on your personal laptop ("local") or a real server ("production"). If you're local, it automatically loads your .env file for you.
The Model Shifter (ModelLoader):
Embeddings: It reads your YAML file, sees you want Hugging Face, and "plugs in" that specific model.
The Brain (LLM): It looks at your config to see which AI you want (like Llama 3 via Groq) and sets it up with the right "creativity" (temperature) and speed.
The Safety Net: It uses that DocumentPortalException you saw earlier. If a key is missing or a model fails to load, it doesn't just crash—it gives a detailed report.
Is this boilerplate?
Yes. This is a classic "Model Factory" pattern.
Why use it? Instead of writing 50 lines of setup code at the top of every single file in your project, you just write loader = ModelLoader() and llm = loader.load_llm().
Can you copy-paste it? Yes, but notice it's very specific to Groq and Hugging Face. If you switched to OpenAI or Anthropic later, you'd only have to change the code in this one file, and the rest of your app would keep working perfectly."""