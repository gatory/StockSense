from llama_index.core.readers.base import BaseReader
from llama_index.core import Document
import json

class NewsExtractor(BaseReader):
    def load_data(self, file, extra_info=None):
        with open(file, "r") as f:
            data = json.load(f)
            news = data['news']
        docs = []
        for each in news:
            doc = Document(
                text=f"headline: {each['headline']}\nsummary: {each['summary']}\n\n",
                extra_info={
                    'category': each['category'],
                    'datetime': each['datetime'],
                    'headline': each['headline'],
                    'id': each['id'],
                    'image': each['image'],
                    'related': each['related'],
                    'source': each['source'],
                    'summary': each['summary'],
                    'url': each['url'],
                }
            )
            docs.append(doc)
        return docs