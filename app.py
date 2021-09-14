from flask import Flask
from flask import redirect, render_template
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)

@app.route("/")
def index():

    ticker = "FB"
    url = f"https://finance.yahoo.com/quote/{ticker}/"
    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser")


    articles_list = []
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
        temp_dict['title'] = title.text
        temp_dict['description'] = description.text
        temp_dict['source'] = source.text
        temp_dict['link'] = link

        # Adding dictionary to list
        articles_list.append(temp_dict.copy())

    return render_template("index.html", articles=articles_list)