from os import read
from bs4 import BeautifulSoup
from random import shuffle
from flask import Flask
from flask import redirect, render_template, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from tempfile import mkdtemp
from functools import wraps
from mysql.connector import Error
import yaml
import mysql.connector
import requests
import re


app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure db
db = yaml.load(open('db.yaml'))
connection = mysql.connector.connect(host=db['mysql_host'],
                                         database=db['mysql_db'],
                                         user=db['mysql_user'],
                                         password= db['mysql_password'],
                                         autocommit=True)

cur = connection.cursor()

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Gets tickers held by user
def get_tickers():
        cur.execute("SELECT ticker FROM tickers WHERE user_id = %s", (session['user_id'],))
        results_temp = cur.fetchall()
        tckrs = []
        for index, result in enumerate(results_temp):
            tckrs.append(result[0])
        return tckrs

# Make sure responses are not cached (from CS50 finance)
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# Defining some global variables
articles_list = []
MAX_ARTICLES = 5
tickers = set()

@app.route("/register", methods=["GET", "POST"])
#"""Register user"""
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
           return ("Username not entered")

        if not password:
            return ("Password not entered")
        if len(password) < 8 or password.isalpha():
            return ("Password must be at least 8 characters and contain at least one number")

        if password != confirmation:
            return ("Passwords do not match")
        
        # Checks if username chosen is available

        cur.execute("SELECT username FROM users")
        taken_usernames = cur.fetchall()
        taken_usernames_list = []
        for index, x in enumerate(taken_usernames):
            taken_usernames_list.append(x[0])

        if username in taken_usernames_list:
            return("Username already taken")
        
        # Insert user into database
        sql = "INSERT INTO users (username, hash) VALUES (%s, %s)"
        val = (username, generate_password_hash(password))
        cur.execute(sql, val)
        connection.commit()

        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        username = request.form.get('username')
        password = request.form.get('password')
        # Ensure username was submitted
        if not username:
            return ("must provide username")

        # Ensure password was submitted
        elif not password:
            return ("must provide password")

        # Query database for username
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))

        # Stores details of user
        usernames = cur.fetchall()
        usernames_list = []
        for index, x in enumerate(usernames):
            temp_dict = {
                "ID" : x[0],
                "username" : x[1],
                "hash" : x[2]
            }
            usernames_list.append(temp_dict.copy())

        # Ensure username exists and password is correct
        if len(usernames_list) != 1 or not check_password_hash(usernames_list[0]["hash"], request.form.get("password")):
            return ("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = usernames_list[0]["ID"]
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        articles_list.clear()
        tickers = get_tickers()
        for ticker in tickers:
            # Sets limit for number of articles
            limit = 0
            # Gets page for specific article
            url = f"https://finance.yahoo.com/quote/{ticker}"
            result = requests.get(url)
            doc = BeautifulSoup(result.text, "html.parser")
            
            # Finds articles in Yahoo Finance Page
            articles = doc.findAll(class_="js-stream-content Pos(r)")

            # Stores info about each article in articles_list
            for count, article in enumerate(articles, start=(len(articles_list))):

                # Sets max number of articles per company
                limit += 1
                if limit >= MAX_ARTICLES:
                    break

                # Accessing HTML elements
                temp_dict = {}
                source = article.find(class_="C(#959595) Fz(11px) D(ib) Mb(6px)")
                link = article.find(href=True).get('href')
                title = source.next_sibling
                description = title.next_sibling

                # Adding article to dictionary
                temp_dict['stock'] = ticker
                temp_dict['title'] = title.text
                temp_dict['description'] = description.text
                temp_dict['source'] = source.text
                temp_dict['link'] = url+link
                temp_dict['id'] = count

                # Adding dictionary to list
                articles_list.append(temp_dict.copy())
        
        #Randomises feed
        shuffle(articles_list)

        return render_template("index.html", articles=articles_list, tickers=tickers)
    else:
        # Adds article to read_later list
        article_number = int(request.form.get('article_id'))
        for article in articles_list:
            if article['id'] == article_number:
                # Update saved article db
                cur.execute("INSERT INTO saved(user_id, stock, title, a_description, a_source, link, article_id) VALUES(%s, %s, %s, %s, %s, %s, %s)",
                (session['user_id'], article['stock'], article['title'], article['description'], article['source'], article['link'], article['id']))
                connection.commit()                    
                break
        return redirect("/saved")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    # Adds users stock into feed
    if request.method == "POST" and request.form.get('stock_add'):
        stock = request.form.get('stock_add').upper()
        if stock not in get_tickers():
            cur.execute("INSERT INTO tickers(user_id, ticker) VALUES(%s, %s)", (session['user_id'], stock))
            connection.commit()
        return redirect("/add")
        # Removes users stock from feed
    elif request.method == "POST" and request.form.get('stock_removal'):
        stock = request.form.get('stock_removal').upper()
        cur.execute("DELETE FROM tickers WHERE user_id = %s and ticker = %s", (session['user_id'], stock))
        connection.commit()
        return redirect("/add")
    else:
        return render_template("add.html", tickers=get_tickers())


@app.route("/saved", methods=["POST","GET"])
@login_required
def saved():
    # Removes article from saved
    if request.method=="POST":
        article_id = int(request.form.get("article_id"))
        for article in articles_list:
            if article['id'] == article_id:
                # Removes article from saved db
                cur.execute("DELETE FROM saved WHERE user_id = %s AND article_id = %s", (session['user_id'], article_id))
                connection.commit()
                break
        return redirect("/saved")
    else:
        cur.execute("SELECT stock, title, a_description, a_source, link, article_id FROM saved WHERE user_id = %s", (session['user_id'],))
        results_temp = cur.fetchall()
        read_later = []
        for index, result in enumerate(results_temp):
            temp_dict = {
                "stock":result[0],
                "title":result[1],
                "description":result[2],
                "source":result[3],
                "link":result[4],
                "id": result[5]
            }
            read_later.append(temp_dict.copy())
        return render_template("saved.html", read_later=read_later)

@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

if __name__== '__main__':
    app.run(debug=True)