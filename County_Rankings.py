#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np

df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')
df.columns = ['Date', 'County', 'State', 'Fips', 'Cases', 'Deaths']
df = df.sort_values(by=['State', 'County'])
print(df.tail())

#Assigning Fips to New York City, NY, Kansas City, MO and Joplin, MO
df.loc[df['County'] == 'New York City', 'Fips'] = 999
df.loc[df['County'] == 'Kansas City', 'Fips'] = 998
df.loc[df['County'] == 'Joplin', 'Fips'] = 997

fips = df['Fips'].unique()

#Create a Table for each Region
#Regions
ne_data = {'New England':['Maine', 'New Hampshire', 'Vermont', 'Massachusetts', 'Rhode Island', 'Connecticut']}
ma_data = {'Middle Atlantic':['New York', 'New Jersey','Pennsylvania']}
en_data = {'East North Central':['Ohio', 'Michigan', 'Indiana', 'Wisconsin', 'Illinois']}
wn_data = {'West North Central':['Minnesota', 'Iowa', 'Missouri', 'North Dakota', 'South Dakota', 'Nebraska', 'Kansas']}
sa_data = {'South Atlantic':['Delaware', 'Maryland', 'West Virginia', 'Virginia', 'North Carolina', 'South Carolina', 'Georgia', 'Florida', 'Puerto Rico', 'District of Columbia', 'Virgin Islands', 'Northern Mariana Islands']}
es_data = {'East South Central':['Kentucky', 'Tennessee', 'Alabama', 'Mississippi']}
ws_data = {'West South Central':['Arkansas', 'Louisiana', 'Oklahoma', 'Texas']}
mo_data = {'Mountain':['Montana', 'Idaho', 'Wyoming', 'Colorado', 'New Mexico', 'Arizona', 'Utah', 'Nevada']}
pa_data = {'Pacific':['California', 'Oregon', 'Washington', 'Alaska', 'Hawaii']}


table = pd.DataFrame({'County':[], 'COVID-Free Days':[], 'New Cases in Last 14 Days':[]})
Regions = [ne_data, ma_data, en_data, wn_data, sa_data, es_data, ws_data, mo_data, pa_data]

reverse_region = {} #State to region
regions = {} #Region to list of states
#For Some reason I couldn't get list comprehension to work
for region_dict in Regions:
    for region in region_dict:
        regions[region]=region_dict[region]
        for state in region_dict[region]:
            reverse_region[state] = region
Regions = {region_name:table.copy() for region_name in regions}


abbrev = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

in_abbrev = {v: k for k, v in abbrev.items()}

fix_new_cases = lambda x : max(x, 0)
for fip in fips:
    #fip=56041
    frame = df[df['Fips']==fip].drop('Fips', axis = 1).reset_index()
    try:
        county = frame.iloc[0]['County']
        state = frame.iloc[0]['State']
    except:
        continue
        
    print(f'Working on {county}, {state}')
    # Get New cases, fix NaN, and then set negative days to 0
    frame.loc[:,'New']=frame.loc[:,'Cases'].diff()   
    frame['New'] = frame['New'].fillna('X') 
    indices = np.where(frame['New']=='X')
    frame.loc[indices[0],'New'] = frame.loc[indices[0], 'Cases']
    #frame['New'] = frame['New'].map(fix_new_cases)
    #frame.loc[:,'Total New Cases in Last 14 Days']=frame.loc[:,'New'].rolling(14, min_periods=1).sum()
    #frame['Total New Cases in Last 14 Days'] = frame['Total New Cases in Last 14 Days'].map(fix_new_cases)
    
    frame.loc[:,'Total New Cases in Last 14 Days']=frame.loc[:,'New'].rolling(14, min_periods=1).sum()

    #Percent Change
    frame['Last7'] = frame['New'].rolling(7, min_periods=1).sum().map(fix_new_cases)
    # Set Last 14 days entries to last 7 days if latter is larger
    frame.loc[(frame['Last7'] > frame['Total New Cases in Last 14 Days']), 'Total New Cases in Last 14 Days'] = frame.loc[(frame['Last7'] > frame['Total New Cases in Last 14 Days']), 'Last7']
    frame['Previous7'] = frame['Last7'].shift(7).fillna(0.0).map(fix_new_cases)
    # Set previous 7 days to zero if last7 and last 14 are zero
    frame.loc[(frame['Last7'] == 0) & (frame['Total New Cases in Last 14 Days'] == 0), 'Previous7'] = 0
    frame['PercentChange'] = 100*(frame['Last7'] - frame['Previous7'])/(frame['Last7']+frame['Previous7'])
    frame['PercentChange'] = frame['PercentChange'].fillna(0.0)

    #Calculate Streak
    fd = frame.copy().reset_index().drop(['Total New Cases in Last 14 Days', 'State', 'Deaths', 'Date'], axis=1)

    fd['sign'] = fd['New'].le(0).astype(int)*2 -1
    fd['s'] = fd['sign'].groupby((fd.sign!=fd.sign.shift()).cumsum()).cumsum()
    checker = lambda x : max(x,0)
    fd['Free_Streak'] = fd['s'].map(checker)
    fd = fd.drop(['sign', 's'], axis=1)
    frame['Free Streak']=fd['Free_Streak']
    frame = frame.drop(['index'], axis=1)[['Date', 'State', 'County', 'Cases', 'New', 'Total New Cases in Last 14 Days', 'Free Streak', 'Deaths', 'Last7', 'PercentChange']]
    
    
    _region = reverse_region[state]
    new_row = {'County':f'{county}, {in_abbrev[state]}', 'COVID-Free Days':frame.iloc[-1]['Free Streak'], 'New Cases in Last 14 Days':frame.iloc[-1]['Total New Cases in Last 14 Days'], 'Last 7 Days':frame.iloc[-1]['Last7'], 'Pct Change':frame.iloc[-1]['PercentChange']}
    Regions[_region]=Regions[_region].append(new_row, ignore_index=True)


