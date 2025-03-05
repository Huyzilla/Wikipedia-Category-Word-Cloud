from flask import Flask, render_template, request, jsonify
import os
from wiki_category_analysis import load_from_cache, analyze_category, ensure_cache_dir, save_to_cache
from color_palette import get_all_color_palettes

app = Flask(__name__)

@app.route('/')
def index():
    color_palettes = get_all_color_palettes()
    palette_data = [{'name': palette.name, 'colors': palette.colors} for palette in color_palettes]
    return render_template('index.html', palettes=palette_data)

@app.route('/analyze', methods=['POST'])
def analyze():
    category = request.json.get('category')
    if not category:
        return jsonify({'error': 'Category is required'}), 400

    ensure_cache_dir()
    word_frequencies = load_from_cache(category)

    if word_frequencies is None:
        try:
            word_frequencies = analyze_category(category)
            save_to_cache(category, word_frequencies)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Convert to list of objects for D3.js
    words_data = [{'text': word, 'size': count} for word, count in word_frequencies.items()]
    # Sort by size (frequency) and take top 100 words for better visualization
    words_data.sort(key=lambda x: x['size'], reverse=True)
    words_data = words_data[:100]

    return jsonify(words_data)

if __name__ == '__main__':
    app.run(debug=True)
