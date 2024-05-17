#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from flask import Flask, request, render_template, jsonify
import json
import codecs

app = Flask(__name__, static_folder='public', template_folder='views')

# Set the app secret key from the secret environment variables.
app.secret_key = os.environ.get('SECRET')

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
        with codecs.open('views/products.json', 'r', 'utf-8') as f:
            json_data = json.load(f)
    except (IOError, json.JSONDecodeError):
        json_data = {"products": []}

    # Yeni veriyi JSON dosyasına ekle
    json_data["products"].append(data)

    # Güncellenmiş JSON verisini dosyaya yaz
    with codecs.open('views/products.json', 'w', 'utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    # Başarılı yanıt gönder
    return jsonify({'message': 'Ürün başarıyla eklendi!'}), 200

@app.route('/products', methods=['GET'])
def get_products():
    try:
        with open('views/products.json', 'r','utf-8') as f:
            json_data = json.load(f)
    except IOError:
        return jsonify({'message': 'Veri bulunamadı'}), 404

    return jsonify(json_data), 200

@app.route('/users', methods=['POST'])
def add_user():
    # POST isteğinden gelen JSON verisini al
    data = request.get_json()

    # JSON dosyasını oku
    try:
        with open('views/users.json', 'r','utf-8') as f:
            json_data = json.load(f)
    except IOError:
        json_data = {"users": []}

    # user_id değerlerini user sözlüklerinden ayırın
    user_ids = [user.get('user_id', 0) for user in json_data['users']]

    if user_ids:
      max_user_id = max(user_ids)
    else:
      max_user_id = 0
    # Yeni kullanıcıya bir sonraki user_id değerini ata
    data['user_id'] = max_user_id + 1

    # Yeni veriyi JSON dosyasına ekle
    json_data["users"].append(data)

    # Güncellenmiş JSON verisini dosyaya yaz
    with open('views/users.json', 'w','utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    # Başarılı yanıt gönder
    return jsonify({'message': 'Kullanıcı başarıyla eklendi!'}), 200
  
  
@app.route('/users', methods=['GET'])
def get_users():
    try:
        with open('views/users.json', 'r','utf-8') as f:
            json_data = json.load(f)
    except IOError:
        return jsonify({'message': 'Veri bulunamadı'}), 404

    return jsonify(json_data), 200
  
  
@app.route('/discount', methods=['GET'])
def get_discount():
    try:
        with open('views/discount.json', 'r','utf-8') as f:
            discount_data = json.load(f)
    except IOError:
        return jsonify({'message': 'Veri bulunamadı'}), 404

    return jsonify(discount_data), 200


  

@app.route('/users/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    amount = data.get('amount')
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    
    if not user_id or not product_id:
        return jsonify({'message': 'Eksik veri: user_id ve product_id gerekli'}), 400

    # Ürünleri bul
    try:
        with open('views/products.json', 'r','utf-8') as f:
            products_data = json.load(f)
            products_dict = {product['product_id']: product for product in products_data["products"]}
    except IOError:
        return jsonify({'message': 'Ürün verisi bulunamadı'}), 404

    # ID'ye göre ürünü bul
    product = products_dict.get(product_id)
    if not product:
        return jsonify({'message': 'Ürün bulunamadı'}), 404

    # Kullanıcıları bul ve sepetteki ürünleri kontrol et
    try:
        with open('views/users.json', 'r','utf-8') as f:
            users_data = json.load(f)
            users_dict = {user['user_id']: user for user in users_data["users"]}
    except IOError:
        return jsonify({'message': 'Kullanıcı verisi bulunamadı'}), 404

    # ID'ye göre kullanıcıyı bul
    user = users_dict.get(user_id)
    if not user:
        return jsonify({'message': 'Kullanıcı bulunamadı'}), 404

    # Sepetteki ürünleri kontrol et
    for item in user["cart"]:
        if item["product_id"] == product_id:
            # Eğer sepette zaten bu ürün varsa, miktarı artır
            item["amount"] += amount
            break
    else:
        # Eğer ürün sepette yoksa, yeni bir giriş oluştur
        user["cart"].append({"product_id": product_id, "amount": amount})

    # JSON dosyasını güncelle
    with open('views/users.json', 'w','utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=4)

    return jsonify({'message': 'Ürün başarıyla sepete eklendi!'}), 200

  
  
  
@app.route('/users/credit_card', methods=['POST'])
def add_credit_card():
    data = request.get_json()
    user_id = data.get('user_id')
    card_number = data.get('card_number')
    expiry_date = data.get('expiry_date')
    card_holder_name = data.get('card_holder_name')
    cvv = data.get('cvv')
    
    if not user_id or not card_number or not expiry_date or not card_holder_name:
        return jsonify({'message': 'Eksik veri: user_id, card_number, expiry_date ve card_holder_name gerekli'}), 400

    # Kullanıcıları bul
    try:
        with open('views/users.json', 'r','utf-8') as f:
            users_data = json.load(f)
            users_dict = {user['user_id']: user for user in users_data["users"]}
    except IOError:
        return jsonify({'message': 'Kullanıcı verisi bulunamadı'}), 404

    # ID'ye göre kullanıcıyı bul
    user = users_dict.get(user_id)
    if not user:
        return jsonify({'message': 'Kullanıcı bulunamadı'}), 404

    # Yeni kredi kartı bilgilerini ekle
    new_card = {
        "card_number": card_number,
        "expiry_date": expiry_date,
        "card_holder_name": card_holder_name,
        "cvv": cvv
    }
    if "credit_card" not in user:
        user["credit_card"] = []
    user["credit_card"].append(new_card)

    # JSON dosyasını güncelle
    with open('views/users.json', 'w','utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=4)

    return jsonify({'message': 'Kredi kartı başarıyla eklendi!'}), 200
  
 



  
@app.route('/users/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    # Kullanıcıları bul
    try:
        with open('views/users.json', 'r','utf-8' ) as f:
            users_data = json.load(f)
            users_dict = {user['user_id']: user for user in users_data["users"]}
    except IOError:
        return jsonify({'message': 'Kullanıcı verisi bulunamadı'}), 404

    # ID'ye göre kullanıcıyı bul
    user = users_dict.get(user_id)
    if not user:
        return jsonify({'message': 'Kullanıcı bulunamadı'}), 404

    # Sepet öğelerini döndür
    return jsonify(user["cart"])

  
@app.route('/')
def homepage():
    """Displays the homepage."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
