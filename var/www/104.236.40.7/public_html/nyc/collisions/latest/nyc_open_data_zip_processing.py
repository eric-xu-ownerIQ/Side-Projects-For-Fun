# Eric Xu , 2017-02, 2017-05


import pandas as pd
import numpy as np
import requests
import json
import time
import datetime
import urllib2
import re
import os
import math
from pandas import DataFrame
from datetime import date
import time
from datetime import datetime
from datetime import timedelta

########## getting latest data and dates ##########
print 'processing latest data'

response = requests.get('https://data.cityofnewyork.us/resource/qiz3-axqb.json')

data_latest = pd.read_json(response.text)
print data_latest.columns
data_latest = data_latest.drop_duplicates(['unique_key'])
data_latest = data_latest.reset_index(drop = True)

ZipStats_latest = pd.DataFrame(zip(data_latest['zip_code'].value_counts().index,
                                   data_latest['zip_code'].value_counts().values))

ZipStats_latest.columns = ['zip','value']

ZipDataBase = pd.read_csv('/var/www/104.236.40.7/public_html/nyc/collisions/latest/ZipDataBaseWithArea.csv')

value_base = []

for zip_base in ZipDataBase['zip']:
    zip_base = str(zip_base)
    found = 0
    for each_zip, each_value in zip(ZipStats_latest['zip'], ZipStats_latest['value']):
        each_zip = str(int(float(each_zip)))
        if each_zip == zip_base:
            found = 1
            value_base.append(each_value)
            break
    if found == 0:
        value_base.append('N/A')
        
ZipDataBase['value'] = value_base        
ZipDataBase['zip'] = ZipDataBase.zip.map("{:05}".format)

# outputting ZipData.csv for latest
ZipDataBase.to_csv('/var/www/104.236.40.7/public_html/nyc/collisions/latest/ZipData.csv', index = False)


# normalizing collisions by zip code land area
value_base = []

for zip_base,sqmiles in zip(ZipDataBase['zip'],ZipDataBase['sqmiles']):
    zip_base = str(zip_base)
    found = 0
    for each_zip, each_value in zip(ZipStats_latest['zip'], ZipStats_latest['value']):
        each_zip = str(int(float(each_zip)))
        if each_zip == zip_base:
            found = 1
	    try:
            	value_base.append(round(float(each_value)/float(sqmiles),2))
            except:
		value_base.append('N/A')
            break
    if found == 0:
        value_base.append('N/A')
        
ZipDataBase['value'] = None
ZipDataBase['value'] = value_base        
# ZipDataBase['zip'] = ZipDataBase.zip.map("{:05}".format)

ZipDataBase.to_csv('/var/www/104.236.40.7/public_html/nyc/collisions/latest/ZipDataNormalized.csv', index = False)

print 'done processing latest data'

########## google maps api latest data to fill in missing zips ##########

print 'loading all data'
data_all = pd.read_csv('/var/www/104.236.40.7/public_html/nyc/collisions/AllData.csv')
data_all = data_all.drop_duplicates(['UNIQUE KEY'])
data_all = data_all.reset_index(drop = True)
print 'done loading all data'

# making sure data_all dates are correctly formated
print 'checking date format consistency'
consistent_dates = []
for each_date in data_all['DATE']:
    try:
        consistent_dates.append(datetime.strptime(str(each_date), "%m/%d/%Y").strftime('%Y-%m-%d'))
    except:
        try:
		consistent_dates.append(datetime.strptime(str(each_date), "%m/%d/%y").strftime('%Y-%m-%d'))
	except:
        	consistent_dates.append(str(each_date)[0:10])
data_all['DATE'] = None
data_all['DATE'] = consistent_dates
print consistent_dates[0:10]
print 'finished checking date format consistency'


# set of dates in all
data_all_dates = set(data_all['DATE'])
# print data_all_dates

# set of dates in latest
data_latest_dates = set((data_latest['date']))
new_each = []
for each in data_latest_dates:
    new_each.append(str(each)[0:10])
data_latest_dates = set(new_each)
print data_latest_dates

# checking if any dates are new
new_dates = []
for each_unique_latest_date in data_latest_dates:
    if each_unique_latest_date not in data_all_dates:
        new_dates.append(each_unique_latest_date)
print new_dates

date_min_list_latest = []
date_max_list_latest = []
updatetime_list_latest = []

