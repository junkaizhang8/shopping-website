from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_bcrypt import Bcrypt
from datetime import timedelta, datetime
import sqlite3

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'dkf3sldkjfDF23fLJ3b'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

def initializeCountries():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    query_result = cur.execute('SELECT country FROM Country;').fetchall()
    countries = []
    for tuple in query_result:
        countries.append(tuple[0])
    return countries

def resetSessionVariables():
    session['review'] = ""
    session['rating'] = 0
    session['link'] = ""
    session['name'] = ""
    session['cost'] = ""
    session['stock'] = ""
    session['type'] = ""


@app.route('/home')
def homePage():
    if 'user' not in session:
        flash('You must log in before you can access this page')
        return redirect(url_for('logInPage'))
    
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    date = datetime.today().strftime('%Y-%m-%d')
    sql_query = f"""
SELECT id, name, cost, cost * SUM(amount) AS priority, image
FROM (Product INNER JOIN Purchase ON product_id = id) NATURAL JOIN Receipt
WHERE date = '{date}'
GROUP BY id
ORDER BY priority DESC
LIMIT 5;
"""
    query_result = cur.execute(sql_query).fetchall()
    popular_today = []
    for tuple in query_result:
        product = {'id': tuple[0],
                   'name': tuple[1],
                   'cost': tuple[2],
                   'image': tuple[4]}
        popular_today.append(product)
    return render_template("index.html", popular_today=popular_today)

@app.route('/', methods=['GET', 'POST'])
def logInPage():
    resetSessionVariables()
    if request.method == 'POST':
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        username = request.form.get('username')
        password = request.form.get('password')
        sql_query = f"SELECT username, password FROM User WHERE username = '{username}';"
        query_result = cur.execute(sql_query).fetchall()
        if len(query_result) == 0:
            flash(f"No such user: {username}")
            return render_template("login.html")
        elif(not bcrypt.check_password_hash(query_result[0][1], password)):
            flash('Incorrect password')
            return render_template("login.html")
        else:
            session['user'] = username
            return redirect(url_for('homePage'))
    else:
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signUpPage():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            flash("Username cannot be empty!")
            return redirect(url_for("signUpPage"))
        password = request.form.get('password')
        if not password:
            flash("Password cannot be empty!")
            return redirect(url_for("signUpPage"))
        country = request.form.get('country')
        if not country:
            flash("Please enter a valid country!")
            return redirect(url_for("signUpPage"))
        password_hashed = bcrypt.generate_password_hash(password)
        password_hashed_str = password_hashed.decode('utf-8')
        sql_query = f"SELECT username FROM User WHERE username = '{username}';"
        user_result = cur.execute(sql_query).fetchall()
        sql_query = f"SELECT country FROM Country WHERE country = '{country.title()}';"
        country_result = cur.execute(sql_query).fetchall()
        if len(user_result) == 0:
            if len(country_result) == 0:
                countries = initializeCountries()
                flash('Please enter a valid country!')
                return render_template('signup.html', country_list=countries)
            else:
                sql_query = f"INSERT INTO User VALUES ('{username}', '{password_hashed_str}', '{country}');"
                cur.execute(sql_query)
                con.commit()
                flash('You have successfully signed up!')
                return redirect(url_for('logInPage'))
        else:
            countries = initializeCountries()
            flash('Username already exists!')
            return render_template('signup.html', country_list=countries)
    else:
        countries = initializeCountries()
        return render_template('signup.html', country_list=countries)

