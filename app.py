from flask import Flask
from flask import redirect, render_template, request, redirect
from bs4 import BeautifulSoup
from random import shuffle
import requests
import re

app = Flask(__name__)
articles_list = []
tickers = set()
@app.route("/")
def index():
    
    # Creates a list of empty dictionaries to store article data on each stock
    for ticker in tickers:
        # Gets page for specific article
        url = f"https://finance.yahoo.com/quote/{ticker}"
        result = requests.get(url)
        doc = BeautifulSoup(result.text, "html.parser")
        
        # Finds articles in Yahoo Finance Page
        articles = doc.findAll(class_="js-stream-content Pos(r)")

        # Stores info about each article in articles_list
        for article in articles:
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


            # Adding dictionary to list
            articles_list.append(temp_dict.copy())
    
    shuffle(articles_list)

    return render_template("index.html", articles=articles_list)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        stock = request.form.get('stock')
        tickers.add(stock)
        return redirect("/add")
    else:
        return render_template("add.html")
