class lulc_lat_long_file():
    
    
    def __init__(self, filepath, all_files:list):
        '''
        filepath:str
        all_files:list
        '''
        self.filepath = filepath
        self.all_files = all_files


        
        
    def build(self):
        all_stations = pd.read_excel(self.filepath)
        sites =[ file[-24:-18] for file in self.all_files]
        locations = all_stations[all_stations['SITE_ID'].isin(sites)]
        options = ['LOCATION_LAT','LOCATION_LONG','LOCATION_ELEV']
        lat_long_df = all_stations[all_stations['VARIABLE'].isin(options)]

        self.df =lat_long_df.pivot(index = ["SITE_ID",'GROUP_ID'], columns = 'VARIABLE', values = ['DATAVALUE']).reset_index().drop(columns = ['GROUP_ID'])
        self.df = self.df.T.reset_index(drop = True).T
       
        self.df.rename(columns = {0:"SITE_ID",1:"ELEVATION", 2:"LATITUDE", 3:"LONGITUDE"}, inplace = True)
        self.lat_longfloat('LATITUDE')
        self.lat_longfloat('LONGITUDE')
        self.lat_longfloat('ELEVATION')
        self.df = self.df.groupby('SITE_ID')[["LATITUDE","LONGITUDE","ELEVATION"]].agg("mean").reset_index()

        lulc_options = ['IGBP']
        lulc_df = all_stations[all_stations['VARIABLE'].isin(lulc_options)]
        lulc_df = lulc_df.rename(columns ={"DATAVALUE": "LULC"})
        lulc_df = lulc_df.drop(columns = list(lulc_df.columns[1:4]) ).reset_index(drop = True)


        lulc_lat_long_df = pd.merge(lulc_df,self.df,on = ["SITE_ID"] )
        
        
        lulc_lat_long_df.to_csv(self.save_path)
    def lat_longfloat(self,col):
        self.df[col] = self.df[col].astype(float)  