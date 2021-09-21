from flask import Flask
from flask import redirect, render_template, request, redirect
import mysql.connector
from mysql.connector import Error
import yaml
from bs4 import BeautifulSoup
from random import shuffle
import requests
import re

app = Flask(__name__)

# Configure db
db = yaml.load(open('db.yaml'))

connection = mysql.connector.connect(host=db['mysql_host'],
                                         database=db['mysql_db'],
                                         user=db['mysql_user'],
                                         password= db['mysql_password'])

cur = connection.cursor()
cur.execute("INSERT INTO news.test(id, ticker) VALUES (1, 'TSLA')")
connection.commit()
cur.execute("SELECT * FROM test")
result = cur.fetchall()

for x in result:
    print(x)

# Defining some global variables
articles_list = []
read_later = []
MAX_ARTICLES = 5
tickers = set()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        articles_list.clear()
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
                read_later.append(article)
                break
        return redirect("/readlater")


@app.route("/add", methods=["GET", "POST"])
def add():
    # Adds users stock into feed
    if request.method == "POST" and request.form.get('stock_add'):
        stock = request.form.get('stock_add').upper()
        tickers.add(stock)
        return redirect("/add")
    elif request.method == "POST" and request.form.get('stock_removal'):
        stock = request.form.get('stock_removal').upper()
        tickers.remove(stock)
        return redirect("/add")
    else:
        return render_template("add.html", tickers=tickers)


@app.route("/readlater", methods=["POST","GET"])
def readlater():
    # Removes article from read later
    if request.method=="POST":
        article_id = int(request.form.get("article_id"))
        for article in articles_list:
            if article['id'] == article_id:
                read_later.remove(article)
                break
        return redirect("/readlater")
    else:
        return render_template("readlater.html", read_later=read_later)

if __name__== '__main__':
    app.run(debug=True)