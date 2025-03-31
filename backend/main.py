from flask import Flask, render_template, request, jsonify
from scraper import get_products
from database import init_db, save_search, get_search_history
import learning

app = Flask(__name__, 
           template_folder='../frontend', 
           static_folder='../frontend',
           static_url_path='')
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    products = get_products(query)
    save_search(query)
    learning.update_model(query, products)
    return jsonify(products)

@app.route('/history')
def history():
    searches = get_search_history()
    return render_template('history.html', searches=searches)

@app.route('/api/products')
def api_products():
    query = request.args.get('query', '')
    products = learning.get_recommendations(query)
    return jsonify(products)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)