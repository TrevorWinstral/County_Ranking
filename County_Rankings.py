#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np

df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')
df.columns = ['Date', 'County', 'State', 'Fips', 'Cases', 'Deaths']
df = df.sort_values(by=['State', 'County'])
print(df.tail())


fips = df['Fips'].unique()

#Create a Table for each Region
#Regions
ne_data = {'New England':['Maine', 'New Hampshire', 'Vermont', 'Massachusetts', 'Rhode Island', 'Connecticut']}
ma_data = {'Middle Atlantic':['New York', 'New Jersey','Pennsylvania']}
en_data = {'East North Central':['Ohio', 'Michigan', 'Indiana', 'Wisconsin', 'Illinois']}
wn_data = {'West North Central':['Minnesota', 'Iowa', 'Missouri', 'North Dakota', 'South Dakota', 'Nebraska', 'Kansas']}
sa_data = {'South Atlantic':['Delaware', 'Maryland', 'West Virginia', 'Virginia', 'North Carolina', 'South Carolina', 'Georgia', 'Florida', 'Puerto Rico', 'District of Columbia']}
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


for fip in fips:
    #fip=56041
    frame = df[df['Fips']==fip].drop('Fips', axis = 1).reset_index()
    try:
        county = frame.iloc[0]['County']
        state = frame.iloc[0]['State']
    except:
        continue
        
    print(f'Working on {county}, {state}')
    frame.loc[:,'New']=frame.loc[:,'Cases'].diff()    
    frame['New'] = frame['New'].fillna(0.0)
    frame.loc[:,'Total New Cases in Last 14 Days']=frame.loc[:,'New'].rolling(14, min_periods=1).sum()
    
    #Calculate Streak
    
    fd = frame.copy().reset_index().drop(['Total New Cases in Last 14 Days', 'State', 'Deaths', 'Date'], axis=1)

    fd['sign'] = fd['New'].le(0).astype(int)*2 -1
    fd['s'] = fd['sign'].groupby((fd.sign!=fd.sign.shift()).cumsum()).cumsum()
    checker = lambda x : max(x,0)
    fd['Free_Streak'] = fd['s'].map(checker)
    fd = fd.drop(['sign', 's'], axis=1)
    frame['Free Streak']=fd['Free_Streak']
    frame = frame.drop(['index'], axis=1)[['Date', 'State', 'County', 'Cases', 'New', 'Total New Cases in Last 14 Days', 'Free Streak', 'Deaths']]
    
    if frame.iloc[-1]['Total New Cases in Last 14 Days'] == np.float64(np.NaN):
        continue
    
    _region = reverse_region[state]
    new_row = {'County':f'{county}, {in_abbrev[state]}', 'COVID-Free Days':frame.iloc[-1]['Free Streak'], 'New Cases in Last 14 Days':frame.iloc[-1]['Total New Cases in Last 14 Days']}
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
    new_row = {'County':f'{county}, {state}', 'COVID-Free Days':delta, 'New Cases in Last 14 Days':0}
    print(new_row)
    Regions[_region]=Regions[_region].append(new_row, ignore_index=True)




def highlighter(s):
    val_1 = s['COVID-Free Days']
    val_2 = s['New Cases in Last 14 Days']
    r=''
    try:
        if val_1>=14:
            r = 'background-color: #018001;'
        elif 20>=val_2 :
            r = 'background-color: #02be02;'
        elif 200>=val_2 >=21:
            r = 'background-color: #ffff01;'
        elif 1000>=val_2 >= 201:
            r = 'background-color: #ffa501;'
        elif 20000>=val_2 >= 1001:
            r = 'background-color: #ff3434;'
        elif val_2 > 20001:
            r = 'background-color: #990033;'
    except Exception as e:
        r = 'background-color: white'
    return [r]*len(s)

def hover(hover_color="#ffff99"):
    return dict(selector="tbody tr:hover td, tbody tr:hover th",
                props=[("background-color", "rgba(66, 165, 245, 0.2) !important")])

top = """

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


# In[20]:


styles=[hover(),]
for region in Regions:
    try:
        print(region)
        #Fix NaN and sort
        Regions[region] = Regions[region].dropna(subset=['New Cases in Last 14 Days']).astype({"COVID-Free Days": int, "New Cases in Last 14 Days": int})
        fix_new_cases = lambda x : max(x, 0)
        Regions[region]['New Cases in Last 14 Days'] = Regions[region]['New Cases in Last 14 Days'].map(fix_new_cases)
        temp = Regions[region].sort_values(by=['New Cases in Last 14 Days', 'COVID-Free Days'], ascending=[True, False])
        #temp = Regions[region].sort_values(by=['COVID-Free Days', 'New Cases in Last 14 Days'], ascending=[False, True])
        
        #Add rank
        temp['Rank'] = temp.reset_index().index
        temp['Rank'] = temp['Rank'].add(1)
        temp = temp[['Rank', 'County', 'COVID-Free Days', 'New Cases in Last 14 Days']]
        
        s = temp.style.apply(highlighter, axis = 1).set_table_styles(styles).hide_index()
        
        with open(f'{region.replace(" ", "_")}.html', 'w') as out:
            content = top + s.render() + bottom
            out.write(content)
    except Exception as e:
        print(f'Error:\n{e}')
