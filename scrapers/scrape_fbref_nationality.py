# libraries
import numpy as np
import pandas as pd
from datetime import date
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import flag

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

hoy = f'{today.year}-{mes}-{today.day}' # Today's date in dataframe's format


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
