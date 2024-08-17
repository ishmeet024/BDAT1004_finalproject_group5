import requests
from pymongo import MongoClient
from datetime import datetime, timedelta
import time

def fetch_crypto_prices(api_token, api_code):
    base_url = 'https://api.coinbase.com/v2/prices'
    currencies = ['BTC', 'ETH', 'USDT', 'XRP', 'BNB', 'USDC', 'DOGE', 'ADA', 'SOL', 'TRX', 'MATIC', 'LTC', 'DOT', 'TON',
                  'WBTC', 'AVAX', 'BCH', 'DAi', 'SHIB', 'LINK', 'XLM', 'BUSD', 'UNI', 'XMR', 'ETC', 'OKB',
                  'FIL', 'MNT', 'LDO', 'APT', 'ARB', 'CRO', 'VET', 'NEAR', 'QNT', 'MKR', 'AAVE', 'GRT',
                  'OP', 'ALGO', 'EGLD', 'SAND', 'STX', 'THETA', 'EOS', 'XDC', 'XTZ', 'IMX', 'SNX', 'APE']  

    crypto_data = []

    for currency in currencies:
        url = f"{base_url}/{currency}-USD/spot"
        headers = {
            'Authorization': f'Bearer {api_token}',
            'CB-ACCESS-SIGN': api_code,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            symbol = data['data']['base']
            price = float(data['data']['amount'])
            timestamp = datetime.utcnow().isoformat()  

            crypto_data.append({
                'timestamp': timestamp,
                'symbol': symbol,
                'price': price
            })
        else:
            print(f"Failed to fetch {currency} price. Status code: {response.status_code}")

    return crypto_data

def save_data_to_db(data_to_save):
    client = MongoClient(
    "mongodb+srv://ishmeet:Bdat2024@finalproject-cluster.vgvua.mongodb.net/?retryWrites=true&w=majority&appName=finalproject-cluster")
    db = client['crypto']
    collection = db['crypto_table']
    
    result = collection.insert_many(data_to_save)
    print(f"{len(result.inserted_ids)} records inserted into MongoDB.")

if __name__ == "__main__":
    api_key = 'bayisvyp'
    api_secret = '68bb6e5f-0148-4dae-858b-800962ca5200'

    while True:
        crypto_prices = fetch_crypto_prices(api_key, api_secret)
        save_data_to_db(crypto_prices)
        print('Data stored successfully')
        
        # Fetch data every 24 hours
        time.sleep(24 * 60 * 60)  # Sleep for 24 hours
        print('Data fetching process completed')
