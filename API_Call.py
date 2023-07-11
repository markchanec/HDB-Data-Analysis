#!/usr/bin/env python
# coding: utf-8

import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
import requests
import json

# force IPv4 for faster response
import socket
import requests.packages.urllib3.util.connection as urllib3_cn
def allowed_gai_family():
    family = socket.AF_INET    
    return family
urllib3_cn.allowed_gai_family = allowed_gai_family

#api call to get lat long of address
def get_latlong(address):
    api = "https://developers.onemap.sg/commonapi/search?returnGeom=Y&getAddrDetails=N&searchVal="
    req = requests.get(api+address) #'&pageNum=1'
    if req.status_code == 200:
        coords = json.loads(req.text)
        if coords['found'] > 0:
            lat = coords['results'][0]['LATITUDE']
            long = coords['results'][0]['LONGITUDE']
            return lat, long
    return np.nan, np.nan

#process with known address
def process_df(data, name):
    #to improve the algo by not repeating request if same address
    prev_address,    prev_lat,    prev_long    = "", np.nan, np.nan
    current_address, current_lat, current_long = "", np.nan, np.nan

    for i in range(len(data)):
        current_address = data.loc[i,name]
        print('Processing %i record' %i, end='\r')
        if current_address != prev_address:
            current_lat, current_long = get_latlong(current_address)
        else:
            current_lat, current_long = prev_lat, prev_long
        data.loc[i,'lat'] = current_lat
        data.loc[i,'long'] = current_long
        
#api call to get list of search term
def get_list(api):
    req = requests.get(api)
    if req.status_code == 200:
        coords = json.loads(req.text)
        pages = coords['totalNumPages']
    
    results = ''
    list_results = []
    
    #get all results from each page
    for i in range(1, pages+1):
        query = api + '&pageNum=' + str(i)
        req = requests.get(query)
        if req.status_code == 200:
            coords = json.loads(req.text)
            if coords['found'] > 0:
                results = len(coords['results'])
                for r in range(results):
                    list_results.append([coords['results'][r]['SEARCHVAL'], 
                                     coords['results'][r]['LATITUDE'],
                                     coords['results'][r]['LONGITUDE'] ])
                
    return list_results

