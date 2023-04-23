#!/usr/bin/env python
# coding: utf-8

# In[4]:


import requests
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime

api = 'http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard'

jsonData = requests.get(api).json()
events = jsonData['events']

links = []
for event in events:
    event_links = event['links']
    for each in event_links:
        if each['text'] == 'Box Score':
            links.append(each['href'])
            
dfs = {}
for link in links:
    url = link

    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('table')

    # Get the column headers
    headers = []
    for header in table.find_all('th'):
        headers.append(header.text)

    # Get the data rows
    rows = []
    for row in table.find_all('tr'):
        row_data = []
        for cell in row.find_all('td'):
            row_data.append(cell.text)
        if row_data:
            rows.append(row_data)

    # Create the DataFrame
    df = pd.DataFrame(rows, columns=["Team", "Q1", "Q2", "Q3", "Q4", "Total"])
    dfs[df["Team"][0] + " vs " + df["Team"][1]] = df

# Webpage Stuff Below    
    
# Create an empty list to store HTML tables
html_tables = []

# Loop through each dataframe and create HTML tables
for name, df in dfs.items():
    html_table = df.to_html(classes='data')
    html_tables.append(html_table)

# Combine all HTML tables into a single string
all_tables = ''.join(html_tables)

# Create HTML header with title and images
html_header = f'''
<!DOCTYPE html>
<html>
<head>
<style>
    body {{
        background-image: url("https://advancedhoops.com/wp-content/uploads/2021/08/Basketball-Court-Wood-Background-7267-Best-Wallpapers-Basketball-Court.jpg");
        color: white; /* change the font color to white */
        font-family: Helvetica
    }}
    .container {{
        width: 80%;
        margin: 0 auto;
        text-align: center;
    }}
    h1 {{
        margin-top: 50px;
    }}
    .logo {{
        display: block;
        margin: 0 auto;
        width: 200px;
        height: auto;
    }}
    .table-container {{
        margin-top: 20px;
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        grid-gap: 20px;
    }}
</style>
</head>
<body>
<div class="container">
    <h1>NBA Scoreboard</h1>
    <img src="https://cdn.freebiesupply.com/images/large/2x/nba-logo-transparent.png" alt="NBA Logo" class="logo">
    <h2>Boxscores</h2>
    <div class="table-container">
        {all_tables}
    </div>
    <br>
    <p class="last-updated">Last updated: {datetime.datetime.now()}</p>
    <img src="https://cdn.freebiesupply.com/images/large/2x/espn-logo-transparent.png" alt="ESPN" width="500">
</div>
'''

# Create HTML footer to close the document
html_footer = '''
</body>
</html>
'''

# Combine the header, tables, and footer into a single string
all_html = html_header + html_footer

# Save combined HTML tables into a new file
with open('index.html', 'w') as f:
    f.write(all_html)
    f.close()

