import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

## scrap teams for each season
seasons = list(range(2015, 2025))
records = []

for s in seasons:
    url = f'https://www.basketball-reference.com/leagues/NBA_{s}.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    time.sleep(3.5)

    rows = soup.find('table', id='per_game-team').find('tbody').find_all('tr')
    for row in rows:
        team = row.find('td').find('a').get_text()
        team_abb = row.find('td').find('a').get('href').split('/')[-2]
        records.append([s, team, team_abb])
    print(f'{s} done')

team_df = pd.DataFrame(records, columns=['Season', 'Team', 'Team Abb'])
team_df.to_csv('Files/Team Abbreviations.txt', sep='|')


## scrap boxscore links
records = []

for idx, r in team_df.iterrows():
    s = r['Season']
    t = r['Team Abb']
    url = f'https://www.basketball-reference.com/teams/{t}/{s}_games.html'
    r = requests.get(url)
    time.sleep(3.5)

    soup = BeautifulSoup(r.content, 'html.parser')
    rows = [x for x in soup.find('table', id='games').find('tbody').find_all('tr') if x.get('class') == None]
    for row in rows:
        td = row.find_all('td')[3].find('a').get('href')
        if td not in records:
            records.append(td)
    
    print(f'Boxscore Link {idx + 1} of {team_df.shape[0]} done.')

games_list = pd.DataFrame(records, columns=['Game URL'])
games_list['Game URL'] = 'https://www.basketball-reference.com' + df['Game URL']

games_list.to_csv('Files/Games List.txt', sep='|')


## scrap game data
records = []
i = 1
qtr = 'q1'  ## adjust this to q2, q3, h1, etc.

for game in games_list['Game URL'].values:
    r = requests.get(game)
    time.sleep(3.5)

    soup = BeautifulSoup(r.content, 'html.parser')
    teams = soup.find('div', class_='scorebox').find_all('strong')
    team_0 = teams[0].find('a').get_text()
    team_1 = teams[1].find('a').get_text()

    table_soups = []

    for t in soup.find_all('table'):
        id = t.get('id')
        if id:
            if qtr in id:  
                table_soups.append(t)

    team_0_stats = [x.get_text() for x in table_soups[0].find('tfoot').find_all('td', class_='right')[1:-2]]
    team_0_stats.insert(0, team_0)
    team_1_stats = [x.get_text() for x in table_soups[1].find('tfoot').find_all('td', class_='right')[1:-2]]
    team_1_stats.insert(0, team_1)
    stats = team_0_stats + team_1_stats

    records.append(stats)
    print(f'Game {i} of {games_list.shape[0]} complete.')
    i += 1

stats_df = pd.DataFrame(records, columns=['Team 0', 'FG_0', 'FGA_0', 
                                          'FG%_0', '3P_0', '3PA_0', 
                                          '3P%_0', 'FT_0', 'FTA_0', 
                                          'FT%_0', 'ORB_0', 'DRB_0', 
                                          'TRB_0', 'AST_0', 'STL_0', 
                                          'BLK_0', 'TOV_0', 'PF_0', 
                                          'PTS_0', 'Team 1', 'FG_1', 
                                          'FGA_1', 'FG%_1', '3P_1', 
                                          '3PA_1', '3P%_1', 'FT_1', 
                                          'FTA_1', 'FT%_1', 'ORB_1', 
                                          'DRB_1', 'TRB_1', 'AST_1', 
                                          'STL_1', 'BLK_1', 'TOV_1', 
                                          'PF_1', 'PTS_1'])
stats_df.replace('', 0, inplace=True)
stats_df['Game'] = games_list['Game URL'].values
stats_df.to_csv(f'{qtr} results.txt', sep='|')
