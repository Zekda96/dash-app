# libraries
import numpy as np
import pandas as pd
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import flag

country = 'ECUADOR'

# fbref table link
url = 'https://fbref.com/es/stathead/scout/ECU'

results = pd.read_html(url)[0]  # Player stats

# Selenium for fixtures

driver = webdriver.Firefox(options=Options())
driver.get(url)

# Get column names
thead = driver.find_element(By.XPATH, '//*[@id="fixtures_players"]/thead')
header = thead.find_elements(By.XPATH, './/tr')
cols = header[0].text.split()

# Get rows
tbody = driver.find_element(By.XPATH, '//*[@id="fixtures_players"]/tbody')
data = []

# Iterate rows and get items
for tr in tbody.find_elements(By.XPATH, './/tr'):
    row = [item.text for item in tr.find_elements(By.XPATH, './/td')]
    row.insert(0, tr.find_elements(By.XPATH, './/th')[0].text)
    data.append(row)
# Create dataframe with future fixtures
fixtures = pd.DataFrame(data=data, columns=cols)

# Format date
fixtures_date = fixtures.Fecha.str.split(',', expand=True)
fixtures.loc[:, 'Fecha'] = fixtures_date[0]
# Clean date
fixtures = fixtures[fixtures['Fecha'] != 'Fecha']

# Format time
fixtures_time = fixtures.Hora.str.split('(', expand=True)
for i, row in fixtures_time.iterrows():
    if row[1] is not None:
        fixtures_time.loc[i, :] = row[1][:-1]

fixtures.loc[:, 'Hora'] = fixtures_time[0]

# Replace Mediocentro with CC
fixtures.loc[:, 'Posc'] = fixtures.Posc.replace(to_replace='CC', value='MC')
fixtures.loc[:, 'Posc'] = fixtures.Posc.replace(to_replace='DF,CC', value='DF/MC')
fixtures.loc[:, 'Posc'] = fixtures.Posc.replace(to_replace='DL,CC', value='DL/MC')

fixtures.loc[:, 'Jugador'] = fixtures.Jugador.replace(to_replace='Félix Torres Caicedo', value='Félix Torres')


# Get today's date
today = date.today()
# Standardize two digit months (01, 02, ... 10, 11, 12)
if today.month < 10:
    mes = f'0{today.month}'
else:
    mes = f'{today.month}'

if today.day < 10:
    dia = f'0{today.day}'
else:
    dia = f'{today.day}'

hoy = f'{today.year}-{mes}-{dia}' # Today's date in dataframe's format


fixtures_today = fixtures[fixtures['Fecha'] == hoy]
fixtures_today = fixtures_today.sort_values(by='Hora')
fixtures_today = fixtures_today.reset_index(drop=True)
ec = flag.flag('EC')

tweet = [f'🇪🇨🇪🇨⚽⚽ #EcuatorianosEnElExterior que juegan hoy:\n\n']
for i, row in fixtures_today.iterrows():
    fecha = row['Fecha']
    player = row['Jugador']
    hora = row['Hora']
    edad = row['Edad'][:2]
    equipo = row['Equipo']
    rival = row['Adversario']
    pais = row['País']
    posc = row['Posc']

    if pais[:3] == 'eng':
        p_flag = '🏴󠁧󠁢󠁥󠁮󠁧󠁿'
    else:
        p_flag = flag.flag(f'{pais[:2]}')

    if np.remainder(i+1, 4) == 0:
        tweet.append('-'*45 + '\n\n')
    tweet.append(f'{player} ({edad} - {posc}) - [{p_flag}{pais[-3:]}] {equipo} vs {rival} - {hora}\n\n')

tweet = ''.join(tweet)
print(tweet)

with open('fixtures.txt', 'w') as f:
    f.write(tweet)

