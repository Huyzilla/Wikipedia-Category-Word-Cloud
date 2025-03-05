import requests
import sys
import re
import json
import os
from collections import Counter
import nltk
from nltk.corpus import stopwords
from datetime import datetime, timedelta

# Cache settings
CACHE_DIR = "cache"
CACHE_EXPIRY_DAYS = 7  # Cache results expire after 7 days

def ensure_cache_dir():
    """Ensure cache directory exists."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_cache_path(category):
    """Get cache file path for a category."""
    # Sanitize category name for filename
    safe_name = re.sub(r'[^\w\-_]', '_', category)
    return os.path.join(CACHE_DIR, f"{safe_name}.json")

def load_from_cache(category):
    """Load cached results for a category if they exist and are not expired."""
    cache_path = get_cache_path(category)
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Check if cache is expired
        cache_date = datetime.fromisoformat(cache_data['timestamp'])
        if datetime.now() - cache_date > timedelta(days=CACHE_EXPIRY_DAYS):
            return None
        
        return cache_data['word_frequencies']
    except (json.JSONDecodeError, KeyError, ValueError):
        return None

def save_to_cache(category, word_frequencies):
    """Save results to cache."""
    cache_path = get_cache_path(category)
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'word_frequencies': word_frequencies
    }
    
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

def get_pages_in_category(category):
    """Get all pages in a given Wikipedia category."""
    url = "https://en.wikipedia.org/w/api.php"
    pages = []
    
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": "500"
    }
    
    while True:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'query' in data and 'categorymembers' in data['query']:
            members = data['query']['categorymembers']
            pages.extend([member['title'] for member in members if member['ns'] == 0])
        
        if 'continue' not in data:
            break
            
        params.update(data['continue'])
    
    return pages

def get_page_content(title):
    """Get the text content of a Wikipedia page."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "extracts",
        "explaintext": True
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    pages = data['query']['pages']
    page_id = list(pages.keys())[0]
    
    if 'extract' in pages[page_id]:
        return pages[page_id]['extract']
    return ""

def process_text(text):
    """Process text to get non-common words."""
    # Download required NLTK data
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    
    # Simple word tokenization without sentence tokenization
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = set(stopwords.words('english'))
    
    # Filter words
    words = [word for word in words 
            if word.isalnum() 
            and word not in stop_words 
            and len(word) > 2]
    
    return words

def analyze_category(category):
    """Analyze a category and return word frequencies."""
    # Get all pages in category
    pages = get_pages_in_category(category)
    print(f"Found {len(pages)} pages in category")
    
    # Process all pages
    all_words = []
    for i, page in enumerate(pages, 1):
        print(f"Processing page {i}/{len(pages)}: {page}")
        content = get_page_content(page)
        words = process_text(content)
        all_words.extend(words)
    
    # Return word frequencies as a dictionary
    return dict(Counter(all_words))

def display_results(word_frequencies, num_words=50):
    """Display word frequency results."""
    print("\nMost common words and their frequencies:")
    print("-" * 40)
    sorted_freq = sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True)
    for word, count in sorted_freq[:num_words]:
        print(f"{word}: {count}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python wiki_category_analysis.py <category_name>")
        sys.exit(1)
    
    category = sys.argv[1]
    print(f"Analyzing category: {category}")
    
    # Ensure cache directory exists
    ensure_cache_dir()
    
    # Try to load from cache first
    word_frequencies = load_from_cache(category)
    
    if word_frequencies is not None:
        print("Using cached results")
    else:
        print("Cache not found or expired, fetching fresh data...")
        word_frequencies = analyze_category(category)
        save_to_cache(category, word_frequencies)
    
    # Display results
    display_results(word_frequencies)

if __name__ == "__main__":
    main()
