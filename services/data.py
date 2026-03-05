import requests
import pandas as pd

def get_accounts(user_id = False):
    accounts = requests.get('http://localhost:8080/api/accounts').json()
    
    accounts = pd.DataFrame([acc for acc in accounts])
    
    accounts['LastClaimDate'] = pd.to_datetime(
        accounts['LastClaimDate'],
        errors="coerce",
        utc=True,
        format='ISO8601'
    )
    
    if user_id:
        accounts = accounts.loc[accounts['DiscordId'] == user_id]
    
    return accounts

def get_transactions(user_id = False):
    transactions = requests.get('http://localhost:8080/api/transactions').json()
    
    transactions = pd.DataFrame([t for t in transactions])
    
    transactions['Date'] = pd.to_datetime(
        transactions['Date'],
        errors="coerce",
        utc=True,
        format='ISO8601'
    )
    transactions = transactions.dropna(subset=["Date"])

    if user_id:
        transactions = transactions.loc[
            (transactions['SenderDiscordId'] == user_id) | (transactions['ReceiverDiscordId'] == user_id)
        ]
            
    return transactions

def get_challenges(user_id = False):
    challenges = requests.get('http://localhost:8080/api/challenges').json()
    
    challenges = pd.DataFrame([c for c in challenges])
    
    challenges['Date'] = pd.to_datetime(
        challenges['Date'],
        errors="coerce",
        utc=True,
        format='ISO8601'
    )
    challenges = challenges.dropna(subset=["Date"])

    if user_id:
        challenges = challenges.loc[
            (challenges['ChallengerDiscordId'] == user_id) |
            (challenges['ChallengedDiscordId'] == user_id)
        ]
        
    return challenges

def get_roulettes(user_id = False):
    transactions = requests.get('http://localhost:8080/api/transactions').json()
    roulettes = requests.get('http://localhost:8080/api/roulette').json()
    
    transactions = get_transactions(user_id)
    if transactions.empty:
        return False
    
    roulettes = pd.DataFrame([
        r for r in roulettes
    ]).drop(columns=['Id'])
    
    roulette_wagers = roulettes.rename(columns={
        'WageredTransactionId': 'Id',
        'RewardTransactionId': 'Reward',
        'BetNumber': 'BetNumberWager',
        'RolledNumber': 'RolledNumberWager',
        'BetType': 'BetTypeWager'
    })[['Id', 'Reward', 'BetNumberWager', 'RolledNumberWager', 'BetTypeWager']]
    
    # Transactions final merge
    transactions = (
        transactions
        .merge(roulette_wagers, on='Id', how='left')
    )
    
    if transactions.loc[
        (transactions['TransactionType'] == 4) &
        (transactions['SenderDiscordId'] == user_id)
        , 'Amount'
        ].sum() == 0:
        return None
    
    return transactions