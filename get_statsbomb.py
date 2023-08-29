import pandas as pd
from statsbombpy import sb

# Get data
m_id = 69302  # FCB match
events = sb.events(match_id=m_id)
events.to_csv(f'match_{m_id}.csv')
