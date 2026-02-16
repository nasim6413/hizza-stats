import pandas as pd
from services.data import *

def get_economy_shares():
    accounts = get_accounts()
    
    balances = accounts.sort_values(by='Balance', ascending=False)

    total_economy = accounts['Balance'].sum()
    balances['Share'] = round((balances['Balance'] / total_economy) * 100, 2)
    
    largest_share = balances.iloc[0]['Share']
    
    # Balance pie chart if shares are too large
    if largest_share >= 45:
        top_number = 4
    if largest_share >= 60:
        top_number = 3
    if largest_share >= 70:
        top_number = 2
    if largest_share >= 80:
        top_number = 1
    else:
        top_number = 5
        
    top_balances = balances.iloc[:top_number]
    rest_balances = balances.iloc[top_number:]
    
    economy_shares = {}
    for i, j in top_balances.iterrows():
        economy_shares[j['DiscordId']] = j['Share']
        
    economy_shares['Others'] = sum(rest_balances['Share'])
    
    return economy_shares