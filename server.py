#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from flask import Flask, request, render_template, jsonify
import json

app = Flask(__name__, static_folder='public', template_folder='views')

# Set the app secret key from the secret environment variables.
app.secret = os.environ.get('SECRET')

@app.after_request
def apply_kr_hello(response):
    """Adds some headers to all responses."""
    # Made by Kenneth Reitz. 
    if 'MADE_BY' in os.environ:
        response.headers["X-Was-Here"] = os.environ.get('MADE_BY')
    # Powered by Flask. 
    response.headers["X-Powered-By"] = os.environ.get('POWERED_BY')
    return response
  
@app.route('/products', methods=['POST'])
def add_product():
    # POST isteğinden gelen JSON verisini al
    data = request.get_json()

    # JSON dosyasını oku
    try:
        with open('products.json', 'r') as f:
            json_data = json.load(f)
            if 'views/products' not in json_data:
                json_data = {"products": []}
    except (FileNotFoundError, json.JSONDecodeError):
        json_data = {"products": []}

    # Yeni veriyi JSON dosyasına ekle
    json_data["products"].append(data)

    # Güncellenmiş JSON verisini dosyaya yaz
    with open('views/products.json', 'w') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    # Başarılı yanıt gönder
    return jsonify({'message': 'Ürün başarıyla eklendi!'}), 200

@app.route('/products', methods=['GET'])
def get_products():
    try:
        with open('views/products.json', 'r') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        return jsonify({'message': 'Veri bulunamadı'}), 404

    return jsonify(json_data), 200

@app.route('/users', methods=['POST'])
def add_user():
    # POST isteğinden gelen JSON verisini al
    data = request.get_json()

    # JSON dosyasını oku
    try:
        with open('views/users.json', 'r') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        json_data = {"users": []}

    # Yeni veriyi JSON dosyasına ekle
    json_data["users"].append(data)

    # Güncellenmiş JSON verisini dosyaya yaz
    with open('views/users.json', 'w') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    # Başarılı yanıt gönder
    return jsonify({'message': 'Kullanıcı başarıyla eklendi!'}), 200

@app.route('/users', methods=['GET'])
def get_users():
    try:
        with open('views/users.json', 'r') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        return jsonify({'message': 'Veri bulunamadı'}), 404

    return jsonify(json_data), 200

@app.route('/')
def homepage():
    """Displays the homepage."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run( debug = True )
