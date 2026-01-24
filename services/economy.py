import pandas as pd
from services.data import *

def get_economy_shares():
    accounts = get_accounts()
    
    balances = accounts.sort_values(by='Balance', ascending=False)

    total_economy = accounts['Balance'].sum()
    balances['Share'] = round((balances['Balance'] / total_economy) * 100, 2)
    
    top_number = 5
    if balances.iloc[0]['Share'] >= 45:
        top_number = 4
    
    top_balances = balances.iloc[:top_number]
    rest_balances = balances.iloc[top_number:]
    
    economy_shares = {}
    for i, j in top_balances.iterrows():
        economy_shares[j['DiscordId']] = j['Share']
        
    economy_shares['Others'] = sum(rest_balances['Share'])
    
    return economy_shares