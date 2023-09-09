from flask import Flask
from flask_bcrypt import Bcrypt
from datetime import datetime
import sqlite3

app = Flask(__name__)
bcrypt = Bcrypt(app)

con = sqlite3.connect('database.db')
cur = con.cursor()

cur.execute('PRAGMA foreign_keys = ON;')
cur.execute('DROP TABLE IF EXISTS Country;')
cur.execute('DROP TABLE IF EXISTS Purchase;')
cur.execute('DROP TABLE IF EXISTS Cart;')
cur.execute('DROP TABLE IF EXISTS Receipt;')
cur.execute('DROP TABLE IF EXISTS Uploaded;')
cur.execute('DROP TABLE IF EXISTS Review;')
cur.execute('DROP TABLE IF EXISTS User;')
cur.execute('DROP TABLE IF EXISTS Product;')

cur.execute('CREATE TABLE IF NOT EXISTS Country(country TEXT PRIMARY KEY);')
cur.execute('CREATE TABLE IF NOT EXISTS User(username TEXT PRIMARY KEY, password TEXT, country TEXT);')
cur.execute("""CREATE TABLE IF NOT EXISTS Product(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
cost DECIMAL(7, 2) CHECK (cost >= 0),
stock INTEGER CHECK (stock >= 0),
type TEXT,
description TEXT,
image TEXT
);""")
cur.execute("""CREATE TABLE IF NOT EXISTS Uploaded(
product_id INTEGER,
username TEXT,
FOREIGN KEY (product_id) REFERENCES Product(id),
FOREIGN KEY (username) REFERENCES User(username)
);""")
cur.execute("""CREATE TABLE IF NOT EXISTS Review(
product_id INTEGER,
username TEXT,
review TEXT,
rating INTEGER CHECK (rating >= 1),
FOREIGN KEY (product_id) REFERENCES Product(id),
FOREIGN KEY (username) REFERENCES User(username)
);""")
cur.execute("""CREATE TABLE IF NOT EXISTS Receipt(
receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
date DATE,
FOREIGN KEY (username) REFERENCES User(username)
);""")
cur.execute("""CREATE TABLE IF NOT EXISTS Purchase(
receipt_id INTEGER,
product_id INTEGER,
amount INTEGER CHECK (amount > 0),
FOREIGN KEY (receipt_id) REFERENCES Receipt(receipt_id),
FOREIGN KEY (product_id) REFERENCES Product(id)
);""")
cur.execute("""CREATE TABLE IF NOT EXISTS Cart(
username TEXT,
product_id INTEGER,
amount INTEGER CHECK (amount > 0),
FOREIGN KEY (username) REFERENCES User(username),
FOREIGN KEY (product_id) REFERENCES Product(id)
);""")

# Insert list of countries into the database
country_list_file = open('country_list.txt', 'r')
country_list = country_list_file.readlines()
for country in country_list:
    country = country.strip('\n')
    cur.execute(f"INSERT INTO Country VALUES ('{country}');")

product_data_file = open('products.txt', 'r')
data = product_data_file.readline()
product_data_str = ""

while data != '&$------$&\n':
    product_data_str = ""
    while data != '\n':
        product_data_str += data
        data = product_data_file.readline()
    product_data = product_data_str.strip('\n').split('\n')
    sql_query = "INSERT INTO Product (name, cost, stock, type, description, image) VALUES ("
    sql_query += f"""
"{product_data[0]}",
{product_data[1]},
{product_data[2]},
"{product_data[3]}",
"{product_data[4]}",
"{product_data[5]}");"""
    cur.execute(sql_query)
    product_data_str = ""
    data = product_data_file.readline()

# Insert some sample data to the database so that the site is not empty when first run
sample_data_file = open('sample_data.txt', 'r')
data = sample_data_file.readline()

while data != '\n':
    user_data = data.strip('\n').split('|')
    password = user_data[1]
    password_hashed = bcrypt.generate_password_hash(password)
    password_hashed_str = password_hashed.decode('utf-8')
    sql_query = f"INSERT INTO User VALUES ('{user_data[0]}', '{password_hashed_str}', '{user_data[2]}');"
    cur.execute(sql_query)
    data = sample_data_file.readline()
data = sample_data_file.readline()

while data != '\n':
    uploaded_data = data.strip('\n').split('|')
    sql_query = f"INSERT INTO Uploaded VALUES ({uploaded_data[0]}, '{uploaded_data[1]}');"
    cur.execute(sql_query)
    data = sample_data_file.readline()
data = sample_data_file.readline()

while data != '\n':
    review_data = data.strip('\n').split('|')
    sql_query = "INSERT INTO Review VALUES ("
    sql_query += f'{review_data[0]}, "{review_data[1]}", "{review_data[2]}", {review_data[3]});'
    cur.execute(sql_query)
    data = sample_data_file.readline()
data = sample_data_file.readline()

while data != '\n':
    receipt_data = data.strip('\n').split('|')
    sql_query = f"INSERT INTO Receipt (username, date) VALUES ('{receipt_data[0]}', '{receipt_data[1]}');"
    cur.execute(sql_query)
    data = sample_data_file.readline()
data = sample_data_file.readline()

while data != '\n':
    username = data.strip('\n')
    date = datetime.today().strftime('%Y-%m-%d')
    sql_query = f"INSERT INTO Receipt (username, date) VALUES ('{username}', '{date}');"
    cur.execute(sql_query)
    data = sample_data_file.readline()
data = sample_data_file.readline()

while data != '\n':
    purchase_data = data.strip('\n').split('|')
    sql_query = "INSERT INTO Purchase (receipt_id, product_id, amount) VALUES ("
    sql_query += f"{purchase_data[0]}, {purchase_data[1]}, {purchase_data[2]});"
    cur.execute(sql_query)
    data = sample_data_file.readline()

con.commit()
print("Data successfully loaded.")

# --------------------------------------------------------------------------------
# Image Sources:
# https://www.walmart.com/ip/Red-Delicious-Apples-Each/45912954
# https://healthjade.com/apple-fruit/
# https://www.jiomart.com/p/groceries/pears-green-imported-1-kg/590001296
# https://www.homedepot.ca/product/kidsquad-police-cruiser-12v-ride-on-toy-car/1001129107
# https://www.walmart.ca/en/ip/Popsicle-Ice-Pops-Orange-Cherry-Grape/6000195981163
# https://www.uline.ca/Product/Detail/S-24333/Pencils/2-Pencils
# https://www.apple.com/ca/shop/buy-iphone/iphone-14-pro/6.7-inch-display-512gb-deep-purple
# https://www.goodreads.com/book/show/29241321-projekt-1065
# https://www.hellyhansen.com/en_global/active-puffy-jacket-53523