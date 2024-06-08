#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from flask import Flask, request, render_template, jsonify
import json
import codecs

app = Flask(__name__, static_folder='public', template_folder='views')

# Set the app secret key from the secret environment variables.
app.secret_key = os.environ.get('API_KEY')


@app.before_request
def authenticate_request():
    """Before each request, authenticate the request by checking the API key."""
    api_key = request.headers.get('API-Key')
    if api_key != app.secret_key:
        # Eğer API anahtarı geçerli değilse, 401 Unauthorized hatası döndür
        return jsonify({'message': 'API anahtarı geçersiz.'}), 401





@app.after_request
def apply_kr_hello(response):
    if 'MADE_BY' in os.environ:
        response.headers["X-Was-Here"] = os.environ.get('MADE_BY')
    response.headers["X-Powered-By"] = os.environ.get('POWERED_BY')
    return response



@app.route('/users', methods=['POST'])
def add_user():
    # POST isteğinden gelen JSON verisini al
    data = request.get_json()

    # Yeni kullanıcıya varsayılan değerleri ekle
    
    data['cart'] = []
    data['favourites'] = []
    data['wallet'] = 0
    data['credit_card'] = []
    data['address'] = []

    # JSON dosyasını oku
    try:
        with codecs.open('views/users.json', 'r', 'utf-8') as f:
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
    with codecs.open('views/users.json', 'w', 'utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    # Başarılı yanıt gönder
    return jsonify({'message': 'Kullanıcı başarıyla eklendi!', 'user_id': data['user_id']}), 200


  
  
@app.route('/users', methods=['GET'])
def get_users():
    try:
        with codecs.open('views/users.json', 'r', 'utf-8') as f:
            json_data = json.load(f)
    except IOError:
        return jsonify({'message': 'Veri bulunamadı'}), 404

    return jsonify(json_data), 200
  
  
@app.route('/discount', methods=['GET'])
def get_discount():
    try:
        with codecs.open('views/discount.json', 'r', 'utf-8') as f:
            discount_data = json.load(f)
    except IOError:
        return jsonify({'message': 'Veri bulunamadı'}), 404

    return jsonify(discount_data), 200

@app.route('/cart/<int:user_id>', methods=['POST'])
def add_to_cart(user_id):
    data = request.get_json()
    amount = data.get('amount')
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({'message': 'Eksik veri: product_id gerekli'}), 400

    # Ürünleri bul
    try:
        with codecs.open('views/products.json', 'r', 'utf-8') as f:
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
        with codecs.open('views/users.json', 'r', 'utf-8') as f:
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
    with codecs.open('views/users.json', 'w', 'utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=4)

    return jsonify({'message': 'Ürün başarıyla sepete eklendi!'}), 200
  
  
@app.route('/credit_card/<int:user_id>', methods=['POST'])
def add_credit_card(user_id):
    data = request.get_json()
    card_number = data.get('card_number')
    expiry_date = data.get('expiry_date')
    card_holder_name = data.get('card_holder_name')
    cvv = data.get('cvv')
    
    if not card_number or not expiry_date or not card_holder_name:
        return jsonify({'message': 'Eksik veri: card_number, expiry_date ve card_holder_name gerekli'}), 400

    # Kullanıcıları bul
    try:
        with codecs.open('views/users.json', 'r', 'utf-8') as f:
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
    try:
        with codecs.open('views/users.json', 'w', 'utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=4)
    except IOError:
        return jsonify({'message': 'Kullanıcı verisi güncellenemedi'}), 500

    return jsonify({'message': 'Kredi kartı başarıyla eklendi!'}), 200
  
  
  
@app.route('/favorites/<int:user_id>', methods=['POST'])
def add_to_favorites(user_id):
    # Get the JSON data from the POST request
    data = request.get_json()
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({'message': 'Eksik veri: product_id gerekli'}), 400

    # Load users data
    try:
        with codecs.open('views/users.json', 'r', 'utf-8') as f:
            users_data = json.load(f)
            users_dict = {user['user_id']: user for user in users_data["users"]}
    except IOError:
        return jsonify({'message': 'Kullanıcı verisi bulunamadı'}), 404

    # Find the user by ID
    user = users_dict.get(user_id)
    if not user:
        return jsonify({'message': 'Kullanıcı bulunamadı'}), 404

    # Add product to favorites if it's not already in the list
    if "favourites" not in user:
        user["favourites"] = []
    
    for favorite in user["favourites"]:
        if favorite["product_id"] == product_id:
            return jsonify({'message': 'Ürün zaten favorilerde'}), 400
    
    user["favourites"].append({"product_id": product_id})

    # Write the updated data back to the JSON file
    try:
        with codecs.open('views/users.json', 'w', 'utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=4)
    except IOError:
        return jsonify({'message': 'Kullanıcı verisi güncellenemedi'}), 500

    return jsonify({'message': 'Ürün favorilere başarıyla eklendi!'}), 200


  
  
@app.route('/credit_card/<int:user_id>', methods=['GET'])
def get_credit_card(user_id):
    # Kullanıcıları bul
    try:
        with codecs.open('views/users.json', 'r', 'utf-8') as f:
            users_data = json.load(f)
            users_dict = {user['user_id']: user for user in users_data["users"]}
    except IOError:
        return jsonify({'message': 'Kullanıcı verisi bulunamadı'}), 404

    # ID'ye göre kullanıcıyı bul
    user = users_dict.get(user_id)
    if not user:
        return jsonify({'message': 'Kullanıcı bulunamadı'}), 404

    # Kredi kartı bilgilerini döndür
    return jsonify({'credit_card':user["credit_card"]})  
  
  
@app.route('/favorites/<int:user_id>', methods=['GET'])
def get_favorites(user_id):
    try:
        with codecs.open('views/users.json', 'r', 'utf-8') as f:
            users_data = json.load(f)
            users_dict = {user['user_id']: user for user in users_data["users"]}
    except IOError:
        return jsonify({'message': 'Kullanıcı verisi bulunamadı'}), 404

    user = users_dict.get(user_id)
    if not user:
        return jsonify({'message': 'Kullanıcı bulunamadı'}), 404

    favorites = user.get('favourites', [])

    try:
        with codecs.open('views/products.json', 'r', 'utf-8') as f:
            products_data = json.load(f)
            products_dict = {product['product_id']: product for product in products_data["products"]}
    except IOError:
        return jsonify({'message': 'Ürün verisi bulunamadı'}), 404

    detailed_favorites = []
    for item in favorites:
        product_id = item.get('product_id')
        product_details = products_dict.get(product_id)
        if product_details:
            detailed_favorites.append({
                'product_id': product_id,
                'details': product_details
            })

    return jsonify({'favorites': detailed_favorites}), 200

  
@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    # Kullanıcıları bul
    try:
        with codecs.open('views/users.json', 'r', 'utf-8') as f:
            users_data = json.load(f)
            users_dict = {user['user_id']: user for user in users_data["users"]}
    except IOError:
        return jsonify({'message': 'Kullanıcı verisi bulunamadı'}), 404

    # ID'ye göre kullanıcıyı bul
    user = users_dict.get(user_id)
    if not user:
        return jsonify({'message': 'Kullanıcı bulunamadı'}), 404

    # Sepet bilgilerini al
    cart_items = user.get('cart', [])

    # Ürünleri bul
    try:
        with codecs.open('views/products.json', 'r', 'utf-8') as f:
            products_data = json.load(f)
            products_dict = {product['product_id']: product for product in products_data["products"]}
    except IOError:
        return jsonify({'message': 'Ürün verisi bulunamadı'}), 404

    # Sepet öğelerinin detaylarını oluştur
    detailed_cart = []
    for item in cart_items:
        product_id = item['product_id']
        product_details = products_dict.get(product_id)
        if product_details:
            detailed_cart.append({
                'amount': item['amount'],
                'details': product_details
            })

    return jsonify({'cart': detailed_cart}), 200


  
@app.route('/products', methods=['GET'])
def get_products():
    try:
        with codecs.open('views/products.json', 'r', 'utf-8') as f:
            json_data = json.load(f)
    except IOError:
        return jsonify({'message': 'Veri bulunamadı'}), 404

    return jsonify(json_data), 200
  
@app.route('/influencers', methods=['GET'])
def get_influencers():
    # Influencer verilerini bul
    try:
        with codecs.open('views/influencers.json', 'r', 'utf-8') as f:
            influencers_data = json.load(f)
    except IOError:
        return jsonify({'message': 'Influencer verisi bulunamadı'}), 404

    # Influencer verilerini döndür
    return jsonify(influencers_data)


@app.route('/data')
def page2():
    """Displays the homepage."""
    return render_template('page2.html')
  
  
@app.route('/search_products', methods=['GET'])
def search_products():
    # Arama terimini alın
    search_term = request.args.get('term')

    if not search_term:
        return jsonify({'message': 'Arama terimi eksik'}), 400

    try:
        with codecs.open('views/products.json', 'r', 'utf-8') as f:
            products_data = json.load(f)
    except IOError:
        return jsonify({'message': 'Ürün verisi bulunamadı'}), 404

    # Arama terimine göre ürünleri filtrele
    filtered_products = [product for product in products_data['products'] if search_term.lower() in product['name'].lower()]

    return jsonify({'products': filtered_products}), 200

  
@app.route('/wallet/<int:user_id>', methods=['GET'])
def get_wallet(user_id):
    try:
        # users.json dosyasını oku
        with codecs.open('views/users.json', 'r', 'utf-8') as f:
            users_data = json.load(f)
            users_dict = {user['user_id']: user for user in users_data["users"]}
    except IOError:
        return jsonify({'message': 'Kullanıcı verisi bulunamadı'}), 404

    # İstenen kullanıcıyı bul
    user = users_dict.get(user_id)
    if not user:
        return jsonify({'message': 'Kullanıcı bulunamadı'}), 404

    # Kullanıcının cüzdan bilgilerini döndür
    return jsonify({'wallet': user.get('wallet', 0)}), 200

@app.route('/past_orders/<int:user_id>', methods=['GET'])
def get_past_orders(user_id):
    # Kullanıcıları bul
    try:
        with codecs.open('views/users.json', 'r', 'utf-8') as f:
            users_data = json.load(f)
            users_dict = {user['user_id']: user for user in users_data["users"]}
    except IOError:
        return jsonify({'message': 'Kullanıcı verisi bulunamadı'}), 404

    # ID'ye göre kullanıcıyı bul
    user = users_dict.get(user_id)
    if not user:
        return jsonify({'message': 'Kullanıcı bulunamadı'}), 404

    # Geçmiş sipariş bilgilerini al
    past_orders = user.get('pastOrders', [])

    # Ürünleri bul
    try:
        with codecs.open('views/products.json', 'r', 'utf-8') as f:
            products_data = json.load(f)
            products_dict = {product['product_id']: product for product in products_data["products"]}
    except IOError:
        return jsonify({'message': 'Ürün verisi bulunamadı'}), 404

    # Geçmiş sipariş öğelerinin detaylarını oluştur
    detailed_past_orders = []
    for item in past_orders:
        product_id = item['product_id']
        product_details = products_dict.get(product_id)
        if product_details:
            detailed_past_orders.append({
                'amount': item['amount'],
                'details': product_details
            })

    return jsonify({'pastOrders': detailed_past_orders}), 200

@app.route('/address/<int:user_id>', methods=['GET'])
def get_user_address(user_id):
    try:
        with codecs.open('views/users.json', 'r', 'utf-8') as f:
            users_data = json.load(f)
            users_dict = {user['user_id']: user for user in users_data["users"]}
    except IOError:
        return jsonify({'message': 'Kullanıcı verisi bulunamadı'}), 404

    user = users_dict.get(user_id)
    if not user:
        return jsonify({'message': 'Kullanıcı bulunamadı'}), 404

    return jsonify({'address': user.get('address', {})}), 200

  
@app.route('/address/<int:user_id>', methods=['POST'])
def add_address(user_id):
    # POST isteğinden gelen JSON verisini al
    data = request.get_json()

    # Kullanıcıları bul
    try:
        with codecs.open('views/users.json', 'r', 'utf-8') as f:
            users_data = json.load(f)
            users_dict = {user['user_id']: user for user in users_data["users"]}
    except IOError:
        return jsonify({'message': 'Kullanıcı verisi bulunamadı'}), 404

    # ID'ye göre kullanıcıyı bul
    user = users_dict.get(user_id)
    if not user:
        return jsonify({'message': 'Kullanıcı bulunamadı'}), 404

    # Adresi ekle
    if "address" not in user:
        user["address"] = []
    user["address"].append(data)

    # JSON dosyasını güncelle
    try:
        with codecs.open('views/users.json', 'w', 'utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=4)
    except IOError:
        return jsonify({'message': 'Kullanıcı verisi güncellenemedi'}), 500

    return jsonify({'message': 'Adres başarıyla eklendi!'}), 200

@app.route('/comments', methods=['GET'])
def get_comments():
    try:
        with codecs.open('views/comment.json', 'r', 'utf-8') as f:
            comments_data = json.load(f)
    except IOError:
        return jsonify({'message': 'Yorum verisi bulunamadı'}), 404

    return jsonify(comments_data), 200

  
  
@app.route('/purchase/<int:user_id>', methods=['POST'])
def purchase(user_id):
    # Kullanıcıları bul
    try:
        with codecs.open('views/users.json', 'r', 'utf-8') as f:
            users_data = json.load(f)
            users_dict = {user['user_id']: user for user in users_data["users"]}
    except IOError:
        return jsonify({'message': 'Kullanıcı verisi bulunamadı'}), 404

    # ID'ye göre kullanıcıyı bul
    user = users_dict.get(user_id)
    if not user:
        return jsonify({'message': 'Kullanıcı bulunamadı'}), 404

    # Sepet öğelerini geçmiş siparişlere ekle
    if 'pastOrders' not in user:
        user['pastOrders'] = []
    user['pastOrders'].extend(user['cart'])

    # Sepeti temizle
    user['cart'] = []

    # JSON dosyasını güncelle
    try:
        with codecs.open('views/users.json', 'w', 'utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=4)
    except IOError:
        return jsonify({'message': 'Kullanıcı verisi güncellenemedi'}), 500

    return jsonify({'message': 'Sepet başarıyla siparişlere aktarıldı!'}), 200


  
@app.route('/')
def homepage():
    """Displays the homepage."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
