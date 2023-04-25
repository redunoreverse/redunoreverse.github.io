#!/usr/bin/env python
# coding: utf-8
# %%
import requests
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime

api = 'http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard'

teams = ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GS', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NY', 'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
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
    if 'OT' in headers:
        df = pd.DataFrame(rows, columns=["Team", "Q1", "Q2", "Q3", "Q4", "OT", "Total"])
        dfs[df["Team"][0] + " vs " + df["Team"][1]] = df
    elif ('OT1' and 'OT2') in headers:
        df = pd.DataFrame(rows, columns=["Team", "Q1", "Q2", "Q3", "Q4", "OT1", "OT2", "Total"])
        dfs[df["Team"][0] + " vs " + df["Team"][1]] = df
    else:
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
'''

# Add the tables to the HTML header
table_count = len(html_tables)
if table_count == 1:
    all_html = html_header + f'<div class="table-row">{html_tables[0]}</div>'
else:
    table_row_html = ''.join([f'<div class="table">{table_html}</div>' for table_html in html_tables])
    all_html = html_header + f'<div class="table-row">{table_row_html}</div>'

# Add the last updated time and footer to the HTML
all_html += f'<br><p class="last-updated">Last updated: {datetime.datetime.now()}</p>'
all_html += '<img src="https://cdn.freebiesupply.com/images/large/2x/espn-logo-transparent.png" alt="ESPN" width="325" style="display: block; margin: 0 auto; margin-center: 0px;"></div></body></html>'

# Save combined HTML tables into a new file
with open('index.html', 'w') as f:
    f.write(all_html)
    f.close()