date_min_list_latest.append(str(min(data_latest['date']))[0:10])
date_max_list_latest.append(str(max(data_latest['date']))[0:10])
string_value_latest = time.strftime('%l:%M%p ' + '(EST) ' + 'on %b %d, %Y')
updatetime_list_latest.append(string_value_latest)
        
# only proceed if new dates are found        
if len(new_dates) > 0:
    # take out any new dates from all data
    for take_out_date in data_latest_dates:
        data_all = data_all[data_all['DATE']!=take_out_date]
        data_all = data_all.reset_index(drop = True)
        
    print 'starting google maps api'

    latest_date_list = []
    for latest_date in data_latest['date']:
        latest_date_list.append(str(latest_date)[0:10])

    data_latest['date'] = None
    data_latest['date'] = latest_date_list
    try:
	len(data_latest['contributing_factor_vehicle_5'])
    except:
	data_latest['contributing_factor_vehicle_5'] = None

    try:
        len(data_latest['vehicle_type_code_5'])
    except:
        data_latest['vehicle_type_code_5'] = None


    zipped_array = zip(data_latest['date'], data_latest['time'], data_latest['borough'], 
                       data_latest['zip_code'], data_latest['latitude'], data_latest['longitude'], 
                       data_latest['location'], data_latest['on_street_name'], 
                       data_latest['cross_street_name'], data_latest['off_street_name'], 
                       data_latest['number_of_persons_injured'], 
                       data_latest['number_of_persons_killed'], 
                       data_latest['number_of_pedestrians_injured'], 
                       data_latest['number_of_pedestrians_killed'], 
                       data_latest['number_of_cyclist_injured'], 
                       data_latest['number_of_cyclist_killed'], 
                       data_latest['number_of_motorist_injured'], 
                       data_latest['number_of_motorist_killed'], 
                       data_latest['contributing_factor_vehicle_1'], 
                       data_latest['contributing_factor_vehicle_2'], 
                       data_latest['contributing_factor_vehicle_3'], 
                       data_latest['contributing_factor_vehicle_4'], 
                       data_latest['contributing_factor_vehicle_5'], 
                       data_latest['unique_key'], data_latest['vehicle_type_code1'], 
                       data_latest['vehicle_type_code2'], 
                       data_latest['vehicle_type_code_3'], data_latest['vehicle_type_code_4'], 
                       data_latest['vehicle_type_code_5'])

    Rawdf = pd.DataFrame(zipped_array)

    Rawdf.columns = ['DATE', 'TIME', 'BOROUGH', 'ZIP CODE', 'LATITUDE', 'LONGITUDE',
                     'LOCATION', 'ON STREET NAME', 'CROSS STREET NAME', 'OFF STREET NAME', 
                     'NUMBER OF PERSONS INJURED', 'NUMBER OF PERSONS KILLED', 
                     'NUMBER OF PEDESTRIANS INJURED', 'NUMBER OF PEDESTRIANS KILLED', 
                     'NUMBER OF CYCLIST INJURED', 'NUMBER OF CYCLIST KILLED', 
                     'NUMBER OF MOTORIST INJURED', 'NUMBER OF MOTORIST KILLED', 
                     'CONTRIBUTING FACTOR VEHICLE 1', 'CONTRIBUTING FACTOR VEHICLE 2', 
                     'CONTRIBUTING FACTOR VEHICLE 3', 'CONTRIBUTING FACTOR VEHICLE 4', 
                     'CONTRIBUTING FACTOR VEHICLE 5', 'UNIQUE KEY', 'VEHICLE TYPE CODE 1', 
                     'VEHICLE TYPE CODE 2', 'VEHICLE TYPE CODE 3', 'VEHICLE TYPE CODE 4', 
                     'VEHICLE TYPE CODE 5']


    #add new columns
    Rawdf['YEAR']=None
    Rawdf['HOUR']=None
    Rawdf['MONTH']=None
    Rawdf['DAY']=None


    MONTH = []
    DAY = []
    YEAR = []
    HOUR = []

    zipped_array = zip(Rawdf['DATE'], Rawdf['TIME'])


    # ADD MONTH, DAY, YEAR, and HOUR columns

    for index,values in enumerate(zipped_array):
        DATE = str(values[0])
        TIME = values[1]
        if index % 90000 == 1000:
            print str(index) + ' of ' + str(len(zipped_array))
        MONTH.append(DATE[5:7])
        DAY.append(DATE[8:10])
        YEAR.append(DATE[0:4])
        hour_value = int(TIME[0:2].replace(':',''))

        if hour_value==0:
            HOUR.append('12:51 AM')
        elif hour_value==1:
            HOUR.append('1:51 AM')
        elif hour_value==2:
            HOUR.append('2:51 AM')
        elif hour_value==3:
            HOUR.append('3:51 AM')
        elif hour_value==4:
            HOUR.append('4:51 AM')
        elif hour_value==5:
            HOUR.append('5:51 AM')
        elif hour_value==6:
            HOUR.append('6:51 AM')
        elif hour_value==7:
            HOUR.append('7:51 AM')
        elif hour_value==8:
            HOUR.append('8:51 AM')
        elif hour_value==9:
            HOUR.append('9:51 AM')
        elif hour_value==10:
            HOUR.append('10:51 AM')
        elif hour_value==11:
            HOUR.append('11:51 AM')
        elif hour_value==12:
            HOUR.append('12:51 PM')
        elif hour_value==13:
            HOUR.append('1:51 PM')
        elif hour_value==14:
            HOUR.append('2:51 PM')
        elif hour_value==15:
            HOUR.append('3:51 PM')
        elif hour_value==16:
            HOUR.append('4:51 PM')
        elif hour_value==17:
            HOUR.append('5:51 PM')
        elif hour_value==18:
            HOUR.append('6:51 PM')
        elif hour_value==19:
            HOUR.append('7:51 PM')
        elif hour_value==20:
            HOUR.append('8:51 PM')
        elif hour_value==21:
            HOUR.append('9:51 PM')
        elif hour_value==22:
            HOUR.append('10:51 PM')
        elif hour_value==23:
            HOUR.append('11:51 PM')

    Rawdf['YEAR']=YEAR
    Rawdf['HOUR']=HOUR
    Rawdf['MONTH']=MONTH
    Rawdf['DAY']=DAY


    Rawdf['DAY OF WEEK'] = None
    DAY_OF_WEEK = []

    zipped_array = zip(Rawdf['DAY'], Rawdf['MONTH'], Rawdf['YEAR'])

    for index,values in enumerate(zipped_array):
        DAY = int(values[0])
        MONTH = int(values[1])
        YEAR = int(values[2])
        if index % 90000 == 1000:
            print str(index) + ' of ' + str(len(zipped_array))
        if index == 0:
            module_value = date(YEAR, MONTH, DAY).weekday()
            if module_value==0:
                dow_value = 'Monday'
            elif module_value==1:
                dow_value = 'Tuesday'
            elif module_value==2:
                dow_value = 'Wednesday'
            elif module_value==3:
                dow_value = 'Thursday'
            elif module_value==4:
                dow_value = 'Friday'
            elif module_value==5:
                dow_value = 'Saturday'
            elif module_value==6:
                dow_value = 'Sunday'
            else:
                dow_value = 'Unknown'
                print 'unknown day of week'
            DAY_OF_WEEK.append(dow_value)

            Previous_Day = DAY
            Previous_Month = MONTH
            Previous_DOW = dow_value

        # processes this loop when not the first index
        else:
            if (Previous_Day!=DAY) or (Previous_Month!=MONTH):
                module_value = date(YEAR, MONTH, DAY).weekday()
                if module_value==0:
                    dow_value = 'Monday'
                elif module_value==1:
                    dow_value = 'Tuesday'
                elif module_value==2:
                    dow_value = 'Wednesday'
                elif module_value==3:
                    dow_value = 'Thursday'
                elif module_value==4:
                    dow_value = 'Friday'
                elif module_value==5:
                    dow_value = 'Saturday'
                elif module_value==6:
                    dow_value = 'Sunday'
                else:
                    dow_value = 'Unknown'
                    print 'unknown dow'
                DAY_OF_WEEK.append(dow_value)

            else:
                DAY_OF_WEEK.append(Previous_DOW)

            Previous_Day = DAY
            Previous_Month = MONTH
            Previous_DOW = dow_value

    Rawdf['DAY OF WEEK'] = DAY_OF_WEEK

    print '...'


    BRONX=[10453, 10457, 10460, 10458, 10467, 10468, 10451, 10452, 10456, 10454, 10455, 10459, 
           10474, 10463, 10471, 10466, 10469, 10470, 10475, 10461, 10462,10464, 10465, 10472, 
           10473] 

    BROOKLYN=[11212, 11213, 11216, 11233, 11238, 11209, 11214, 11228, 11204, 11218, 11219, 
              11230, 11234, 11236, 11239,11223, 11224, 11229, 11235,11201, 11205, 11215, 
              11217, 11231,11203, 11210, 11225, 11226, 11207, 11208,11211, 11222, 11220, 
              11232, 11206, 11221, 11237] 

    MANHATTAN=[10026, 10027, 10030, 10037, 10039, 10001, 10011, 10018, 10019, 10020, 10036, 
               10029, 10035, 10010, 10016, 10017, 10022, 10012, 10013, 10014, 10004, 10005, 
               10006, 10007, 10038, 10280, 10002, 10003, 10009, 10021, 10028, 10044, 10128, 
               10023, 10024, 10025, 10031, 10032, 10033, 10034, 10040, 10178, 10279, '00083']

    QUEENS=[11361, 11362, 11363, 11364, 11354, 11355, 11356, 11357, 11358, 11359, 11360, 11365, 
            11366, 11367,11412, 11423, 11432, 11433, 11434, 11435, 11436, 11101, 11102, 11103, 
            11104, 11105, 11106, 11374, 11375, 11379, 11385, 11691, 11692, 11693, 11694, 11695, 
            11697, 11004, 11005, 11411, 11413, 11422, 11426, 11427, 11428, 11429, 11414, 11415, 
            11416, 11417, 11418, 11419, 11420, 11421, 11368, 11369, 11370, 11372, 11373, 11377, 
            11378]

    STATENISLAND=[10302, 10303, 10310, 10306, 10307, 10308, 10309, 10312, 10301, 10304, 
                  10305, 10314]

    Link1='https://maps.googleapis.com/maps/api/geocode/json?address='
    Link3 = '&key=AIzaSyD0nxCTgbmoDA-vyRKOjwduqi-XV2BpbF8'

    # creating a dictinary of boroughs to match each nyc zip code to a borough
    zip2borough = {}
    for borough in ["BRONX", "BROOKLYN", "MANHATTAN", "QUEENS", "STATENISLAND"]:
        for zipCode in eval(borough):
            zip2borough[str(zipCode)] = borough


    # finding which indices are valid for the following columns
    S1NN=Rawdf['ON STREET NAME'].notnull()
    S2NN=Rawdf['CROSS STREET NAME'].notnull()
    S3NN=Rawdf['OFF STREET NAME'].notnull()


    zipped_array = zip(Rawdf['ON STREET NAME'], Rawdf['CROSS STREET NAME'], 
                       Rawdf['OFF STREET NAME'], Rawdf['ZIP CODE'], S1NN, S2NN, S3NN, 
                       Rawdf['BOROUGH'])

    Rawdf['ZIP CODE'] = None
    Rawdf['BOROUGH'] = None
    NEW_ZIPS = []
    NEW_BOROUGHS = []
    OverLimit = 0

    for index,values in enumerate(zipped_array):  
        # valid zip code or 'Unknown' : Continue = 0
        # invalid zip code: Continue = 1
        Continue=0
        try:
            # valid zip code found
            try_me = int(float(values[3]))
            Continue = 0
        except:
            if str(values[3])=='Unknown':
                Continue = 0
            else:
                Continue = 1

        if (Continue == 0):
            if str(values[3])=='':
                Continue = 1

        # not over limit and no valid zip code
        if (Continue ==1) and (OverLimit == 0):
            print '-----------------'
            print ''.join(['working on ', str(index), ' of ', str(len(zipped_array))])
            Link2=''
            # street names present
            if True in [values[4], values[5], values[6]]:
                if values[4]==True:
                    Link2=values[0]
                    Link2=Link2.replace(' ','+')
                else:
                    Link2=''
                if values[5]==True:
                    if Link2=='':
                        Link2=values[1]
                        Link2=Link2.replace(' ','+')
                    else:
                        Link2=Link2+'+and+'+values[1]
                        Link2=Link2.replace(' ','+')
                else:
                    Link2=Link2+''
                if values[6]==True:
                    if Link2=='':
                        Link2=values[2]
                        Link2=Link2.replace(' ','+')
                    else:
                        Link2=Link2+'+and+'+values[2]
                        Link2=Link2.replace(' ','+')
                else:
                    Link2=Link2+''
                Link2='ny+'+Link2


                # go forward and call the google maps api only if cross streets were found
                successful = 0
                totalLink = Link1 + Link2 + Link3
                # call google maps api
                response = requests.get(totalLink) 
                if (response.text).find('OVER_QUERY_LIMIT')>0:
                    OverLimit = 1
                    print 'over query limit'

                if (response.text).count('ZERO_RESULTS') > 0:
                    # add ny+(ny)
                    Link2 = 'ny+' + Link2
                    totalLink = Link1 + Link2 + Link3
                    # call google maps api
                    print 'calling: ' + str(totalLink)
                    response = requests.get(totalLink)
                    if (response.text).count('ZERO_RESULTS') > 0:
                        pass
                    elif (response.text).find('OVER_QUERY_LIMIT')>0:
                        OverLimit = 1
                        print 'over query limit'
                        break
                    else:
                        successful = 1
                else:
                    successful = 1                    

                if successful == 1:
                    zipValue = None
                    boroughValue = None
                    for zipCode in BRONX:
                        FoundZip = (response.text).find(str(zipCode))
                        if FoundZip > 0:
                            boroughValue = 'BRONX'
                            zipValue = zipCode
                            break
                    if FoundZip == -1:
                        for zipCode in BROOKLYN:
                            FoundZip = (response.text).find(str(zipCode))
                            if FoundZip > 0:
                                boroughValue = 'BROOKLYN'
                                zipValue = zipCode
                                break
                    if FoundZip == -1:
                        for zipCode in MANHATTAN:
                            FoundZip = (response.text).find(str(zipCode))
                            if FoundZip > 0:
                                boroughValue = 'MANHATTAN'
                                zipValue = zipCode
                                break

                    if FoundZip == -1:
                        for zipCode in QUEENS:
                            FoundZip = (response.text).find(str(zipCode))
                            if FoundZip > 0:
                                boroughValue = 'QUEENS'
                                zipValue = zipCode
                                break

                    if FoundZip == -1:
                        for zipCode in STATENISLAND:
                            FoundZip = (response.text).find(str(zipCode))
                            if FoundZip > 0:
                                boroughValue = 'STATEN ISLAND'
                                zipValue = zipCode
                                break


                    if boroughValue!=None:
                        NEW_ZIPS.append(zipValue)
                        NEW_BOROUGHS.append(boroughValue)
                        print 'SUCCESS!!'
                        time.sleep(.3)
                        if index % 500 == 2:
                            print '...'
                    # can't find borough  
                    else:
                        NEW_ZIPS.append('Unknown')
                        NEW_BOROUGHS.append('Unknown')
                # if unsuccessful
                else:
                    NEW_ZIPS.append('Unknown')
                    NEW_BOROUGHS.append('Unknown')
            # no valid streets
            else:
                NEW_ZIPS.append('Unknown')
                NEW_BOROUGHS.append('Unknown')
        # no valid zip code found but overlimit
        elif (Continue == 1) and (OverLimit==1):
            NEW_ZIPS.append(values[3])
            NEW_BOROUGHS.append(values[7])

        # zip code exists
        elif Continue == 0:
            NEW_ZIPS.append(values[3])
            NEW_BOROUGHS.append(values[7])
        # do nothing
        elif OverLimit == 0:
            NEW_ZIPS.append(values[3])
            NEW_BOROUGHS.append(values[7])




    if OverLimit == 1:
        Rawdf['ZIP CODE'] = NEW_ZIPS
        Rawdf['BOROUGH'] = NEW_BOROUGHS
        print 'over limit -- trying second key'
        run_second_key = 1
    else:
        run_second_key = 0
        Rawdf['ZIP CODE'] = NEW_ZIPS
        Rawdf['BOROUGH'] = NEW_BOROUGHS



    if run_second_key == 1:

        # finding which indices are valid for the following columns
        S1NN=Rawdf['ON STREET NAME'].notnull()
        S2NN=Rawdf['CROSS STREET NAME'].notnull()
        S3NN=Rawdf['OFF STREET NAME'].notnull()


        zipped_array = zip(Rawdf['ON STREET NAME'], Rawdf['CROSS STREET NAME'], 
                           Rawdf['OFF STREET NAME'], Rawdf['ZIP CODE'], S1NN, S2NN, S3NN, 
                           Rawdf['BOROUGH'])

        Rawdf['BOROUGH'] = None
        NEW_ZIPS = []
        NEW_BOROUGHS = []
        OverLimit = 0
        # new key
        Link3='&key=AIzaSyDcnwSKtZ4LFOTT16pU8OW2I3YZKrRlA24'
        for index,values in enumerate(zipped_array):  
            # valid zip code or 'Unknown' : Continue = 0
            # invalid zip code: Continue = 1
            Continue=0
            try:
                # valid zip code found
                try_me = int(float(values[3]))
                Continue = 0
            except:
                if str(values[3])=='Unknown':
                    Continue = 0
                else:
                    Continue = 1

            if (Continue == 0):
                if str(values[3])=='':
                    Continue = 1

            # not over limit and no valid zip code
            if (Continue ==1) and (OverLimit == 0):
                print '-----------------'
                print ''.join(['working on ', str(index), ' of ', str(len(zipped_array))])
                Link2=''
                # street names present
                if True in [values[4], values[5], values[6]]:
                    if values[4]==True:
                        Link2=values[0]
                        Link2=Link2.replace(' ','+')
                    else:
                        Link2=''
                    if values[5]==True:
                        if Link2=='':
                            Link2=values[1]
                            Link2=Link2.replace(' ','+')
                        else:
                            Link2=Link2+'+and+'+values[1]
                            Link2=Link2.replace(' ','+')
                    else:
                        Link2=Link2+''
                    if values[6]==True:
                        if Link2=='':
                            Link2=values[2]
                            Link2=Link2.replace(' ','+')
                        else:
                            Link2=Link2+'+and+'+values[2]
                            Link2=Link2.replace(' ','+')
                    else:
                        Link2=Link2+''
                    Link2='ny+'+Link2


                    # go forward and call the google maps api only if cross streets were found
                    successful = 0
                    totalLink = Link1 + Link2 + Link3
                    # call google maps api
                    response = requests.get(totalLink) 
                    if (response.text).find('OVER_QUERY_LIMIT')>0:
                        OverLimit = 1
                        print 'over query limit'

                    if (response.text).count('ZERO_RESULTS') > 0:
                        # add ny+(ny)
                        Link2 = 'ny+' + Link2
                        totalLink = Link1 + Link2 + Link3
                        # call google maps api
                        print 'calling: ' + str(totalLink)
                        response = requests.get(totalLink)
                        if (response.text).count('ZERO_RESULTS') > 0:
                            pass
                        elif (response.text).find('OVER_QUERY_LIMIT')>0:
                            OverLimit = 1
                            print 'over query limit'
                            break
                        else:
                            successful = 1
                    else:
                        successful = 1                    

                    if successful == 1:
                        zipValue = None
                        boroughValue = None
                        for zipCode in BRONX:
                            FoundZip = (response.text).find(str(zipCode))
                            if FoundZip > 0:
                                boroughValue = 'BRONX'
                                zipValue = zipCode
                                break
                        if FoundZip == -1:
                            for zipCode in BROOKLYN:
                                FoundZip = (response.text).find(str(zipCode))
                                if FoundZip > 0:
                                    boroughValue = 'BROOKLYN'
                                    zipValue = zipCode
                                    break
                        if FoundZip == -1:
                            for zipCode in MANHATTAN:
                                FoundZip = (response.text).find(str(zipCode))
                                if FoundZip > 0:
                                    boroughValue = 'MANHATTAN'
                                    zipValue = zipCode
                                    break

                        if FoundZip == -1:
                            for zipCode in QUEENS:
                                FoundZip = (response.text).find(str(zipCode))
                                if FoundZip > 0:
                                    boroughValue = 'QUEENS'
                                    zipValue = zipCode
                                    break

                        if FoundZip == -1:
                            for zipCode in STATENISLAND:
                                FoundZip = (response.text).find(str(zipCode))
                                if FoundZip > 0:
                                    boroughValue = 'STATEN ISLAND'
                                    zipValue = zipCode
                                    break


                        if boroughValue!=None:
                            NEW_ZIPS.append(zipValue)
                            NEW_BOROUGHS.append(boroughValue)
                            print 'SUCCESS!!'
                            time.sleep(.3)
                            if index % 500 == 2:
                                print '...'
                        # can't find borough  
                        else:
                            NEW_ZIPS.append('Unknown')
                            NEW_BOROUGHS.append('Unknown')
                    # if unsuccessful
                    else:
                        NEW_ZIPS.append('Unknown')
                        NEW_BOROUGHS.append('Unknown')
                # no valid streets
                else:
                    NEW_ZIPS.append('Unknown')
                    NEW_BOROUGHS.append('Unknown')
            # no valid zip code found but overlimit
            elif (Continue == 1) and (OverLimit==1):
                NEW_ZIPS.append(values[3])
                NEW_BOROUGHS.append(values[7])

            # zip code exists
            elif Continue == 0:
                NEW_ZIPS.append(values[3])
                NEW_BOROUGHS.append(values[7])
            # do nothing
            elif OverLimit == 0:
                NEW_ZIPS.append(values[3])
                NEW_BOROUGHS.append(values[7])




        if OverLimit == 1:
            Rawdf['ZIP CODE'] = NEW_ZIPS
            Rawdf['BOROUGH'] = NEW_BOROUGHS
            print 'over limit again -- may need to be re-run'
        else:
            Rawdf['ZIP CODE'] = NEW_ZIPS
            Rawdf['BOROUGH'] = NEW_BOROUGHS


    print 'done using google maps api'
    
    # concatenating data
    frames = [data_all, Rawdf]
    data_all1 = pd.concat(frames)
    data_all = data_all1.reset_index(drop = True)
    print 'finished concatenating data'

    
    print 'saving all data'
    data_all = data_all.drop_duplicates(['UNIQUE KEY'])
    data_all = data_all.reset_index(drop = True)
    data_all.to_csv('/var/www/104.236.40.7/public_html/nyc/collisions/AllData.csv', index = False)
    print 'finished saving all data'

    # recalculating stats for month and all
    
    #month
    print 'processing month data'
    maxDate = pd.Timestamp(max(data_all['DATE']))
    MonthFilter = str(maxDate - timedelta(days=30))[0:10]
    
    data_month = data_all[data_all['DATE']>=MonthFilter]
    data_month = data_month.reset_index(drop = True)
    data_month = data_month.drop_duplicates(['UNIQUE KEY'])
    data_month = data_month.reset_index(drop = True)
    
    ZipStats_month = pd.DataFrame(zip(data_month['ZIP CODE'].value_counts().index,
                                      data_month['ZIP CODE'].value_counts().values))
    
    ZipStats_month.columns = ['zip','value']

    ZipStats_month = ZipStats_month[ZipStats_month['zip']!='Unknown']
    ZipStats_month = ZipStats_month.reset_index(drop = True)
    ZipStats_month.columns = ['zip','value']

    value_base = []


    for zip_base in ZipDataBase['zip']:
        zip_base = str(zip_base)
        found = 0
        for each_zip, each_value in zip(ZipStats_month['zip'], ZipStats_month['value']):
            each_zip = str(int(float(each_zip)))
            if each_zip == zip_base:
                found = 1
                value_base.append(each_value)
                break
        if found == 0:
            value_base.append(0)

    ZipDataBase['value'] = value_base        
    
    # outputting ZipData.csv for month
    ZipDataBase.to_csv('/var/www/104.236.40.7/public_html/nyc/collisions/month/ZipData.csv', index = False)


    # normalizing collisions by zip code land area
    value_base = []

    for zip_base,sqmiles in zip(ZipDataBase['zip'],ZipDataBase['sqmiles']):
        zip_base = str(zip_base)
        found = 0
        for each_zip, each_value in zip(ZipStats_month['zip'], ZipStats_month['value']):
            each_zip = str(int(float(each_zip)))
            if each_zip == zip_base:
                found = 1
                try:
                    value_base.append(round(float(each_value)/float(sqmiles),2))
                except:
                    value_base.append('N/A')
                break
        if found == 0:
            value_base.append('N/A')
            
    ZipDataBase['value'] = None
    ZipDataBase['value'] = value_base        
    # ZipDataBase['zip'] = ZipDataBase.zip.map("{:05}".format)

    ZipDataBase.to_csv('/var/www/104.236.40.7/public_html/nyc/collisions/month/ZipDataNormalized.csv', index = False)



    date_min_list_month = []
    date_max_list_month = []
    updatetime_list_month = []


    date_min_list_month.append(str(min(data_month['DATE']))[0:10])
    date_max_list_month.append(str(max(data_month['DATE']))[0:10])
    string_value_month = time.strftime('%l:%M%p ' + '(EST) ' + 'on %b %d, %Y')
    updatetime_list_month.append(string_value_month)




    print 'done processing month data'
    
    
    # all 
    print 'processing all data'


    maxDate = pd.Timestamp(max(data_all['DATE']))
    YearFilter = str(maxDate - timedelta(days=364))[0:10]
    
    data_all = data_all[data_all['DATE']>=YearFilter]
    data_all = data_all.reset_index(drop = True)
    data_all = data_all.drop_duplicates(['UNIQUE KEY'])
    data_all = data_all.reset_index(drop = True)
    


    ZipStats_all = pd.DataFrame(zip(data_all['ZIP CODE'].value_counts().index,
                                      data_all['ZIP CODE'].value_counts().values))
    
    ZipStats_all.columns = ['zip','value']

    ZipStats_all = ZipStats_all[ZipStats_all['zip']!='Unknown']
    ZipStats_all = ZipStats_all.reset_index(drop = True)
    ZipStats_all.columns = ['zip','value']

    value_base = []

    for zip_base in ZipDataBase['zip']:
        zip_base = str(zip_base)
        found = 0
        for each_zip, each_value in zip(ZipStats_all['zip'], ZipStats_all['value']):
            each_zip = str(int(float(each_zip)))
            if each_zip == zip_base:
                found = 1
                value_base.append(each_value)
                break
        if found == 0:
            value_base.append(0)

    ZipDataBase['value'] = value_base        
    # ZipDataBase['zip'] = ZipDataBase.zip.map("{:05}".format)

    # outputting ZipData.csv for all
    ZipDataBase.to_csv('/var/www/104.236.40.7/public_html/nyc/collisions/ZipData.csv', index = False)


    # normalizing collisions by zip code land area
    value_base = []

    for zip_base,sqmiles in zip(ZipDataBase['zip'],ZipDataBase['sqmiles']):
        zip_base = str(zip_base)
        found = 0
        for each_zip, each_value in zip(ZipStats_all['zip'], ZipStats_all['value']):
            each_zip = str(int(float(each_zip)))
            if each_zip == zip_base:
                found = 1
                try:
                    value_base.append(round(float(each_value)/float(sqmiles),2))
                except:
                    value_base.append('N/A')
                break
        if found == 0:
            value_base.append('N/A')
            
    ZipDataBase['value'] = None
    ZipDataBase['value'] = value_base        
    # ZipDataBase['zip'] = ZipDataBase.zip.map("{:05}".format)

    ZipDataBase.to_csv('/var/www/104.236.40.7/public_html/nyc/collisions/ZipDataNormalized.csv', index = False)






    date_min_list_all = []
    date_max_list_all = []
    updatetime_list_all = []

    date_min_list_all.append(str(min(data_all['DATE']))[0:10])
    date_max_list_all.append(str(max(data_all['DATE']))[0:10])
    string_value_all = time.strftime('%l:%M%p ' + '(EST) ' + 'on %b %d, %Y')
    updatetime_list_all.append(string_value_all)


    dateDF = pd.DataFrame(zip(date_min_list_latest, date_max_list_latest, updatetime_list_latest, 
                              date_min_list_month, date_max_list_month, updatetime_list_month,
                              date_min_list_all, date_max_list_all, updatetime_list_all))

    dateDF.columns = ['mindate_latest','maxdate_latest','updatetime_latest', 
                      'mindate_month','maxdate_month','updatetime_month',
                      'mindate_all','maxdate_all','updatetime_all']

    dateDF.to_csv('/var/www/104.236.40.7/public_html/nyc/collisions/latest/displaydates.csv', index = False)
    dateDF.to_csv('/var/www/104.236.40.7/public_html/nyc/collisions/displaydates.csv', index = False)
    dateDF.to_csv('/var/www/104.236.40.7/public_html/nyc/collisions/month/displaydates.csv', index = False)
    

    print 'done processing all data'
    print 'made it to the bitter end!'

    
else:

    

    date_min_list_month = []
    date_min_list_month.append(None)
    date_max_list_month = []
    date_max_list_month.append(None)
    updatetime_list_month = []
    updatetime_list_month.append(None)


    date_min_list_all = []
    date_min_list_all.append(None)
    date_max_list_all = []
    date_max_list_all.append(None)
    updatetime_list_all = []
    updatetime_list_all.append(None)

    dateDF = pd.DataFrame(zip(date_min_list_latest, date_max_list_latest, updatetime_list_latest, 
        date_min_list_month, date_max_list_month, updatetime_list_month,
        date_min_list_all, date_max_list_all, updatetime_list_all))

    dateDF.columns = ['mindate_latest','maxdate_latest','updatetime_latest', 
    'mindate_month','maxdate_month','updatetime_month','mindate_all','maxdate_all','updatetimetime_all']

    dateDF.to_csv('/var/www/104.236.40.7/public_html/nyc/collisions/latest/displaydates.csv', index = False)

    print 'already up to date'
