from llama_index.core import SimpleDirectoryReader 
from news_extractors import NewsExtractor
from datetime import datetime
from news_puller import pull_general_news, pull_company_news
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.response.pprint_utils import pprint_response
import json
import chromadb
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

chroma_client = chromadb.PersistentClient('./chromadb')

def has_loaded(sym=None):
    current_time = datetime.now().strftime("%Y-%m-%d")
    if sym:
        with open('./utils/data/company_news.json', 'r') as file:
            data = json.load(file)
            timestamp = data.get('timestamp')
            symbol = data.get('symbol')
        return current_time == timestamp and sym == symbol
    
    with open('./utils/data/general_news.json', 'r') as file:
        timestamp = json.load(file).get('timestamp')
        return current_time == timestamp

def add_document_to_chroma(collection, document, embed_model):
    for doc in document:
        headline = doc.extra_info.get('headline', '')
        summary = doc.extra_info.get('summary', '')
        related = doc.extra_info.get('related', '')
        doc_id = doc.extra_info.get('id', '')

    combined_text = f"{headline}\n\n{summary}\n\n{related}"

    collection.add(
        document=[combined_text],
        metadata=[doc.extra_info],
        ids=[str(doc_id)],
        embeddings=embed_model.encode([combined_text])
    )

def ingest_news(embed_model, symbol=None):
    print('Checking for new news...')
    if not has_loaded(sym=symbol):
        print('New news not loaded, pulling data...')
        if symbol:
            pull_company_news(symbol=symbol)
        pull_general_news()
        
        print("Reading new documents...")
        general_doc = SimpleDirectoryReader(input_files=["./utils/data/general_news.json"],
                                            file_extractor={".json", NewsExtractor()})
        company_doc = SimpleDirectoryReader(input_files=["./utils/data/company_news.json"],
                                            file_extractor={".json", NewsExtractor()})

        print("Adding documents to ChromaDB collections...")
        general_collection = chroma_client.get_or_create_collection('general_collection')
        company_collection = chroma_client.get_or_create_collection('company_collection')

        add_document_to_chroma(general_collection, general_doc, embed_model=embed_model)
        add_document_to_chroma(company_collection, company_doc, embed_model=embed_model)
    else:
        print("Collections are up-to-date. Skipping ingestion.")

def get_news_info(query: str, llm, embed_model, symbol=None) -> str:

    general_collection = chroma_client.get_or_create_collection('general_collection')
    company_collection = chroma_client.get_or_create_collection('company_collection')

    general_tool = QueryEngineTool.from_defaults(
        query_engine=general_collection,
        description='General Market News'
    )
    company_tool = QueryEngineTool.from_defaults(
        query_engine=company_collection,
        description='Company Specific News'
    )

    query_engine = RouterQueryEngine(
        selector=LLMSingleSelector.from_defaults(llm=llm),
        query_engine_tools=[general_tool, company_tool],
        llm=llm
    )

    res = query_engine.query(query)
    return res.response
              


def main():
    llm = Ollama(model='qwen3:8b', request_timeout=600)
    embed_model = HuggingFaceEmbedding('BAAI/bge-base-en-v1.5')
    ingest_news(embed_model=embed_model, symbol='AAPL')
    print(get_news_info('What is the best stock to by?', llm=llm))
    

if __name__ == "__main__":
    main()