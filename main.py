import json
import pandas as pd
import matplotlib.pyplot as plt
import os
import jinja2
import subprocess
from enums import *

## IMPORTING DATA & CLEANING
with open('data/HizzaCoin.Accounts.json', 'r') as f:
    accounts = json.load(f)
    
with open('data/HizzaCoin.Challenges.json', 'r') as f:
    challenges = json.load(f)
    
with open('data/HizzaCoin.Transactions.json', 'r') as f:
    transactions = json.load(f)
    
# Accounts
for i in accounts:
    i['AccountId'] = i['_id']['$oid']
    del i['_id']
    
    i['LastClaimDate'] = i['LastClaimDate']['$date']
    
# Challenges
for i in challenges:
    i['ChallengeId'] = i['_id']['$oid']
    del i['_id']
        
    i['ChallengeDate'] = i['Date']['$date']
    del i['Date']
    
# Transactions
for i in transactions:
    i['TransactionId'] = i['_id']['$oid']
    del i['_id']
    
    i['TransactionDate'] = i['Date']['$date']
    del i['Date']

# Convert to DataFrame
accounts_df = pd.DataFrame.from_dict(accounts)
challenges_df = pd.DataFrame.from_dict(challenges)
transactions_df = pd.DataFrame.from_dict(transactions).dropna(ignore_index=True)

# Fixing datetime
accounts_df['LastClaimDate'] = pd.to_datetime(accounts_df['LastClaimDate'])
challenges_df['ChallengeDate'] = pd.to_datetime(challenges_df['ChallengeDate'])
transactions_df['TransactionDate'] = pd.to_datetime(transactions_df['TransactionDate'])

# Typecasting
transactions_df['ReceiverDiscordId'] = transactions_df['ReceiverDiscordId'].astype(int)
transactions_df['SenderDiscordId'] = transactions_df['SenderDiscordId'].astype(int)

## EXTRACTING RESULTS
results = {
    'TotalClaims' : 0,
    'BiggestClaim' : 0,
    'InitialClaims' : 0,
    'TotalChallenges' : 0,
    'MostPlayedHand' : {
        1 : 0,
        2: 0,
        3: 0
    },
    
    'MostWinsHand' : {
        1 : 0,
        2 : 0,
        3 : 0
    },
    
    'TotalCoinGives' : 0,
    'BiggestCoinGive' : 0,
    'TotalRouletteWagers' : 0,
    'BiggestRouletteWager' : 0,
    'BiggestRouletteWin' : 0
}

# DATE FILTER TODO: make this editable
date = 'July 2025'
challenges_df = challenges_df[(challenges_df['ChallengeDate'].dt.year == 2025) & (challenges_df['ChallengeDate'].dt.month == 7)]

transactions_df = transactions_df[(transactions_df['TransactionDate'].dt.year == 2025) & (transactions_df['TransactionDate'].dt.month == 7)]

# Transaction types
transaction_types = transactions_df.groupby(['TransactionType']).size()

results['TotalClaims'] = transaction_types.loc[1]
# results['InitialClaims'] = transactions_df.groupby(['TransactionType']).size().loc[0]
results['TotalCoinGives'] = transaction_types.loc[3]
results['TotalRouletteWagers'] = transaction_types.loc[4]

# Challenges Hands
total_challenges = challenges_df.groupby(['State']).size()
results['TotalChallenges'] = total_challenges.loc[1] + total_challenges.loc[2] + total_challenges.loc[3]

challenger_hands = challenges_df.groupby(['State', 'ChallengerHand'], as_index=False).size()
challenged_hands = challenges_df.groupby(['State', 'ChallengedHand'], as_index=False).size()

for i in range(1,4):
    # Played hands
    results['MostPlayedHand'][i] += challenger_hands.loc[
        (challenger_hands['State'].isin([1, 2, 3]))
        & (challenger_hands['ChallengerHand'] == i)
    ]['size'].sum()
    
    results['MostPlayedHand'][i] += challenged_hands.loc[
        (challenged_hands['State'].isin([1, 2, 3]))
        & (challenged_hands['ChallengedHand'] == i)
    ]['size'].sum()
    
    # Winning hands
    results['MostWinsHand'][i] += challenger_hands.loc[
        (challenger_hands['State'] == 1) 
        & (challenger_hands['ChallengerHand'] == i)
    ]['size'].sum()
    
    results['MostWinsHand'][i] += challenged_hands.loc[
        (challenged_hands['State'] == 2) 
        & (challenged_hands['ChallengedHand'] == i)
    ]['size'].sum()

