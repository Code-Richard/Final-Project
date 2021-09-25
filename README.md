# NEWS TRACKER
#### Video Demo:  https://youtu.be/Rqqc8ut3DLE
#### Description:

#### This web app allows you to create portfolio of companies that you would like to keep up to date on news from
#### The latest news articles are web scraped from Yahoo Finance using Beautiful Soup
#### The info scraped for ecah article are as follows: The company; the title of the article; the main description; the source of the article and the link to the full article
#### Articles are displayed on the homepage along with the list of companies in a users portfolio in a sidebar
#### Users can save articles to be read later and remove them once they are done/decide they are no longer interested.
#### Users can add and remove companies from their portfolio in the "stocks" tab
#### New users are able to register for accounts and log in 

#### app.py contains the code for the Flask app
#### The files in the "templates" folder are the HTML pages for the app
#### The static folder contains some custom css 

#### Uses MySQL database to store user details including login details, the companies in a user's portfolio and any saved articles.
#### I chose to use MySQL instead of sqlite3 simply to try using a different system

#### Bootstrap was used to style the app to create a clean, modern look
