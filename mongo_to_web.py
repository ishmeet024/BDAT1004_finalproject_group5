from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
from flask_paginate import Pagination, get_page_args
from math import ceil
from flask import jsonify

app = Flask(__name__)

# MongoDB Connection Setup
client = MongoClient("mongodb+srv://ishmeet:Bdat2024@finalproject-cluster.vgvua.mongodb.net/?retryWrites=true&w=majority&appName=finalproject-cluster")
crypto_db = client['crypto']
crypto_collection = crypto_db['crypto_table']

# DateTime Format Filter for Jinja2
def datetimeformat(value):
    utc_time = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
    eastern_timezone = pytz.timezone('America/New_York')
    edt_time = utc_time.replace(tzinfo=pytz.utc).astimezone(eastern_timezone)
    return edt_time.strftime('%Y-%m-%d %H:%M:%S')

app.jinja_env.filters['datetimeformat'] = datetimeformat

# Pagination Configuration
ITEMS_PER_PAGE = 20

# Function to Fetch Paginated Data
def get_paginated_crypto_data(offset=0, per_page=ITEMS_PER_PAGE):
    return list(crypto_collection.find().skip(offset).limit(per_page))

def get_paginated_data(offset=0):
    return crypto_collection.find().skip(offset).limit(ITEMS_PER_PAGE)

# Route for the Charts Page
@app.route('/charts')
def charts():
    # Line Chart Data (Bitcoin Prices Over Time)
    bitcoin_data = [
        {'timestamp': entry['timestamp'], 'price': entry['price']}
        for entry in crypto_collection.find({'symbol': 'BTC'}, {'_id': 0, 'timestamp': 1, 'price': 1})
    ]

    # Bar Chart Data (Top 5 Cryptocurrencies by Maximum Price)
    top_cryptos_data = [
        {'symbol': entry['_id'], 'price': entry['maxPrice']}
        for entry in crypto_collection.aggregate([
            {"$group": {"_id": "$symbol", "maxPrice": {"$max": "$price"}}},
            {"$sort": {"maxPrice": -1}},
            {"$limit": 5}
        ])
    ]

    return render_template('charts.html', bitcoin_data=bitcoin_data, top_cryptos_data=top_cryptos_data)

# Route for the Home Page with Paginated Cryptocurrency Data
@app.route('/')
def index():
    current_page, items_per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total_documents = crypto_collection.count_documents({})
    paginated_crypto_data = get_paginated_data(offset=offset)

    pagination = Pagination(page=current_page, per_page=items_per_page, total=total_documents, css_framework='bootstrap4')
    total_pages = ceil(total_documents / items_per_page)

    return render_template('index.html', crypto_data=paginated_crypto_data, page=current_page, per_page=items_per_page, pagination=pagination, total_pages=total_pages)

# Route for Filtering Cryptocurrency Data
@app.route('/filter', methods=['GET', 'POST'])
def filtered_data():
    if request.method == 'POST':
        crypto_symbols = request.form.get('cryptos')
        selected_symbols = [symbol.strip() for symbol in crypto_symbols.split(',')]
        filtered_crypto_data = list(crypto_collection.find({'symbol': {'$in': selected_symbols}}))

        current_page, items_per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        total_filtered = len(filtered_crypto_data)

        paginated_filtered_data = filtered_crypto_data[offset:offset + items_per_page]

        pagination = Pagination(page=current_page, per_page=items_per_page, total=total_filtered, css_framework='bootstrap4')

        return render_template('filtered.html', crypto_data=paginated_filtered_data, pagination=pagination, per_page=items_per_page, total=total_filtered, cryptos=crypto_symbols)
    else:
        return render_template('filtered.html', crypto_data=[], pagination=None)


# Run the Flask Application
if __name__ == "__main__":
    app.run(debug=True)
