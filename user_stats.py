import requests
from enums import *

#TODO: rename funcs/vars

def get_user_stats(user_id):
    transactions = requests.get('http://localhost:8080/api/transactions').json()
    challenges = requests.get('http://localhost:8080/api/challenges').json()
    
    user_transactions = [
        t for t in transactions if 
            (t['SenderDiscordId'] == user_id) or 
            (t['ReceiverDiscordId'] == user_id)
        ]

    user_challenges = [
        c for c in challenges if 
            (c['ChallengerDiscordId'] == user_id) or 
            (c['ChallengedDiscordId'] == user_id)
        ]
    
    return user_transactions, user_challenges

def get_coin_results(transactions):
    coin_stats = {'TotalClaims' : 0,
                  'BiggestClaim' : 0}
    
    for item in transactions:
        
        if item['TransactionType'] == 1:
            # Adds up total claims
            coin_stats['TotalClaims'] += 1
            
            # Changes biggest claim if larger than current
            if item['Amount'] > coin_stats['BiggestClaim']:
                coin_stats['BiggestClaim'] = item['Amount']
            
    return coin_stats

def get_challenge_stats(challenges, user_id):
    chal_stats = {'TotalChallenges' : 0,
                  'TotalChallenger' : 0,
                  'TotalChallenged' : 0,
                  'FavouriteHands' :
                      {1 : 0,
                       2 : 0,
                       3 : 0}}
    
    for item in challenges:
        if item['State'] in [1, 2, 3]: # Completed challenges
            chal_stats['TotalChallenges'] += 1
            
            if item['ChallengerDiscordId'] == user_id:
                chal_stats['TotalChallenger'] += 1
                
                # Append hands
                chal_stats['FavouriteHands'][item['ChallengerHand']] += 1
                
            elif item['ChallengedDiscordId'] == user_id:
                chal_stats['TotalChallenged'] += 1
                
                # Append hands
                chal_stats['FavouriteHands'][item['ChallengedHand']] += 1
                       
    return chal_stats

# def get_roulette_results(transactions, user_id)

# TEST
transactions, challenges = get_user_stats('148455623313326080') 

print(transactions)
print(challenges)


print(get_coin_results(transactions))       
print(get_challenge_stats(challenges, '148455623313326080'))