@app.route('/catalog', methods=['GET', 'POST'])
def catalogPage():
    if 'user' not in session:
        flash('You must log in before you can access this page')
        return redirect(url_for('logInPage'))
    
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    sql_query = """
SELECT id, name, cost, type, image, AVG(rating) AS average_rating, UPPER(name) AS name_capital
FROM Product LEFT JOIN Review ON id = product_id
GROUP BY id
"""
    if request.method == 'POST':
        filter_by = request.form.getlist('filter')
        if (filter_by != []):
            sql_query += "HAVING"
            for filter in filter_by:
                sql_query += f" type = '{filter}' OR"
            sql_query = sql_query[:-3]
        sort_by = request.form.get('sort')
        if sort_by == 'alphabetical':
            sql_query += "ORDER BY name_capital"
        elif sort_by == 'reverse alphabetical':
            sql_query += "ORDER BY name_capital DESC"
        elif sort_by == 'rating':
            sql_query += "ORDER BY average_rating DESC"
    sql_query += ";"
    query_result = cur.execute(sql_query).fetchall()
    products = []
    for tuple in query_result:
        if type(tuple[5]) != float and type(tuple[5]) != int:
            rating = 0
        else:
            rating = tuple[5]
        product_info = {'id': tuple[0],
                        'name': tuple[1],
                        'cost': tuple[2],
                        'type': tuple[3],
                        'image': tuple[4],
                        'rating': rating}
        products.append(product_info)
    filter_list = ["Book", "Clothing", "Electronic", "Entertainment", "Food", "Furniture", "Utility"]
    resetSessionVariables()
    return render_template('catalog.html', product_list=products, filter_list=filter_list)

@app.route('/description/<product_id>')
def descriptionPage(product_id):
    if 'user' not in session:
        flash('You must log in before you can access this page')
        return redirect(url_for('logInPage'))
    
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    query_result = cur.execute(f"""
SELECT id, name, cost, stock - purchased - SUM(amount) AS stock_remaining, type, description, image
FROM Product INNER JOIN Purchase ON id = Purchase.product_id INNER JOIN
(SELECT product_id, SUM(amount) AS purchased
FROM Cart
GROUP BY product_id) T1
ON id = T1.product_id
WHERE id = {int(product_id)}
GROUP BY id;
""").fetchall()
    if len(query_result) == 0:
        query_result = cur.execute(f"""
SELECT id, name, cost, stock - SUM(amount) AS stock_remaining, type, description, image
FROM Product INNER JOIN Purchase ON id = Purchase.product_id
WHERE id = {int(product_id)}
GROUP BY id;
""").fetchall()
    if len(query_result) == 0:
        query_result = cur.execute(f"""
SELECT id, name, cost, stock - purchased AS stock_remaining, type, description, image
FROM Product LEFT JOIN
(SELECT product_id, SUM(amount) AS purchased
FROM Cart
GROUP BY product_id) T1
ON id = T1.product_id
WHERE id = {int(product_id)}
GROUP BY id;
""").fetchall()
    if type(query_result[0][3]) != float and type(query_result[0][3])!= int:
        stock_remaining = cur.execute(f"SELECT stock FROM Product WHERE id = {int(product_id)};").fetchall()[0][0]
    else:
        stock_remaining = query_result[0][3]
    
    info = {'id': query_result[0][0],
            'name': query_result[0][1],
            'cost': query_result[0][2],
            'stock_remaining': stock_remaining,
            'type': query_result[0][4],
            'description': query_result[0][5],
            'image': query_result[0][6]}

    sql_query = f"""
SELECT username, review, rating
FROM Product INNER JOIN Review ON id = product_id
WHERE id = {product_id}
ORDER BY rating DESC;
"""
    query_result = cur.execute(sql_query).fetchall()
    user_reviews = []
    for tuple in query_result:
        review = {'username': tuple[0],
                  'review': tuple[1],
                  'rating': tuple[2]}
        user_reviews.append(review)
    session['product_id'] = info['id']
    session['product_stock'] = info['stock_remaining']
    session['link'] = ""
    session['name'] = ""
    session['cost'] = ""
    session['stock'] = ""
    session['type'] = ""
    session['description'] = ""
    return render_template('description.html', product_info=info, reviews=user_reviews,\
                           product_id=product_id, review=session['review'], rating=session['rating'])

