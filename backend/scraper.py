import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from database import save_product
import time

ua = UserAgent()

def normalize_query(query):
    """Extract key product terms from long descriptions"""
    # Remove special characters and model numbers if they don't help search
    query = re.sub(r'[^a-zA-Z0-9\s]', '', query)
    # Take first 3-5 meaningful words
    terms = [word for word in query.split() if len(word) > 3][:5]
    return ' '.join(terms)

def get_products(query):
    normalized_query = normalize_query(query)
    sites = {
        'Amazon': f'https://www.amazon.com/s?k={normalized_query.replace(" ", "+")}',
        'Mercado Livre': f'https://lista.mercadolivre.com.br/{normalized_query.replace(" ", "-")}',
        'Americanas': f'https://www.americanas.com.br/busca/{normalized_query.replace(" ", "-")}',
        'Casas Bahia': f'https://www.casasbahia.com.br/busca/{normalized_query.replace(" ", "-")}'
    }
    
    products = []
    for site, url in sites.items():
        try:
            headers = {'User-Agent': ua.random}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Site-specific selectors
            if site == 'Amazon':
                items = soup.select('[data-component-type="s-search-result"]')[:8]
            elif site == 'Mercado Livre':
                items = soup.select('.ui-search-layout__item')[:8]
            elif site == 'Americanas':
                items = soup.select('[data-testid="product-card"]')[:8]
            elif site == 'Casas Bahia':
                items = soup.select('.ProductGrid__GridCell')[:8]
            
            for item in items:
                try:
                    # Site-specific extraction
                    if site == 'Amazon':
                        name = item.select_one('h2 a span').text.strip()
                        price_whole = item.select_one('.a-price-whole').text.strip()
                        price_fraction = item.select_one('.a-price-fraction').text.strip()
                        price = float(f'{price_whole}{price_fraction}'.replace('.','').replace(',','.'))
                        link = 'https://amazon.com' + item.select_one('h2 a')['href']
                    elif site == 'Mercado Livre':
                        name = item.select_one('.ui-search-item__title').text.strip()
                        price = float(item.select_one('.price-tag-fraction').text.replace('.','').replace(',','.'))
                        link = item.select_one('.ui-search-link')['href']
                    elif site == 'Americanas':
                        name = item.select_one('[data-testid="product-name"]').text.strip()
                        price = float(item.select_one('[data-testid="price-value"]').text.replace('R$','').replace('.','').replace(',','.'))
                        link = 'https://www.americanas.com.br' + item.select_one('a')['href']
                    elif site == 'Casas Bahia':
                        name = item.select_one('.ProductCard__Name').text.strip()
                        price = float(item.select_one('.ProductPrice__Price').text.replace('R$','').replace('.','').replace(',','.'))
                        link = 'https://www.casasbahia.com.br' + item.select_one('a')['href']
                    
                    product = {
                        'name': name,
                        'price': price,
                        'site': site,
                        'link': link if link.startswith('http') else f'https://{site}.com{link}'
                    }
                    save_product(product)
                    products.append(product)
                    
                except Exception as e:
                    print(f"Error parsing product from {site}: {e}")
                    continue
                    
            time.sleep(1)  # Be polite to servers
            
        except Exception as e:
            print(f"Error scraping {site}: {e}")
            continue
            
    return products