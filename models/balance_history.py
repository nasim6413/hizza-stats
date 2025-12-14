import requests
import pandas as pd

def get_historical_balance(user_id):
    
    transactions = requests.get('http://localhost:8080/api/transactions').json()
    accounts = requests.get('http://localhost:8080/api/accounts').json()
    
    transactions = pd.DataFrame([
        t for t in transactions if 
            (t['SenderDiscordId'] == user_id) or 
            (t['ReceiverDiscordId'] == user_id)
        ]
    )
    
    if not transactions.empty:
        transactions['Date'] = pd.to_datetime(
            transactions['Date'],
            utc=True,
            format='ISO8601'
        ) 
    else:
        return None
    
    # Get current balance
    account = pd.DataFrame([acc for acc in accounts if acc['DiscordId'] == user_id])
    
    account['LastClaimDate'] = pd.to_datetime(
        account['LastClaimDate'],
        utc=True,
        format='ISO8601'
    ) 
    
    today = pd.Timestamp.utcnow().normalize()
    current_balance = int(account['Balance'].iloc[0])

    l30d_balances = {}

    running_end_balance = current_balance

    for i in range(30):
        day = today - pd.Timedelta(days=i)
        day_start = day
        day_end = day + pd.Timedelta(days=1)

        day_tx = transactions[
            (transactions['Date'] >= day_start) &
            (transactions['Date'] < day_end)
        ]

        coins_claimed = day_tx.loc[
            day_tx['TransactionType'].isin([0, 1]),
            'Amount'
        ].sum()

        coins_given = day_tx.loc[
            (day_tx['TransactionType'] == 3) &
            (day_tx['SenderDiscordId'] == user_id),
            'Amount'
        ].sum()

        coins_received = day_tx.loc[
            (day_tx['TransactionType'] == 3) &
            (day_tx['ReceiverDiscordId'] == user_id),
            'Amount'
        ].sum()

        challenges_won = day_tx.loc[
            (day_tx['TransactionType'] == 2) &
            (day_tx['ReceiverDiscordId'] == user_id),
            'Amount'
        ].sum()

        challenges_lost = day_tx.loc[
            (day_tx['TransactionType'] == 2) &
            (day_tx['SenderDiscordId'] == user_id) &
            (day_tx['ReceiverDiscordId'] != '0'), # Coin lock filter
            'Amount'
        ].sum()

        roulettes_won = day_tx.loc[
            (day_tx['TransactionType'] == 4) &
            (day_tx['SenderDiscordId'] == '0'),
            'Amount'
        ].sum()

        roulettes_lost = day_tx.loc[
            (day_tx['TransactionType'] == 4) &
            (day_tx['SenderDiscordId'] == user_id),
            'Amount'
        ].sum()

        start_balance = running_end_balance - (
            coins_claimed    
            + coins_received 
            + challenges_won 
            + roulettes_won  
            - coins_given    
            - challenges_lost
            - roulettes_lost 
        )

        l30d_balances[day.date()] = {
            'start_balance': int(start_balance),
            'end_balance': int(running_end_balance)
        }

        running_end_balance = start_balance
        
    return l30d_balances

def get_top5_historical_balance():
    accounts = requests.get('http://localhost:8080/api/accounts').json()
    
    accounts = pd.DataFrame([acc for acc in accounts])

    top5 = accounts.nlargest(5, 'Balance')['DiscordId'].values.tolist()
    
    top5_balances = {}
    for user in top5:
        top5_balances[user] = get_historical_balance(user)
        
    return top5_balances