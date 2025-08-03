import json
import pandas as pd
import os

from jinja2 import Template
from enums import *

## Importing data
with open('data/HizzaCoin.Accounts.json', 'r') as f:
    accounts = json.load(f)
    
with open('data/HizzaCoin.Challenges.json', 'r') as f:
    challenges = json.load(f)
    
with open('data/HizzaCoin.Transactions.json', 'r') as f:
    transactions = json.load(f)
    
## Cleaning data
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
transactions_df = pd.DataFrame.from_dict(transactions)

print(challenges_df)

## Creating plots

# July 2025
# How many claims, how many initial claims (new hizzaers)
# How many challenges, most played hand, which hand won most often
# Biggest coingive
# Biggest roulette wager, and biggest roulette win

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
# template = latex_jinja_env.get_template('test.tex')
# print(template.render(section1='Long Form', section2='Short Form'))
