import requests
import pandas as pd
from models.balance_history import get_historical_balance

def get_top5_historical_balance():
    accounts = requests.get('http://localhost:8080/api/accounts').json()
    
    accounts = pd.DataFrame([acc for acc in accounts])

    top5 = accounts.nlargest(5, 'Balance')['DiscordId'].values.tolist()
    
    top5_balances = {}
    for user in top5:
        top5_balances[user] = get_historical_balance(user)
        
    return top5_balances

def get_economy_shares():
    accounts = requests.get('http://localhost:8080/api/accounts').json()
    
    accounts = pd.DataFrame([acc for acc in accounts])
    
    balances = accounts.sort_values(by='Balance', ascending=False)
    
    top5_balances = balances.iloc[:5]
    
    rest_balances = balances.iloc[6:]
    total_economy = accounts['Balance'].sum()
    
    
    economy_shares = {}
    for i, j in top5_balances.iterrows():
        economy_shares[j['DiscordId']] = round((j['Balance'] / total_economy) * 100, 2)
        
    economy_shares['Others'] = round((rest_balances['Balance'].sum() / total_economy) * 100, 2)
    
    return economy_shares