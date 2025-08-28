import finnhub
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from dateutil.relativedelta import relativedelta
from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex

load_dotenv()
finnhub_client_token = os.getenv('FINHUB_API_KEY')
finnhub_client = finnhub.Client(api_key=finnhub_client_token)

def get_market_news():
    res = finnhub_client.general_news('general', min_id=20)
    
    with open('cogs/data/general.json', 'w') as file:
        json.dump(res, file, indent=4)



def get_company_news(symbol: str, months: int):
    today = datetime.today()
    past_date = today - relativedelta(months=months)
    today_f = today.strftime('%Y-%m-%d')
    past_date_f = past_date.strftime('%Y-%m-%d')

    res = finnhub_client.company_news(symbol=symbol, _from=past_date_f, to=today_f)
    
    with open('cogs/data/company.json', 'w') as file:
        json.dump(res, file, indent=4)

get_market_news()
get_company_news('AAPL', 3)