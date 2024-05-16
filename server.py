#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from flask import Flask, request, render_template, jsonify
import json

# Support for gomix's 'front-end' and 'back-end' UI.
app = Flask(__name__, static_folder='public', template_folder='views')

# Set the app secret key from the secret environment variables.
app.secret = os.environ.get('SECRET')

# Dream database. Store dreams in memory for now. 
DREAMS = ['Python. Python, everywhere.']


@app.after_request
def apply_kr_hello(response):
    """Adds some headers to all responses."""
  
    # Made by Kenneth Reitz. 
    if 'MADE_BY' in os.environ:
        response.headers["X-Was-Here"] = os.environ.get('MADE_BY')
    
    # Powered by Flask. 
    response.headers["X-Powered-By"] = os.environ.get('POWERED_BY')
    return response

  
  
@app.route('/data', methods=['POST'])
def add_data():
    # POST isteğinden gelen JSON verisini al
    data = request.get_json()

    # JSON dosyasını oku
    with open('views/data.json', 'r') as f:
        json_data = json.load(f)

    # Yeni veriyi JSON dosyasına ekle
    json_data[data['name']] = data['value']

    # Güncellenmiş JSON verisini dosyaya yaz
    with open('views/data.json', 'w') as f:
        json.dump(json_data, f)

    # Başarılı yanıt gönder
    return jsonify({'message': 'Veri başarıyla eklendi!'}), 200

  
  
@app.route('/data', methods=['GET'])
def get_data():
    try:
        with open('views/data.json', 'r') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        return jsonify({'message': 'Veri bulunamadı'}), 404

    return jsonify(json_data), 200


@app.route('/')
def homepage():
    """Displays the homepage."""
    return render_template('index.html')
    
@app.route('/dreams', methods=['GET', 'POST'])
def dreams():
    """Simple API endpoint for dreams. 
    In memory, ephemeral, like real dreams.
    """
  
    # Add a dream to the in-memory database, if given. 
    if 'dream' in request.args:
        DREAMS.append(request.args['dream'])
    
    # Return the list of remembered dreams. 
    return jsonify(DREAMS)

if __name__ == '__main__':
    app.run()