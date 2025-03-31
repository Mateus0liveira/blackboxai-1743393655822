import sqlite3
from datetime import datetime

DB_NAME = 'products.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Create products table
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  price REAL NOT NULL,
                  site TEXT NOT NULL,
                  link TEXT NOT NULL,
                  last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create searches table
    c.execute('''CREATE TABLE IF NOT EXISTS searches
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  query TEXT NOT NULL,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

def save_product(product):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Check if product already exists
    c.execute('''SELECT id FROM products 
                 WHERE name=? AND site=? AND link=?''',
              (product['name'], product['site'], product['link']))
    
    if c.fetchone():
        # Update price if exists
        c.execute('''UPDATE products 
                     SET price=?, last_seen=CURRENT_TIMESTAMP
                     WHERE name=? AND site=? AND link=?''',
                  (product['price'], product['name'], product['site'], product['link']))
    else:
        # Insert new product
        c.execute('''INSERT INTO products (name, price, site, link)
                     VALUES (?, ?, ?, ?)''',
                  (product['name'], product['price'], product['site'], product['link']))
    
    conn.commit()
    conn.close()

def save_search(query):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO searches (query) VALUES (?)', (query,))
    conn.commit()
    conn.close()

def get_search_history(limit=20):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT query, timestamp FROM searches ORDER BY timestamp DESC LIMIT ?', (limit,))
    results = [{'query': row[0], 'timestamp': row[1]} for row in c.fetchall()]
    conn.close()
    return results

def get_products_by_query(query, limit=10):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT name, price, site, link FROM products 
                 WHERE name LIKE ? 
                 ORDER BY last_seen DESC LIMIT ?''',
              (f'%{query}%', limit))
    results = [{'name': row[0], 'price': row[1], 'site': row[2], 'link': row[3]} 
               for row in c.fetchall()]
    conn.close()
    return results