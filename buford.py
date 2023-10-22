import logging
import json
import pandas as pd
import time
from googlemaps.places import places
from googlemaps.geocoding import geocode
from config import *
import matplotlib.pyplot as plt
import folium
from folium import Icon
from IPython.display import display

def get_coordinates(address):
    everything = geocode(gmaps, address)
    raw_coords = json.dumps(everything[0]['geometry']['location'])
    raw_coords = json.loads(raw_coords)
    #logging.info(f"coordinates {raw_coords} have been extracted")
    return str(raw_coords["lat"]) +"," + str(raw_coords["lng"])

def get_restaurants():
    restos = {}
    for x in range(1, 4):
        if x == 1:
            restos['rest_1'] = places(query=query, client=gmaps)
            logging.info(f"received page 1 of restaurants")
            time.sleep(2)
        else:
            restos[f'rest_{x}'] = places(query=query, client=gmaps, page_token=restos[f'rest_{(x-1)}']["next_page_token"])
            logging.info(f"page {x} received")
            time.sleep(2)
    return restos

def get_df(restos: dict):
    df = pd.DataFrame(restos)
    df = df.transpose()
    page_1 = pd.json_normalize(df['results'][0])
    page_2 = pd.json_normalize(df['results'][1])
    page_3 = pd.json_normalize(df['results'][2])
    df = pd.concat([page_1, page_2, page_3])
    df = df[cols].reset_index()
    logging.info("dataframe created")
    return df

def place_coordinates(df: pd.DataFrame):
    cs = []
    for address in df['formatted_address']:
        c = get_coordinates(address=address)
        cs.append(c)
    df['geometry'] = cs
    sep = ','
    joined = sep.join(cs)
    new_cs = joined.split(sep)
    lats = new_cs[::2]
    lngs = new_cs[1::2]
    df['lat'] = lats
    df['lng'] = lngs
    return df

def get_rating_color(df):
    rating = float(df['rating'])
    if 4.7 <= rating and rating <= 5.0:
        color = 'cadetblue'
        return color
    elif 4.5 <= rating and rating < 4.7:
        color = 'darkgreen'
        return color
    elif 4.0 <= rating and rating < 4.5:
        color = 'green'
        return color
    elif 3.6 <= rating and rating < 4.0:
        color = 'lightgreen'
        return color
    elif 3.2 <= rating and rating < 3.6:
        color = 'beige'
        return color
    elif 2.8 <= rating and rating < 3.2:
        color = 'red'
        return color

def map_restaurants_by_rating(df: pd.DataFrame):
    m = folium.Map(location=[33.85, -84.28], zoom_start=10)
    for i in range(len(df.index)):
        color=get_rating_color(df.iloc[i])
        folium.Marker(
            location = (df.iloc[i]['lat'], df.iloc[i]['lng']),
            popup=df.iloc[i]['name'],
            icon=folium.Icon(color=color, icon_color=color)
        ).add_to(m)
    display(m)