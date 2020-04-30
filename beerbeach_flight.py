import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests

from bs4 import BeautifulSoup
import re

def direct_flights(airportcode, month, max_flight_hours):
    max_flight_time_one_way = max_flight_hours*60
    url = requests.get("https://www.flightsfrom.com/{}/destinations?durationFrom=0&durationTo={}".format(airportcode,max_flight_time_one_way))
    if url.status_code != 200:
        print('Flight Time page loading Error')

    soup = BeautifulSoup(url.content,'html.parser')

    tag = soup.find_all('li', class_=['airport-content-destination-listitem','airport-content-destination-listitem-hidden'])
    destinations = pd.DataFrame(columns = ['Country','City'])
    for item in tag:
        if 'data-name' in item.attrs:
            if 'data-country' in item.attrs:
                destinations = destinations.append({'Country':item['data-country'], 'City' : item['data-name']},ignore_index = True)

    #print(destinations)
    return destinations