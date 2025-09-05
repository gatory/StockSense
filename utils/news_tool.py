from datetime import datetime
import json
# import news_puller
from . import news_puller
from .news_extractors import NewsExtractor
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Response, StorageContext
# from news_extractors import NewsExtractor
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from llama_index.core.response.pprint_utils import pprint_response
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

client = chromadb.PersistentClient('./chromadb_storage')

def pull_updated_news(symbol):
    general_persist=False
    company_persist=False
    with open('./utils/data/general_news.json', 'r') as file:
        data = json.load(file)
        timestamp = data['timestamp']
        
        curr_time = datetime.now().strftime('%Y-%m-%d')
        general_persist=curr_time != timestamp
        if general_persist:
            news_puller.pull_general_news()

    if symbol:
        with open('./utils/data/company_news.json', 'r') as file:
            data = json.load(file)
            timestamp = data['timestamp']
            sym = data['symbol']
        
        curr_time = datetime.now().strftime('%Y-%m-%d')
        company_persist=curr_time != timestamp or sym != symbol
        if company_persist:
            news_puller.pull_company_news(symbol=symbol)

    return general_persist, company_persist

def load_docs_and_index(embed_model, general_persist, company_persist):
        indices = []
        
        general_collection = client.get_or_create_collection(name='general')
        general_docs = SimpleDirectoryReader(
            input_files=["./utils/data/general_news.json"],
            file_extractor={".json": NewsExtractor()}
        ).load_data()
        vector_store = ChromaVectorStore(chroma_collection=general_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        if general_persist:
            index = VectorStoreIndex.from_documents(
                general_docs,
                storage_context=storage_context,
                embed_model=embed_model
            )
        else:
            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store, 
                storage_context=storage_context,
                embed_model=embed_model
            )

        indices.append(index)

        company_collection = client.get_or_create_collection(name='company')
        company_docs = SimpleDirectoryReader(
            input_files=["./utils/data/company_news.json"],
            file_extractor={".json": NewsExtractor()}
        ).load_data()
        vector_store = ChromaVectorStore(chroma_collection=company_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        if company_persist:
            index = VectorStoreIndex.from_documents(
                company_docs,
                storage_context=storage_context,
                embed_model=embed_model
            )
        else:
            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                storage_context=storage_context,
                embed_model=embed_model
            )
        indices.append(index)

        return indices

def get_news_info(query: str, llm, embed_model, symbol=None) -> str:
    if not llm or not embed_model:
        raise Exception('No llm or embed model')
    
    general_persist, company_persist = pull_updated_news(symbol=symbol)
    indices = load_docs_and_index(embed_model=embed_model, 
                                  general_persist=general_persist,
                                  company_persist=company_persist)
    
    if len(indices) != 2:
        raise Exception('No indexes loaded')
    
    general_query_engine = indices[0].as_query_engine(llm=llm)
    general_tool = QueryEngineTool.from_defaults(
        query_engine=general_query_engine,
        description='Using general market news to provide response'
    )
    query_engine_tools = [general_tool]

    if symbol:
        company_query_engine = indices[1].as_query_engine(llm=llm)
        company_tool = QueryEngineTool.from_defaults(
            query_engine=company_query_engine,
            description='Targeting a specific company news to provide response'
        )
        query_engine_tools.append(company_tool)
    
    query_engine = RouterQueryEngine(
        selector=LLMSingleSelector.from_defaults(llm=llm),
        query_engine_tools=query_engine_tools,
        llm=llm
    )

    res: Response = query_engine.query(query)
    pprint_response(response=res, show_source=True)

    return res.response
    
def main():
    pull_updated_news('TSLA')
    llm = Ollama(model='llama3.2:1b', request_timeout=600)

    embed_model = HuggingFaceEmbedding('BAAI/bge-base-en-v1.5')
    res = get_news_info('What companies is the main headline today?', llm=llm, embed_model=embed_model, symbol=None)

    print(f"Final result: {res}")

if __name__ == '__main__':
    main()