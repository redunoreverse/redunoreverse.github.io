#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime

api = 'http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard'

teams = ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
url_template = 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/{}.png&h=200&w=200'
team_urls = {team: url_template.format(team.lower()) for team in teams}

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

# Webpage Stuff    
html_tables = []

# Loop through each dataframe and create HTML tables with logo
for i, (name, df) in enumerate(dfs.items()):
    team_names = name.split(' vs ')
    # Get the team logo URL
    logo_url0 = team_urls.get(team_names[0], None)
    logo_url1 = team_urls.get(team_names[1], None)

    # If the logo exists, add it to the table HTML code
    if logo_url0 and logo_url1:
        logo_html0 = f'<img src="{logo_url0}" alt="{team_names[0]} logo" width="90">'
        logo_html1 = f'<img src="{logo_url1}" alt="{team_names[1]} logo" width="90">'
    else:
        logo_html0 = ''
        logo_html1 = ''
    
    # Create the HTML table
    table_html = f'''
    <div class="table">
        <h3>{name}</h3>
        <div class="logos">
            {logo_html0}
            {logo_html1}
        </div>
        {df.to_html(classes='data')}
    </div>
    '''
    
    html_tables.append(table_html)

# Combine all HTML tables into a single string
all_tables = ''.join(html_tables)

# Create HTML header with title and images
# Create HTML header with title and images
html_header = f'''
<!DOCTYPE html>
<html>
<head>
<style>
body {{
    background-image: url("https://advancedhoops.com/wp-content/uploads/2021/08/Basketball-Court-Wood-Background-7267-Best-Wallpapers-Basketball-Court.jpg");
    color: white;
    font-family: Helvetica;
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
table {{
    margin-right: 15px;
}}
.table-container {{
    margin-top: 20px;
    text-align: center;
}}
.table-row {{
    display: flex;
    justify-content: center;
}}
</style>
</head>
<body>
<div class="container" style="margin: 0 auto;">
    <h1>NBA Scoreboard</h1>
    <img src="https://cdn.freebiesupply.com/images/large/2x/nba-logo-transparent.png" alt="NBA Logo" height="400" style="display: block; margin: 0 auto;">
    <h2>Boxscores</h2>
    <div class="table-row">
        {html_tables[0]}
        {html_tables[1]}
    </div>
    <div class="table-row">
        {html_tables[2]}
        {html_tables[3]}
    </div>
    <br>
    <p class="last-updated">Last updated: {datetime.datetime.now()}</p>
    <img src="https://cdn.freebiesupply.com/images/large/2x/espn-logo-transparent.png" alt="ESPN" width="325" style="display: block; margin: 0 auto; margin-center: 0px;">
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
with open('index1.html', 'w') as f:
    f.write(all_html)
    f.close()

