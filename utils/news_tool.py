import json
import finnhub
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
from dotenv import load_dotenv

last_action_time_str = "2025-08-28T09:15:00" 
last_action_time = datetime.fromisoformat(last_action_time_str)
last_symbol = 'AAPL'

def pull_general_news(finnhub_api_key):
    finnhub_client = finnhub.Client(api_key=finnhub_api_key)

    news = finnhub_client.general_news('general', min_id=0)
    with open('./utils/data/general_news.json', 'w') as file:
        json.dump(news, file, indent=4)

def pull_company_news(finnhub_api_key, symbol: str, x_months):
    finnhub_client = finnhub.Client(api_key=finnhub_api_key)

    today = datetime.today()
    current_date = today.strftime('%Y-%m-%d')
    past_date = (today - relativedelta(months=x_months)).strftime('%Y-%m-%d')

    news = finnhub_client.company_news(symbol=symbol, _from=past_date, to=current_date)
    with open('./utils/data/company_news.json', 'w') as file:
        json.dump(news, file, indent=4)

def get_news_info(query: str, llm, embed_model, symbol=None) -> str:
    if not llm or not embed_model:
        raise Exception("No llm orembed_model")
    
    today = datetime.today().date()

    if last_action_time != today:
        pull_general_news()
    elif last_action_time != today and last_symbol != symbol:
        pull_company_news()
    

    
    
    

def main():
    load_dotenv()
    finnhub_api_key=os.getenv('FINHUB_API_KEY')
    pull_company_news(finnhub_api_key=finnhub_api_key, symbol='AAPL', x_months=3)
    pull_general_news(finnhub_api_key=finnhub_api_key)
    

if __name__ == "__main__":
    main()