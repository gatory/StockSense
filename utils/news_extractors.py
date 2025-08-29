from llama_index.core.readers.base import BaseReader
from llama_index.core import Document
import json

class NewsExtractor(BaseReader):
    def load_data(self, file, extra_info=None):
        with open(file, "r") as f:
            article = json.load(f)
        docs = []
        for each in article:
            docs.append(Document(text=f"Category: {each['category']}, 
                                 Headline: {each['headline']},
                                 Related: {each['related']},
                                 Source: {each['source']},
                                 Summary: {each['summary']},
                                 URL: {each['url']}", 
                                 extra_info=extra_info or {}))
        return docs
    
    