import googlemaps
import logging

gmaps = googlemaps.Client(key="key")
query = "restaurant on buford hwy"
cols = ['formatted_address','name','price_level','rating','user_ratings_total']
logging.getLogger().setLevel(logging.INFO)
