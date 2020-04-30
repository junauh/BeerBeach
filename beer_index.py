import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests

from bs4 import BeautifulSoup
import re

from beerbeach_flight import direct_flights 
from beerbeach_weather import good_weather 

airportcode = input("Enter Airport Code:")
month = input("Enter Month to travel:")
max_flight_hours = float(input("Enter Max flight time in hours, one way:"))
max_temp = float(input("Enter Min water temperature in C:"))
beer_price = float(input("Enter Max 0.5L Draft Beer in SEK:"))



destinations = direct_flights(airportcode, month, max_flight_hours)

selected_beer_list = []

city_url = good_weather(destinations,max_temp,month)

def cheapbeer(city_url,max_temp,beer_price):
    for city in city_url['City']:
        beer_url = 'https://www.numbeo.com/cost-of-living/in/{}?displayCurrency=SEK'.format(city)
        #print(beer_url)
        page_selected_beer_dict = requests.get(beer_url)
        soup_selected_beer_dict= BeautifulSoup(page_selected_beer_dict.content,'html.parser')
        
        tag = soup_selected_beer_dict.find_all('td', class_='priceValue tr_highlighted')
        
        tag_string = ''
        if len(tag) == 26:
            for item in tag[1]:
                tag_string += str(item)
            #print(tag_string)-47.01 kr
            beer_sek = float(tag_string.split()[0])
            selected_beer_list.append(beer_sek)
            
    selected_beer = pd.Series(selected_beer_list)
    city_url['0.5L Draft Beer[SEK]'] = selected_beer
    final = city_url[(city_url['Water Temp'] > max_temp) & (city_url['0.5L Draft Beer[SEK]'] < beer_price)]
    final = final[['City','Water Temp','0.5L Draft Beer[SEK]']]
    return final


final = cheapbeer(city_url,max_temp,beer_price)

if final.empty:
    print('No Beer Beach Destinations, please change inputs')
else:
    print('BEER BEACH DESTINATIONS from {} in {}'.format(airportcode,month))
    print(final)