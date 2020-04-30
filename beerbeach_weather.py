import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests

from bs4 import BeautifulSoup
import re

from beerbeach_flight import direct_flights 

def good_weather(destinations,max_temp, month):
    url = 'https://www.weather2visit.com/country-list'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    page = requests.get(url, headers=headers)

    if page.status_code != 200:
        print('Water Temperature page loading Error')
        
    soup = BeautifulSoup(page.content,'html.parser')

    #navigate through an soup document via 'Tag' object 'a' to extract all country lists with continent
    tag = soup.find_all('a')

    #find children inside li tag with href attribute
    countries = [item['href'] for item in tag if 'href' in item.attrs]

    #regex = r'/{3}'
    final_country = []
    for item in countries:
        #use regular expression to only parsing element with country information - element with 3 '/' i.e. '/africa/burundi/'
        if (len(re.findall('/',item)) == 3):
            country = item.split('/')[2]
            if country.title() in destinations['Country'].unique():
                final_country.append(item)

    #countries_url = pd.Series(final_country)

    cities_list = []
    weather_url = pd.DataFrame(columns = ['City','City_url'])

    for country in final_country:
        url = 'https://www.weather2visit.com{}'.format(country)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        page_beach_country_city = requests.get(url, headers=headers)
        soup_beach_country_city = BeautifulSoup(page_beach_country_city.content,'html.parser')   
        
        #navigate through an soup document via 'Tag' object 'a' to extract all country lists with continent
        sbccfa = soup_beach_country_city.find_all('a')
        cities_list = [item['href'] for item in sbccfa if 'href' in item.attrs]
        cities_list = list(set(cities_list))
        
        for c in cities_list:
            pattern = re.compile(country)
            if pattern.match(c):
                cityhtm = c.split('/')[3]
                city = cityhtm.split('.')[0]
                url = c.split('.')[0]
                weather_url = weather_url.append({'City':city.title(), 'City_url' : url},ignore_index = True)

    weather_url['City'] = weather_url['City'].drop_duplicates()
    weather_url.describe()

    # url = 'https://www.weather2visit.com{c}-{m}.htm'.format(c=city_based_on_travel_time,m = month)
    #https://www.weather2visit.com/europe/sweden/malmoe-august.htm

    url = ''
    city_url = pd.DataFrame(columns = ['City','City_url'])
    alt_filtered_cities = pd.DataFrame(columns = ['City','Country'])

    #means city and city_u are not the same
    for city in destinations['City']: 
        if city in weather_url['City'].unique():
            url = weather_url[weather_url['City'] == city]['City_url'].to_string(index=False)
            url = url.strip()
            city_url = city_url.append({'City':city, 'City_url' : 'https://www.weather2visit.com{c}-{m}.htm'.format(c=url,m = month)},ignore_index = True)
            #print('https://www.weather2visit.com{c}-{m}.htm'.format(c=url,m = month))
        else:
            alt_filtered_cities = alt_filtered_cities.append({'City': city, 'Country': destinations[destinations['City'] == city]['Country']},ignore_index =True)
            
    #print(city_url)

    selected_city_list = []

    for c_url in city_url['City_url']:
        page_selected_city = requests.get(c_url, headers=headers)
        soup_selected_city = BeautifulSoup(page_selected_city.content,'html.parser')
        tag = soup_selected_city.find('th', {'id': 'sst'})
        try:
            temp = tag.find_next('span', {'class': 'cen'}).get_text(strip=True)
            temp = temp.replace('°C','')
            temp = float(temp)
        except AttributeError:
            temp = 0
        #print(temp)
        selected_city_list.append(temp)
    #print(selected_city_list)
    selected_city = pd.Series(selected_city_list)
    city_url['Water Temp'] = selected_city

    final_city_url = city_url[city_url['Water Temp'] > max_temp]
    #print(final_city_url)
    return final_city_url
