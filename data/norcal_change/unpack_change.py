import pandas as pd
import json
import re

# Read in all files 
change17 = pd.read_csv("norcal_change_2017.csv").drop(['system:index', ".geo"], axis=1)
change18 = pd.read_csv("norcal_change_2018.csv").drop(['system:index', ".geo"], axis=1)
change19 = pd.read_csv("norcal_change_2019.csv").drop(['system:index', ".geo"], axis=1)
change20 = pd.read_csv("norcal_change_2020.csv").drop(['system:index', ".geo"], axis=1)
change21 = pd.read_csv("norcal_change_2021.csv").drop(['system:index', ".geo"], axis=1)

# Set Year
change17["year"] = 2017
change18["year"] = 2018
change19["year"] = 2019
change20["year"] = 2020
change21["year"] = 2021

# Convert "result" from a string of a list of dictionaries to a dataframe
def unpack_change(change_string):
	res = [json.loads(idx.replace("'", '"')) for idx in [change_string]]
	return pd.DataFrame.from_dict(res[0])


# For each dataset unpack the values
for df in [change17, change18, change19, change20, change21]:
	for i, row in df.iterrows():	
		ifor_val = unpack_change(row["result"]).set_index("change").transpose()
		for k in ifor_val.keys():
			df.at[i, k] = ifor_val[k]["sum"]


# Join all years
all_change = pd.concat([change17,change18,change19,change20,change21], ignore_index=True).reset_index()

# Write to CSV
all_change.to_csv("all_change.csv")


# Read CSV into DF
all_change = pd.read_csv("all_change.csv")

# Examine content
print(all_change.describe())
print(all_change.head())
