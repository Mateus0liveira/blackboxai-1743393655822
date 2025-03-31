import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from database import save_product
import time

ua = UserAgent()

def get_products(query):
    sites = {
        'Amazon': f'https://www.amazon.com/s?k={query}',
        'Mercado Livre': f'https://lista.mercadolivre.com.br/{query}',
        'Americanas': f'https://www.americanas.com.br/busca/{query}'
    }
    
    products = []
    for site, url in sites.items():
        try:
            headers = {'User-Agent': ua.random}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Example extraction logic (will need site-specific selectors)
            items = soup.select('.product-item')[:5]  # Generic selector
            
            for item in items:
                try:
                    name = item.select_one('.product-name').text.strip()
                    price = float(item.select_one('.price').text.replace('R$','').replace(',','.').strip())
                    link = item.find('a')['href']
                    
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