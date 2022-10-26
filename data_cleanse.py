from ftplib import FTP
import string
from unicodedata import name
import pandas as  pd
import glob
import os
from zipfile import ZipFile
import json

allfilespath = '/Users/csummitt/210/base_Items/*.zip'
filepath= '/Users/csummitt/210/base_Items/cleaned'

class data_cleanse():

    def __init__(self, tower_filepath:string,  latlong_df:pd.DataFrame, air_temp_col:string, gpp_col:string, ts_col:string, dates =['TIMESTAMP_START']) -> None:
        '''
        tower_filepath: string
            filepath to tower data
        
        '''
        self.filepath = tower_filepath
        # self.metadata_filepath= metadata_filepath
        self.lulc_lat_long_df = latlong_df
        self.dates = dates
        self.col_sum = gpp_col
        self.col_mean= air_temp_col
        self.col_mean2= ts_col
        self.cols = ['TIMESTAMP_START',gpp_col,air_temp_col,ts_col]


    def make_df(self):
        '''
        '''
        self.tower_df = pd.read_csv(self.filepath,  low_memory = True, header=2, na_values="-9999",
                                     parse_dates=self.dates,usecols= self.cols)
        idx_start = self.filepath.index("AMF_US") +4
        idx_end = idx_start + 6
        self.site_id = self.filepath[idx_start:idx_end]

        #convert hourly measurements to just yyyy-mm-dd to roll up the days readings
        #mean of Air Temp, Summ of GPP
        self.tower_df['DATE']= pd.to_datetime(self.tower_df['TIMESTAMP_START']).dt.date
        gpp_df = self.tower_df.groupby('DATE')[self.col_sum].sum().reset_index()
        air_temp_df = self.tower_df.groupby('DATE')[self.col_mean].mean().reset_index()
        soil_temp_df= self.tower_df.groupby('DATE')[self.col_mean2].mean().reset_index()

        #join GPP and Temp data together add site_id then join on lat long data ON site_id
        self.tower_df = pd.merge(gpp_df,air_temp_df, on= 'DATE', how = 'inner')
        self.tower_df = pd.merge(self.tower_df, soil_temp_df, on="DATE", how = "inner")
        self.tower_df= self.tower_df.rename(columns={self.col_mean:'TA', self.col_mean2:"TS", self.col_sum:"GPP"})
        self.tower_df['SITE_ID'] = self.site_id
        self.combined_df = self.tower_df.merge(self.lulc_lat_long_df, on= 'SITE_ID', how = 'left')
        return self.combined_df



    





if name ==__main__:
import os
from zipfile import ZipFile
import json
from pathlib import Path
home = str(Path.home())

allfilespath = home+'/210/base_Items/*.zip'
filepath= home + '/210/base_Items/cleaned'

lulc_lat_long_df = pd.read_csv(home + '/210/mids-w210-capstone/data/ameriflux_lulc_lat_long.csv', usecols=['SITE_ID','LULC','LATITUDE','LONGITUDE','ELEVATION'])



with open("/Users/csummitt/210/mids-w210-capstone/data/potential_sites2.json", "r") as file:
    config = json.load(file)


all_files = glob.glob(home + '/210/base_Items/*.zip')
for file in all_files:
    with ZipFile(file, 'r') as compressed:
            compressed.extractall(home + '/210/base_Items/test')
    for csv in glob.glob(home + '/210/base_Items/test/*.csv'):
        idx_start = csv.index("AMF_US") +4
        idx_end = idx_start + 6
        site_id = csv[idx_start:idx_end]
        try:
            air_temp =config[site_id]["TA"]
            gpp= config[site_id]["GPP"]
            ts=config[site_id]["TS"]
        except KeyError as arg:
            print (arg ," Not found")
        try:
            print(f'try {site_id}')
            cleaned = data_cleanse(csv,lulc_lat_long_df,  air_temp[0],gpp[0], ts[0])
            cleaned = cleaned.make_df()
            print(filepath +'/'+ site_id +".csv" )
            cleaned.to_csv(filepath + site_id +".csv" )
        except:
            
            print("did not load into df:" +file)
        os.remove(csv)
    