import pandas as pd
import json
  
# Get the site ids 
# These are the keys of the json file potential_sites2.json
potential_sites_file = open('data/potential_sites2.json')
potential_sites_dict = json.load(potential_sites_file)
potential_site_names = list(potential_sites_dict.keys())

# Get the csv with all site data
all_sites_df = pd.read_csv("data/ameriflux_lulc_lat_long.csv")

# Write a new csv that only has data for sites we want
wanted_site_and_info  = all_sites_df[all_sites_df['SITE_ID'].isin(potential_site_names)]
wanted_site_and_info.to_csv('data/wanted_sites.csv')
