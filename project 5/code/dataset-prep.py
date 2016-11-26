# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 11:55:36 2016

@author: ganjalf
"""

import pandas as pd
import ast
from sklearn.preprocessing import MultiLabelBinarizer
mlb = MultiLabelBinarizer()
columns=["junction_id","junction_type","x","y","z","isRoundabout","connections","avg_lane_speed","lane_speeds_std_deviation",
 "avg_lane_length","lane_length_standard_deviation","edge_types","edge_prioities","number_of_lanes"
 ,"intl_connections","intl_avg_lane_speed","intl_lane_speeds_std_deviation",
 "intl_avg_lane_length","intl_lane_length_standard_deviation","intl_edge_types","intl_edge_prioities","intl_number_of_lanes"]

file_name= "dataset-cgn-tl.csv"
df= pd.read_csv(file_name)
df.columns=columns
df['isRoundabout']= df['isRoundabout'].astype(float)
df= df.drop(df.columns[[0, 1, 4,6,14]], axis=1)
#print df
#df.apply(mapTypes, axis=1) # equiv to df.sum(1)
#df['edge_types'].apply(lambda x: mlb.fit(x))
fixed_types= df['edge_types'].map(lambda x: ast.literal_eval(x))

mlb=mlb.fit(fixed_types)
result= mlb.transform(fixed_types)
#print list(mlb.classes_)

dfn= pd.DataFrame(result,columns=list(mlb.classes_))
df=df.drop('edge_types',1)
dff=pd.concat([df,dfn],axis=1)

#print ast.literal_eval((df['edge_types'][0]))
#print (df['edge_types'][0])
#df1= pd.get_dummies(df)
dff.to_csv("test.csv")