import os
from dotenv import load_dotenv
import json
import finnhub
from datetime import datetime
from dateutil.relativedelta import relativedelta

load_dotenv()
finnhub_api_key = os.getenv('FINHUB_API_KEY')

finnhub_client = finnhub.Client(api_key=finnhub_api_key)

def pull_general_news():
    news = finnhub_client.general_news('general', min_id=0)
    data = {
        'timestamp': datetime.now().strftime("%Y-%m-%d"),
        'news': news 
    }
    
    with open('./utils/data/general_news.json', 'w') as file:
        json.dump(data, file, indent=4)    


def pull_company_news(symbol: str, x_months=3):
    today = datetime.today()
    current_date = today.strftime('%Y-%m-%d')
    past_date = (today - relativedelta(months=x_months)).strftime('%Y-%m-%d')

    news = finnhub_client.company_news(symbol=symbol, _from=past_date, to=current_date)
    data = {
        'timestamp': datetime.now().strftime("%Y-%m-%d"),
        'symbol': symbol,
        'news': news 
    }

    with open('./utils/data/company_news.json', 'w') as file:
        json.dump(data, file, indent=4)

def main(): 
    pull_general_news()
    pull_company_news('TSLA')
    

if __name__ == "__main__":
    main()