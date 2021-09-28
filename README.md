# NEWSCRAPER
#### Video Demo:  https://youtu.be/Rqqc8ut3DLE
#### Description:

#### This web app allows you to create portfolio of companies that you would like to keep up to date on news from
#### The latest news articles are web scraped from Yahoo Finance using Beautiful Soup
#### Beautiful soup was my web scraper of choice due to the good documentation and comprehensive amount of online resources avaiable demonstrating how to use it (especially on YouTube)
#### The info scraped for ecah article are as follows: The company; the title of the article; the main description; the source of the article and the link to the full article
#### Articles are displayed on the homepage along with the list of companies in a users portfolio in a sidebar
#### Users can save articles to be read later and remove them once they are done/decide they are no longer interested.
#### Users can add and remove companies from their portfolio in the "stocks" tab
#### New users are able to register for accounts and log in



#### For the homepage I decided to shuffle the feedd - this is because when a user adds a list of stocks to their portfolio, initially, the articles came up in blocks (i.e one group of articles relating to stock X then another group of articles relating to stock Y etc)
#### By shuffling the feed I avoidn this issue all together and allow the generation of an updated list of articles in a different order everytime a user reloads the home page - I feel like this is better design as this would stop articles from tickers that are added later on by the user from going unread

#### app.py contains the code for the Flask app
#### The files in the "templates" folder are the HTML pages for the app
#### The static folder contains some custom css
#### Given additional time I would have encorporated some Javascript - this would have allowed an increased amount of interactivity to the web app

#### Uses MySQL database to store user details including login details, the companies in a user's portfolio and any saved articles.
#### Encorporating a database allowed a users details to be saved even after the server is reloaded which would be critical for the "Saved" article feature
#### Inside the db I stored user login details (username and password) tickers(user_id and ticker) as well as saved articles(user_id, stock, title, description, source, link)
#### I chose not to store the feed inside a table since I wanted to the feed to be changed and updated when the user reloads the home page so there was little value in storing the entire list of articles
#### I chose to use MySQL instead of sqlite3 to try using a different system as well as easier implementation if I choose to host the web app onto Heroku


#### Bootstrap was used to style the app to create a clean, modern almost "glassy" look
#### Initially was going to go with a dark-mode look but the lighter theme with shadows was much more aesthetically pleasing


#### One thing I was unable to implement was some sort of pagination system. All the articles from a users chosen portfolio will be loaded onto a single page
#### If a user has lot of stocks in portfolio it would cause the home page to take quite a long time to load - to get around this issue I limited the amount of articles per user to 5
