import requests
import pandas as pd

def get_transaction_history(user_id):

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
        
        transactions = (
            transactions
            .sort_values(by='Date', ascending=False)
            .iloc[:99]
        )

    else:
        return None
    
    # Get current balance
    account = pd.DataFrame([acc for acc in accounts if acc['DiscordId'] == user_id])
    
    current_balance = int(account['Balance'].iloc[0])

    l100_transactions = {}
    
    running_balance = current_balance
    count = 0
    l100_transactions[count] = running_balance # starting balance

    for i, j in transactions.iterrows():
        if j['TransactionType'] in (0, 1):
            running_balance -= j['Amount']
        
        if j['TransactionType'] == 3 and j['SenderDiscordId'] == user_id:
            running_balance += j['Amount']

        if j['TransactionType'] == 3 and j['ReceiverDiscordId'] == user_id:
            running_balance -= j['Amount']
            
        if j['TransactionType'] == 2 and j['SenderDiscordId'] == user_id and j['ReceiverDiscordId'] != '0':
            running_balance += j['Amount']
            
        if j['TransactionType'] == 2 and j['ReceiverDiscordId'] == user_id:
            running_balance -= j['Amount']

        if j['TransactionType'] == 4 and j['SenderDiscordId'] == '0':
            running_balance -= j['Amount']
            
        if j['TransactionType'] == 4 and j['SenderDiscordId'] == user_id:
            running_balance += j['Amount']

        count += 1
        l100_transactions[count] = running_balance

    return l100_transactions

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