@app.route('/submit-review', methods=['POST'])
def submitReview():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    id = session['product_id']
    review = request.form.get('review')
    rating = int(request.form.get('rating'))
    if review == "":
        session['review'] = review
        session['rating'] = rating
        flash('Review cannot be empty!')
        return redirect(url_for('descriptionPage', product_id=id))
    if rating == 0:
        session['review'] = review
        session['rating'] = rating
        flash('Please enter a rating!')
        return redirect(url_for('descriptionPage', product_id=id))
    sql_query = f"INSERT INTO Review VALUES ({id}, '{session['user']}', '{review}', {rating});"
    cur.execute(sql_query)
    con.commit()
    resetSessionVariables()
    flash('Review successfully added!')
    return redirect(url_for('descriptionPage', product_id=id))

@app.route('/add-to-cart', methods=['POST'])
def addToCart():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    username = session['user']
    id = session['product_id']
    stock_remaining = session['product_stock']
    try:
        amount = int(request.form.get('amount'))
        if amount != float(request.form.get('amount')) or amount <= 0:
            flash('Please enter a valid amount.')
            return redirect(url_for('descriptionPage', product_id=id))
        if amount > stock_remaining:
            flash('There are not enough stock for purchase.')
            return redirect(url_for('descriptionPage', product_id=id))
    except:
        flash('Please enter a valid amount.')
        return redirect(url_for('descriptionPage', product_id=id))
    cur.execute(f"INSERT INTO Cart VALUES ('{username}', {id}, {amount});")
    con.commit()
    flash('Successfully added to your cart!')
    return redirect(url_for('descriptionPage', product_id=id))

@app.route('/shopping-cart')
def shoppingCartPage():
    if 'user' not in session:
        flash('You must log in before you can access this page')
        return redirect(url_for('logInPage'))
    
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    username = session['user']
    sql_query = f"""
SELECT product_id, name, cost, SUM(amount) AS total_amount, cost * SUM(amount) AS total_cost, image
FROM Cart INNER JOIN Product ON product_id = id
WHERE username = '{username}'
GROUP BY product_id;
"""
    query_result = cur.execute(sql_query).fetchall()
    resetSessionVariables()
    cart = []
    for tuple in query_result:
        cart_info = {'id': tuple[0],
                     'name': tuple[1],
                     'cost': tuple[2],
                     'amount': tuple[3],
                     'total_cost': tuple[4],
                     'image': tuple[5]}
        cart.append(cart_info)
    session['cart'] = cart
    return render_template('shopping_cart.html', cart=cart)

@app.route('/remove-cart-item', methods=['POST'])
def removeCartItem():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    id = int(request.form.get('id'))
    product_name = cur.execute(f"SELECT name FROM Product WHERE id = {id};").fetchall()[0][0]
    cur.execute(f"DELETE FROM Cart WHERE product_id = {id};")
    con.commit()
    flash(f"'{product_name}' removed from your cart.")
    return redirect(url_for('shoppingCartPage'))

@app.route('/checkout', methods=['POST'])
def checkout():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cart = session['cart']
    username = session['user']
    date = datetime.today().strftime('%Y-%m-%d')
    cur.execute(f"INSERT INTO Receipt (username, date) VALUES ('{username}', '{date}');")
    receipt_id = cur.execute(f"""
SELECT receipt_id
FROM Receipt
WHERE username = '{username}'
ORDER BY receipt_id DESC;
""").fetchall()[0][0]
    for item in cart:
        sql_query = f"INSERT INTO Purchase VALUES ({receipt_id}, {item['id']}, {item['amount']});"
        cur.execute(sql_query)
        cur.execute(f"DELETE FROM Cart WHERE product_id = {item['id']};")
    con.commit()
    session['cart'] = []
    flash('Items successfully checked out!')
    return redirect(url_for('shoppingCartPage'))

