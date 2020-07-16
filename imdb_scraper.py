# Requests will allow us to send HTTP requests to get HTML files
# BeautifulSoup will help us parse the HTML files
# pandas will help us assemble the data into a DataFrame to clean and analyze it
# NumPy will add support for mathematical functions and tools for working with arrays

import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

# https://medium.com/better-programming/the-only-step-by-step-guide-youll-need-to-build-a-web-scraper-with-python-e79066bd895a
import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

url = "https://www.imdb.com/search/title/?groups=top_1000&ref_=adv_prv"
headers = {"Accept-Language": "en-US, en;q=0.5"}
results = requests.get(url, headers=headers)

soup = BeautifulSoup(results.text, "html.parser")

titles = []
years = []
time = []
imdb_ratings = []
metascores = []
votes = []
us_gross = []

movie_div = soup.find_all('div', class_='lister-item mode-advanced')

for container in movie_div:
    # name
    name = container.h3.a.text
    titles.append(name)

    # year
    year = container.h3.find('span', class_='lister-item-year').text
    years.append(year)

    # runtime
    runtime = container.p.find('span', class_='runtime').text if container.p.find('span',
                                                                                  class_='runtime').text else '-'
    time.append(runtime)

    # IMDB rating
    imdb = float(container.strong.text)
    imdb_ratings.append(imdb)

    # metascore
    m_score = container.find('span', class_='metascore').text if container.find('span', class_='metascore') else '-'
    metascores.append(m_score)

    # There are two NV containers, grab both of them as they hold both the votes and the grosses
    nv = container.find_all('span', attrs={'name': 'nv'})

    # filter nv for votes
    vote = nv[0].text
    votes.append(vote)

    # filter nv for gross
    grosses = nv[1].text if len(nv) > 1 else '-'
    us_gross.append(grosses)

# building our Pandas dataframe
movies = pd.DataFrame({
    'movie': titles,
    'year': years,
    'timeMin': time,
    'imdb': imdb_ratings,
    'metascore': metascores,
    'votes': votes,
    'us_grossMillions': us_gross,
})
# removing null values to avoid errors
movies.dropna(inplace=True)

# cleaning data with Pandas
movies['year'] = movies['year'].str.extract('(\d+)').astype(int)
movies['timeMin'] = movies['timeMin'].str.extract('(\d+)').astype(int)
movies['votes'] = movies['votes'].str.replace(',', '').astype(int)
movies['us_grossMillions'] = movies['us_grossMillions'].map(lambda x: x.lstrip('$').rstrip('M'))
movies['us_grossMillions'] = pd.to_numeric(movies['us_grossMillions'], errors='coerce')
movies['metascore'] = pd.to_numeric(movies['metascore'], errors='coerce').fillna(0).astype(int) # Replace any thing
# that is not a digit with 0, so we can convert to int

movies.to_csv('movies.csv')