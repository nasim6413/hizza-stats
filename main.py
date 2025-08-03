import json
import pandas as pd
import matplotlib
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

results['BiggestRouletteWager'] = transactions_df.loc[
    (transactions_df['TransactionType'] == 4)
    & (transactions_df['ReceiverDiscordId'] == 0)]['Amount'].max()

results['BiggestRouletteWin'] = transactions_df.loc[
    (transactions_df['TransactionType'] == 4)
    & (transactions_df['SenderDiscordId'] == 0)]['Amount'].max()

print(results)

## CREATING PLOTS

## WRITING TO LATEX TODO: fix thissss
# ## Generating Jinja env
# latex_jinja_env = jinja2.Environment(
#     block_start_string = '\BLOCK{',    # instead of {% 
#     block_end_string = '}',            # instead of %}
#     variable_start_string = '\VAR{',   # instead of {{
#     variable_end_string = '}',         # instead of }}
#     comment_start_string = '\#{',      # instead of {#
#     comment_end_string = '}',          # instead of #}
#     line_statement_prefix = '%%',      # lines starting with %% are statements
#     line_comment_prefix = '%#',        # lines starting with %# are comments
# 	trim_blocks = True,
# 	autoescape = False,
# 	loader = jinja2.FileSystemLoader(os.path.abspath('.'))
# )

# ## Creating report
# template = latex_jinja_env.get_template('template.tex')
# rendered = template.render(
#     title='Fun Report',
#     section1_title='First Section',
#     section1_text='Here is the first section content.',
#     plot1='plot1.png',
#     section2_title='Second Section',
#     section2_text='Second section content.',
#     plot2='plot2.png'
# )

# # Write to .tex
# with open('output_rendered.tex', 'w') as f:
#     f.write(rendered)

# # Compile to PDF using lualatex
# subprocess.run(['lualatex', 'output_rendered.tex'])