# Transaction amounts
results['BiggestCoinGive'] = transactions_df.loc[transactions_df['TransactionType'] == 3]['Amount'].max()

results['Top5RouletteWagers'] = transactions_df.loc[
    (transactions_df['TransactionType'] == 4)
    & (transactions_df['ReceiverDiscordId'] == 0)]['Amount'].nlargest(5).tolist()

results['Top5RouletteWins'] = transactions_df.loc[
    (transactions_df['TransactionType'] == 4)
    & (transactions_df['SenderDiscordId'] == 0)]['Amount'].nlargest(5).tolist()

results['BiggestRouletteWager'] = max(results['Top5RouletteWagers'])
results['BiggestRouletteWin'] = max(results['Top5RouletteWins'])

print(results)

## CREATING PLOTS
# Custom colors
colours = ['#9c399e','#c73c5a','#e8af25']

# Most played hands
labels = list(results['MostPlayedHand'].keys())
labels = [CHALLENGE_HANDS[i] for i in labels]
sizes = list(results['MostPlayedHand'].values())

plt.figure(figsize=(4,4))
plt.pie(sizes, labels=labels, colors=colours, autopct='%1.0f%%', startangle=90)
plt.title('Most Played Hands')
plt.tight_layout()
plt.savefig('plots/mostplayedhands.png')

# Most winning hands
labels = list(results['MostWinsHand'].keys())
labels = [CHALLENGE_HANDS[i] for i in labels]
sizes = list(results['MostWinsHand'].values())

plt.figure(figsize=(4,4))
plt.pie(sizes, labels=labels, colors=colours, autopct='%1.0f%%', startangle=90)
plt.title('Winning Hands')
plt.tight_layout()
plt.savefig('plots/mostwinshands.png')

top5 = ['1st', '2nd', '3rd', '4th', '5th']

# Top 5 wagers
plt.figure(figsize=(4,4))
bars = plt.bar(top5, results['Top5RouletteWagers'], color=colours[0])
plt.title('Top 5 Roulette Wagers')

# Add value labels on top
for bar, amount in zip(bars, results['Top5RouletteWagers']):
    plt.text(
        bar.get_x() + bar.get_width()/2,
        bar.get_height(),
        f'{amount:,}',
        ha='center', va='bottom', fontsize=8
    )
    
plt.tight_layout()
plt.savefig('plots/top5wagers.png')

# Top 5 wins
plt.figure(figsize=(4,4))
bars = plt.bar(top5, results['Top5RouletteWins'], color=colours[0])
plt.title('Top 5 Roulette Wins')

# Add value labels on top
for bar, amount in zip(bars, results['Top5RouletteWins']):
    plt.text(
        bar.get_x() + bar.get_width()/2,
        bar.get_height(),
        f'{amount:,}',
        ha='center', va='bottom', fontsize=8
    )

plt.tight_layout()
plt.savefig('plots/top5wins.png')

## WRITING TO LATEX
## Generating Jinja env
latex_jinja_env = jinja2.Environment(
    block_start_string = '\BLOCK{',    # instead of {% 
    block_end_string = '}',            # instead of %}
    variable_start_string = '\VAR{',   # instead of {{
    variable_end_string = '}',         # instead of }}
    comment_start_string = '\#{',      # instead of {#
    comment_end_string = '}',          # instead of #}
    line_statement_prefix = '%%',      # lines starting with %% are statements
    line_comment_prefix = '%#',        # lines starting with %# are comments
	trim_blocks = True,
	autoescape = False,
	loader = jinja2.FileSystemLoader(os.path.abspath('.'))
)

# Creating report
template = latex_jinja_env.get_template('template.tex')
rendered = template.render(
    date=date,
    results=results,
    most_played_hands_plot='plots/mostplayedhands.png',
    most_wins_hands_plot='plots/mostwinshands.png',
    top_5_wagers_plot = 'plots/top5wagers.png',
    top_5_wins_plot = 'plots/top5wins.png'
)

with open('output.tex', 'w') as f:
    f.write(rendered)
subprocess.run(['lualatex', 'output.tex'])