from datetime import date, datetime
d0 = date(2020, 1, 20)
now = datetime.now()
d1= date(now.year, now.month, now.day)
delta = d1 - d0
delta = delta.days

ze = pd.read_csv('zero.csv')
for index, row in ze.iterrows():
    state = row.state
    county = row.county
    _region = reverse_region[abbrev[state]]
    new_row = {'County':f'{county}, {state}', 'COVID-Free Days':delta, 'New Cases in Last 14 Days':0, 'Last 7 Days':0, 'Pct Change':0.0}
    print(new_row)
    Regions[_region]=Regions[_region].append(new_row, ignore_index=True)




def highlighter(s):
    val_1 = s['COVID-Free Days']
    val_2 = s['New Cases in Last 14 Days']
    
    r=''
    try:
        if val_1>=14: #More than 14 Covid free days
            r = 'background-color: #018001; color: #ffffff;'
        elif 20>=val_2 : # less than 20 in last 2 weeks
            r = 'background-color: #02be02; color: #ffffff;'
        elif 200>=val_2 >=21: #Light green
            r = 'background-color: #ffff01;'
        elif 1000>=val_2 >= 201: #Yellow
            r = 'background-color: #ffa501;'
        elif 20000>=val_2 >= 1001: #Orange
            r = 'background-color: #ff3434;'
        elif val_2 > 20001: # Red
            r = 'background-color: #990033;'
    except Exception as e:
        r = 'background-color: white'
    return [r]*(len(s)-2) + ['']*2

def hover(hover_color="#ffff99"):
    return dict(selector="tbody tr:hover td, tbody tr:hover th",
                props=[("background-color", "rgba(66, 165, 245, 0.2) !important")])

top = """
<!DOCTYPE html>
<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<meta content="utf-8" http-equiv="encoding">
<html>
<head>
<style>

    h2 {
        text-align: center;
        font-family: Helvetica, Arial, sans-serif;
    }
    table { 
        margin-left: auto;
        margin-right: auto;
    }
    table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
    }
    th, td {
        padding: 5px;
        text-align: center;
        font-family: Helvetica, Arial, sans-serif;
        font-size: 90%;
    }
    table tbody tr:hover {
        background-color: #dddddd;
    }
    /*
    table tbody tr:hover td, table tbody tr:hover th {
  background-color: #dddddd !important;
    }
    /*
    .wide {
        width: 90%; 
    }

</style>
</head>
<body>
"""
bottom = """
</body>
</html>
"""


styles=[hover(),]
for region in Regions:
    arrow = lambda x : ' &#x2197;' if x>0 else (' &#x2192' if x ==0  else ' &#x2198') # set arrow direction, ...97 is up, 92 straight, 98 down
    try:
        print(region)
        #Fix NaN and sort
        Regions[region] = Regions[region].dropna(subset=['New Cases in Last 14 Days']).astype({"COVID-Free Days": int, "New Cases in Last 14 Days": int, "Last 7 Days": int, 'Pct Change': float})

        Regions[region]['Trend'] = Regions[region]['Pct Change'].map(arrow)
        #Regions[region]['Pct Change'] = Regions[region]['Pct Change'].map('{:,.2f}%'.format) 
        Regions[region]['Percent Change'] = Regions[region]['Pct Change'].map('{:,.2f}%'.format) + Regions[region]['Trend']

        Regions[region]['New Cases in Last 14 Days'] = Regions[region]['New Cases in Last 14 Days'].map(fix_new_cases)
        temp = Regions[region].sort_values(by=['New Cases in Last 14 Days', 'COVID-Free Days'], ascending=[True, False])
        #temp = Regions[region].sort_values(by=['COVID-Free Days', 'New Cases in Last 14 Days'], ascending=[False, True])
        
        #Add rank
        temp['Rank'] = temp.reset_index().index
        temp['Rank'] = temp['Rank'].add(1)
        temp = temp[['Rank', 'County', 'COVID-Free Days', 'New Cases in Last 14 Days', 'Last 7 Days', 'Percent Change']]
        
        s = temp.style.apply(highlighter, axis = 1).set_table_styles(styles).hide_index()

        with open(f'{region.replace(" ", "_")}.html', 'w') as out:
            body = s.render().replace('&#x2197;','<span style="color: red"> &#x2197;</span>') # red arrow up
            body = body.replace('&#x2198','<span style="color: green"> &#x2198;</span>') # green arrow down
            content = top + body + bottom
            out.write(content)
    except Exception as e:
        print(f'Error:\n{e}')
