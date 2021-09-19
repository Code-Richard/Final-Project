from flask import Flask
from flask import redirect, render_template, request, redirect
from bs4 import BeautifulSoup
from random import shuffle
import requests
import re

app = Flask(__name__)
articles_list = []
read_later = []
tickers = set()
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        for ticker in tickers:
            # Gets page for specific article
            url = f"https://finance.yahoo.com/quote/{ticker}"
            result = requests.get(url)
            doc = BeautifulSoup(result.text, "html.parser")
            
            # Finds articles in Yahoo Finance Page
            articles = doc.findAll(class_="js-stream-content Pos(r)")

            # Stores info about each article in articles_list
            for count, article in enumerate(articles, start=(len(articles_list))):
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

        return render_template("index.html", articles=articles_list)
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
    if request.method == "POST":
        stock = request.form.get('stock').upper()
        tickers.add(stock)
        return redirect("/add")
    else:
        return render_template("add.html")


@app.route("/readlater", methods=["POST","GET"])
def readlater():
    if request.method=="POST":
        article_id = int(request.form.get("article_id"))
        for article in articles_list:
            if article['id'] == article_id:
                read_later.remove(article)
                break
        return redirect("/readlater")
    else:
        return render_template("readlater.html", read_later=read_later)
        