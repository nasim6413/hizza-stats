import pandas as pd
from services.data import *

def get_top_streaks():
    accounts = get_accounts()

    # Drop Hizza account
    accounts = accounts.drop(accounts[accounts['DiscordId'] == "0"].index) 
    
    accounts = accounts.sort_values(by='Streak', ascending=False)
    
    today = pd.Timestamp.utcnow().normalize()
    accounts['days_since_claim'] = (today - accounts['LastClaimDate']).dt.days
    
    # Get total number of users with a streak
    streakers = (
        (accounts['Streak'] > 0) &
        (accounts['days_since_claim'] <= 2)
        ).sum()
    
    accounts = accounts.iloc[:5] # Retrieves top 5
    
    data = {
        'streakers' : streakers,
        'users' : [],
        'streak_num' : [],
        'claim_status' : []
    }
    
    for i, row in accounts.iterrows():
        data['users'].append(row['DiscordId'])
        data['streak_num'].append(str(row['Streak']))
        
        if row['days_since_claim'] == 0:
            data['claim_status'].append(1)
        elif row['days_since_claim'] in [1, 2]:
            data['claim_status'].append(2)
        elif row['days_since_claim'] > 2:
            data['claim_status'].append(3)
            
    return data

def get_in_danger():
    accounts = get_accounts()

    # Drop Hizza account
    accounts = accounts.drop(accounts[accounts['DiscordId'] == "0"].index) 

    accounts = accounts.sort_values(by='Streak', ascending=False)
    
    today = pd.Timestamp.utcnow().normalize()
    accounts['days_since_claim'] = (today - accounts['LastClaimDate']).dt.days
    
    data = {
        'users' : [],
        'streak_num' : []
    }
    
    for i, row in accounts.iterrows():
        if row['days_since_claim'] in [1, 2] and row['Streak'] > 30:
            data['users'].append(row['DiscordId'])
            data['streak_num'].append(str(row['Streak']))
            
    return data