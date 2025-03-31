from collections import defaultdict
from database import get_search_history, get_products_by_query
import re
from datetime import datetime, timedelta

class LearningEngine:
    def __init__(self):
        self.search_patterns = defaultdict(int)
        self.site_preferences = defaultdict(int)
        self.price_ranges = defaultdict(list)
        self.last_updated = datetime.now()
        
    def update_model(self, query, products):
        """Update learning model with new search data"""
        # Update search term frequencies
        for word in re.findall(r'\w+', query.lower()):
            self.search_patterns[word] += 1
            
        # Update site preferences based on results
        for product in products:
            self.site_preferences[product['site']] += 1
            self.price_ranges[product['name'].split()[0]].append(product['price'])
            
        self.last_updated = datetime.now()
        
    def get_recommendations(self, query, limit=5):
        """Generate recommendations based on past searches"""
        # Get similar past queries
        query_words = set(re.findall(r'\w+', query.lower()))
        similar_searches = []
        
        for search in get_search_history(100):
            search_words = set(re.findall(r'\w+', search['query'].lower()))
            similarity = len(query_words & search_words)
            if similarity > 0:
                similar_searches.append((search['query'], similarity))
                
        # Sort by similarity and get most recent
        similar_searches.sort(key=lambda x: (-x[1], x[0]))
        recommendations = []
        
        for search_term, _ in similar_searches[:3]:
            products = get_products_by_query(search_term, limit)
            recommendations.extend(products)
            
        # Sort by site preference and price
        recommendations.sort(
            key=lambda p: (-self.site_preferences[p['site']], p['price'])
        )
        
        return recommendations[:limit]
        
    def get_expected_price_range(self, product_name):
        """Return expected price range based on historical data"""
        base_name = product_name.split()[0]
        prices = self.price_ranges.get(base_name, [])
        if prices:
            avg = sum(prices) / len(prices)
            return (avg * 0.8, avg * 1.2)
        return None

# Global instance
engine = LearningEngine()

# Module-level functions
def update_model(query, products):
    engine.update_model(query, products)
    
def get_recommendations(query):
    return engine.get_recommendations(query)
    
def get_expected_price_range(product_name):
    return engine.get_expected_price_range(product_name)