@app.route('/receipts')
def receiptsPage():
    if 'user' not in session:
        flash('You must log in before you can access this page')
        return redirect(url_for('logInPage'))
    
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    username = session['user']
    sql_query = f"""
SELECT receipt_id, date, product_id, name, cost, SUM(amount) AS total_amount, cost * SUM(amount) AS total_cost, image
FROM (Receipt NATURAL JOIN Purchase) INNER JOIN Product ON product_id = id
WHERE username = '{username}'
GROUP BY receipt_id, product_id
ORDER BY receipt_id DESC, product_id;
"""
    query_result = cur.execute(sql_query).fetchall()
    receipts = []
    if len(query_result) != 0:
        cur_receipt_id = query_result[0][0]
        tuple_index = 0
        while tuple_index < len(query_result):
            receipt_info = {'receipt_id': query_result[tuple_index][0],
                            'date': query_result[tuple_index][1],
                            'purchases': []}
            while tuple_index < len(query_result) and query_result[tuple_index][0] == cur_receipt_id:
                purchase_info = {'product_id': query_result[tuple_index][2],
                                 'name': query_result[tuple_index][3],
                                 'cost': query_result[tuple_index][4],
                                 'amount': query_result[tuple_index][5],
                                 'total_cost': query_result[tuple_index][6],
                                 'image': query_result[tuple_index][7]}
                receipt_info['purchases'].append(purchase_info)
                cur_receipt_id = query_result[tuple_index][0]
                tuple_index += 1
            receipts.append(receipt_info)
            if tuple_index != len(query_result):
                cur_receipt_id = query_result[tuple_index][0]
        resetSessionVariables()
    return render_template('receipts.html', receipts=receipts)

@app.route('/insert-product')
def insertPage():
    if 'user' not in session:
        flash('You must log in before you can access this page')
        return redirect(url_for('logInPage'))
    
    link = session['link']
    name = session['name']
    cost = session['cost']
    stock = session['stock']
    type = session['type']
    review = session['review']
    rating = session['rating']
    type_list = ["", "Book", "Clothing", "Electronic", "Entertainment", "Food", "Furniture", "Utility"]
    return render_template('insert_product.html', link=link, name=name, cost=cost, stock=stock,\
                           type=type, review=review, rating=rating, type_list=type_list)

@app.route('/add', methods=['POST'])
def addProduct():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    link = request.form.get('link')
    name = request.form.get('name')
    cost = request.form.get('cost')
    stock = request.form.get('stock')
    type = request.form.get('type')
    description = request.form.get('description')

    session['link'] = link
    session['name'] = name
    session['cost'] = cost
    session['stock'] = stock
    session['type'] = type
    session['description'] = description

    if link == "":
        flash('Image URL field cannot be empty.')
        return redirect(url_for('insertPage'))
    
    if name == "":
        flash('Product Name field cannot be empty.')
        return redirect(url_for('insertPage'))
    
    try:
        cost = float(request.form.get('cost'))
        cost = round(cost, 2)
        if cost <= 0 or cost > 99999.99:
            session['cost'] = ""
            flash('Please enter a valid cost.')
            return redirect(url_for('insertPage'))
    except:
        session['cost'] = ""
        flash('Please enter a valid cost.')
        return redirect(url_for('insertPage'))
    
    try:
        stock = int(request.form.get('stock'))
        if stock != float(request.form.get('stock')) or stock <= 0:
            session['stock'] = ""
            flash('Please enter a valid stock amount.')
            return redirect(url_for('insertPage'))
    except:
        session['stock'] = ""
        flash('Please enter a valid stock amount.')
        return redirect(url_for('insertPage'))
    
    if type == "":
        flash('Please select a product type.')
        return redirect(url_for('insertPage'))
    
    if description == "":
        flash('Description cannot be empty.')
        return redirect(url_for('insertPage'))
    sql_query = "INSERT INTO Product(name, cost, stock, type, description, image) VALUES ("
    sql_query += f"'{name}', {cost}, {stock}, '{type}', '{description}', '{link}');"
    cur.execute(sql_query)
    con.commit()
    resetSessionVariables()
    flash('Product added successfully!')
    return redirect(url_for('insertPage'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    resetSessionVariables()
    return redirect(url_for('logInPage'))

if __name__ == '__main__':
    app.run(debug=True)