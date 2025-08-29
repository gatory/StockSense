from DiscordBot import Discord_Bot
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

llm = Ollama(model='qwen3:8b', request_timeout=600)
embed_model = HuggingFaceEmbedding('BAAI/bge-base-en-v1.5')
temperature = 0.5

def main():
    print("Starting main application")
    client = Discord_Bot(llm, embed_model)
    client.run()

if __name__ == "__main__":
    main()