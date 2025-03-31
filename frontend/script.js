document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const suggestions = document.getElementById('suggestions');
    const resultsSection = document.getElementById('resultsSection');
    const productsGrid = document.getElementById('productsGrid');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const noResults = document.getElementById('noResults');
    const recommendationsSection = document.getElementById('recommendationsSection');
    const recommendationsGrid = document.getElementById('recommendationsGrid');
    const sortSelect = document.getElementById('sortSelect');

    // Load search history for suggestions
    fetch('/history')
        .then(response => response.json())
        .then(searches => {
            const searchHistory = searches.map(s => s.query);
            setupAutocomplete(searchHistory);
        });

    // Search form submission
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = searchInput.value.trim();
        
        if (query) {
            performSearch(query);
        }
    });

    // Sort products
    sortSelect.addEventListener('change', function() {
        sortProducts(this.value);
    });

    function setupAutocomplete(searchHistory) {
        searchInput.addEventListener('input', function() {
            const input = this.value.toLowerCase();
            suggestions.innerHTML = '';
            
            if (input.length > 2) {
                const matches = searchHistory.filter(term => 
                    term.toLowerCase().includes(input)
                ).slice(0, 5);
                
                if (matches.length) {
                    matches.forEach(match => {
                        const div = document.createElement('div');
                        div.className = 'px-4 py-2 hover:bg-gray-100 cursor-pointer';
                        div.textContent = match;
                        div.addEventListener('click', function() {
                            searchInput.value = match;
                            suggestions.classList.add('hidden');
                            performSearch(match);
                        });
                        suggestions.appendChild(div);
                    });
                    suggestions.classList.remove('hidden');
                } else {
                    suggestions.classList.add('hidden');
                }
            } else {
                suggestions.classList.add('hidden');
            }
        });

        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !suggestions.contains(e.target)) {
                suggestions.classList.add('hidden');
            }
        });
    }

    function performSearch(query) {
        // Show loading state
        productsGrid.innerHTML = '';
        loadingIndicator.classList.remove('hidden');
        noResults.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `query=${encodeURIComponent(query)}`
        })
        .then(response => response.json())
        .then(products => {
            loadingIndicator.classList.add('hidden');
            
            if (products && products.length) {
                displayProducts(products);
                loadRecommendations(query);
            } else {
                noResults.classList.remove('hidden');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loadingIndicator.classList.add('hidden');
            noResults.classList.remove('hidden');
        });
    }

    function displayProducts(products) {
        productsGrid.innerHTML = '';
        
        products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'product-card bg-white rounded-lg shadow-md overflow-hidden transition-all duration-300';
            productCard.innerHTML = `
                <div class="relative pb-2/3 h-48 bg-gray-100">
                    <img src="https://images.pexels.com/photos/90946/pexels-photo-90946.jpeg?auto=compress&cs=tinysrgb&w=600" 
                         alt="${product.name}" 
                         class="absolute h-full w-full object-contain p-4">
                </div>
                <div class="p-4">
                    <h3 class="font-medium text-gray-800 mb-2 truncate">${product.name}</h3>
                    <div class="flex justify-between items-center">
                        <span class="text-xl font-bold text-blue-600">R$ ${product.price.toFixed(2)}</span>
                        <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                            ${product.site}
                        </span>
                    </div>
                    <a href="${product.link}" target="_blank" 
                       class="mt-4 block w-full text-center bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition-colors">
                        Ver no site
                    </a>
                </div>
            `;
            productsGrid.appendChild(productCard);
        });
    }

    function sortProducts(criteria) {
        const productCards = Array.from(productsGrid.children);
        
        productCards.sort((a, b) => {
            const priceA = parseFloat(a.querySelector('span.text-blue-600').textContent.replace('R$ ', ''));
            const priceB = parseFloat(b.querySelector('span.text-blue-600').textContent.replace('R$ ', ''));
            const siteA = a.querySelector('span.bg-blue-100').textContent;
            const siteB = b.querySelector('span.bg-blue-100').textContent;
            
            switch(criteria) {
                case 'price_asc': return priceA - priceB;
                case 'price_desc': return priceB - priceA;
                case 'site': return siteA.localeCompare(siteB);
                default: return 0;
            }
        });
        
        // Re-append sorted products
        productCards.forEach(card => productsGrid.appendChild(card));
    }

    function loadRecommendations(query) {
        fetch(`/api/products?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(recommendations => {
                if (recommendations && recommendations.length) {
                    recommendationsGrid.innerHTML = '';
                    recommendations.forEach(product => {
                        const card = document.createElement('div');
                        card.className = 'product-card bg-white rounded-lg shadow-md overflow-hidden transition-all duration-300';
                        card.innerHTML = `
                            <div class="relative pb-2/3 h-32 bg-gray-100">
                                <img src="https://images.pexels.com/photos/90946/pexels-photo-90946.jpeg?auto=compress&cs=tinysrgb&w=600" 
                                     alt="${product.name}" 
                                     class="absolute h-full w-full object-contain p-4">
                            </div>
                            <div class="p-3">
                                <h3 class="text-sm font-medium text-gray-800 mb-1 truncate">${product.name}</h3>
                                <div class="flex justify-between items-center">
                                    <span class="text-lg font-bold text-blue-600">R$ ${product.price.toFixed(2)}</span>
                                    <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-0.5 rounded">
                                        ${product.site}
                                    </span>
                                </div>
                            </div>
                        `;
                        recommendationsGrid.appendChild(card);
                    });
                    recommendationsSection.classList.remove('hidden');
                } else {
                    recommendationsSection.classList.add('hidden');
                }
            });
    }
});