from datetime import datetime
import json
import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Response
from news_extractors import NewsExtractor
from news_puller import pull_general_news, pull_company_news
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.response.pprint_utils import pprint_response
import chromadb

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def get_news_info(query: str, llm, embed_model, symbol=None) -> str:
    if not llm or not embed_model:
        raise Exception('No llm or embed_model')

    pull_general_news()
    if symbol:
        pull_company_news(symbol=symbol)

    general_docs = SimpleDirectoryReader(
        input_files=["./utils/data/general_news.json"],
        file_extractor={".json": NewsExtractor()}
    ).load_data()
    
    general_index = VectorStoreIndex.from_documents(
        documents=general_docs,
        embed_model=embed_model
    )
    general_query_engine = general_index.as_query_engine(llm=llm)
    general_tool = QueryEngineTool.from_defaults(
        query_engine=general_query_engine,
        description='Using general market news to provide response'
    )
    
    query_engine_tools = [general_tool]
    
    if symbol:
        company_docs = SimpleDirectoryReader(
            input_files=["./utils/data/company_news.json"],
            file_extractor={".json": NewsExtractor()}
        ).load_data()
        
        company_index = VectorStoreIndex.from_documents(
            documents=company_docs,
            embed_model=embed_model
        )
        
        company_query_engine = company_index.as_query_engine(llm=llm)
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
    llm = Ollama(model='llama3.2:1b', request_timeout=600)
    embed_model = HuggingFaceEmbedding('BAAI/bge-base-en-v1.5')
    res = get_news_info('What does tesla have planed for the future?', llm=llm, embed_model=embed_model, symbol='TSLA')
    print(res)


if __name__ == '__main__':
    main()