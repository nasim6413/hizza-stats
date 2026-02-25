import pandas as pd
from services.data import *

def get_top_streaks():
    accounts = get_accounts()

    # Drop Hizza account
    accounts = accounts.drop(accounts[accounts['DiscordId'] == "0"].index) 

    accounts = accounts.sort_values(by='Streak', ascending=False)
    accounts = accounts.iloc[:5] # Retrieves top 5
    
    data = {
        'users' : [],
        'streak_num' : [],
        'claim_status' : []
    }
    
    for i, row in accounts.iterrows():
        data['users'].append(row['DiscordId'])
        data['streak_num'].append(str(row['Streak']))
        
        today = pd.Timestamp.utcnow().normalize()
        days_since_claim = (today - row['LastClaimDate']).days
        
        if days_since_claim == 0:
            data['claim_status'].append(1)
        elif days_since_claim == 1:
            data['claim_status'].append(2)
        elif days_since_claim > 1:
            data['claim_status'].append(3)
            
    return data