# ------------------------- ADD CUP SCHEDULES
url_c1 = 'https://fbref.com/es/comps/8/nacionalidades/Nacionalidades-en-Champions-League'
url_c2 = 'https://fbref.com/es/comps/19/nacionalidades/Nacionalidades-en-Europa-League'
url_c3 = 'https://fbref.com/es/comps/882/nacionalidades/Nacionalidades-en-Europa-Conference-League'
competitions = [{'name': 'Champions Lg', 'url': url_c1},
                {'name': 'Europa Lg',    'url': url_c2},
                {'name': 'Conf Lg', 'url': url_c3}
                ]


cups = []
for cup in competitions:
    driver.get(cup['url'])
    # Get column names
    thead = driver.find_element(By.XPATH, '//*[@id="nations"]/thead')
    header = thead.find_element(By.XPATH, './/tr')
    # Split header
    cols = header.text.split()
    # Fix column name as it is split into separate columns
    idx = cols.index('N.°')
    cols[idx] = 'N.° de Jugadores'
    del cols[idx+1:idx+3]  # Delete the previous separate columns

    # Get rows from cup nationalities table
    tbody = driver.find_element(By.XPATH, '//*[@id="nations"]/tbody')

    # Iterate rows and find Ecuador row
    for tr in tbody.find_elements(By.XPATH, './/tr'):
        if tr.text.split()[2] == country.capitalize():
            country_players = []
            country_url = []
            print(f'\nHoy juegan por {cup["name"]}:')
            # Iterate through ecuadorean players and get their profile url
            for player in tr.find_elements(By.XPATH, './/td[4]/a'):
                name = player.text
                player_url = player.get_attribute('href')

                print(f'{name}')
                country_players.append(name)
                country_url.append(player_url)

    # Iterate through players profile url to get their teams profile url
    teams_url = []
    team_name = []
    for url in country_url:
        driver.get(url)
        for p in driver.find_elements(By.XPATH, '//*[@id="meta"]/div/p'):
            for strong in p.find_elements(By.XPATH, './/strong'):

                # Get club name and club profile URL
                if strong.text == 'Club :':
                    a = p.find_element(By.XPATH, './/a')
                    team_url = a.get_attribute('href')
                    team_name.append(a.text)
                    teams_url.append(team_url)
                    print(f'{cup["name"]} urls: {team_url}')
                    # teams_url.append(p.find_element(By.XPATH, './/a').get_attribute('href'))

    cup_data = []
    team_data = []
    # Iterate through teams profiles to check if they play cup today
    for i, url in enumerate(teams_url):
        driver.get(url)
        # Iter rows and check date and comp
        for tr in driver.find_elements(By.XPATH, '//*[@id="matchlogs_for"]/tbody/tr[not(contains(@class, "thead rowSum"))]'):
            # If is not a header row
            if tr.text.split()[0] != 'Fecha':
                # Check if team plays today
                is_today = tr.find_element(By.XPATH, './/th').text == hoy
                is_cup = tr.find_element(By.XPATH, './/td[2]').text == cup['name']
                if is_today and is_cup:
                    print(f'{cup["name"]}: YES')
                    data = []
                    cols = []
                    for d in tr.find_elements(By.XPATH, './/td'):
                        data.append(d.text)

                    header = driver.find_element(By.XPATH, '//*[@id="matchlogs_for"]/thead/tr')
                    cols = header.text.split()[1:]
                    # Fix column name as it is split into separate columns
                    idx = cols.index('Informe')
                    cols[idx] = 'Informe del Partido'
                    del cols[idx+1:idx+3]  # Delete the previous separate columns

                    break

        # Append match info for qualifying matches
        if is_today and is_cup:
            team_data.append(pd.Series(data))
        else:
            print(f'{cup["name"]}: NO')
    #
    if len(team_data) > 0:
        cup_data = pd.concat(team_data, axis=1, ignore_index=True).T
        cup_data.columns = cols
        cup_data.insert(0, 'Jugador', country_players)
        cup_data.insert(1, 'Equipo', team_name)
        cups.append(cup_data)


for cup in cups:
    tweet = [f'\n{cup.Comp[0]}:\n']
    for row in cup.itertuples():
        j = row.Jugador
        t = row.Equipo
        tweet.append(f'{j} - {t}\n')

    tweet = ''.join(tweet)
    print(tweet)
