import requests
from dateutil.parser import isoparse
from utils.helpers import fetch_months
from utils.enums import *

class HizzaReport:
    def __init__(self, timeframe):
        self.timeframe = timeframe
        self.transactions = []
        self.challenges = []
        
        transactions = requests.get('http://localhost:8080/api/transactions').json()
        challenges = requests.get('http://localhost:8080/api/challenges').json()
        
        # Date filtering
        if self.timeframe:
            month, year = fetch_months(self.timeframe)
            
            for item in transactions:
                date = isoparse(item['Date']) 
                
                if date.month == month and date.year == year:
                    self.transactions.append(item)
                    
            for item in challenges:
                date = isoparse(item['Date']) 
                
                if date.month == month and date.year == year:
                    self.challenges.append(item)
        
        else:
            self.transactions = transactions
            self.challenges = challenges 
    
    def get_coin_results(self):
        """Returns statistics based on coin activity."""
        coin_results = {
            'TotalClaims' : 0,
            'TotalClaimed' : 0,
            'TotalClaimers' : [],
            'BiggestClaim' : 0,
            'BiggestClaimer' : '',
            'InitialClaims' : 0,
            'TotalCoinGives' : 0,
            'TotalCoinGiven' : 0,
            'BiggestCoinGive' : 0,
            'BiggestCoinGiver' : '',
            'BiggestCoinReceiver' : ''
            }
        
        for item in self.transactions:
            # Claims
            if item['TransactionType'] == 1:
                coin_results['TotalClaims'] += 1
                coin_results['TotalClaimed'] += item['Amount']
                
                if item['ReceiverDiscordId'] not in coin_results['TotalClaimers']:
                    coin_results['TotalClaimers'].append(item['ReceiverDiscordId'])
                
                if item['Amount'] > coin_results['BiggestClaim']:
                    coin_results['BiggestClaim'] = item['Amount']
                    coin_results['BiggestClaimer'] = item['ReceiverDiscordId']
                 
            # Initial
            if item['TransactionType'] == 0:
                coin_results['InitialClaims'] += 1
                
            # Give
            if item['TransactionType'] == 3:
                coin_results['TotalCoinGives'] += 1
                coin_results['TotalCoinGiven'] += item['Amount']
                
                if item['Amount'] > coin_results['BiggestCoinGive']:
                    coin_results['BiggestCoinGive'] = item['Amount']
                    coin_results['BiggestCoinGiver'] = item['SenderDiscordId']
                    coin_results['BiggestCoinReceiver'] = item['ReceiverDiscordId']
                    
        return coin_results
    
    def get_challenge_results(self):
        """Returns statistics based on challenge activity."""
        challenge_results = {
            'TotalChallenges' : 0,
            'BiggestChallengeWin' : 0,
            'BiggestChallengeWinner' : '',
            'BiggestChallengeLoser' : '',
            
            'MostChallenged' : {},
            'MostChallenger' : {},
            'TotalWins' : {},
            'TotalLosses' : {},
            'MostWins' : '',
            'MostLosses': '',
            
            'PlayedHands' : {
                1 : 0,
                2 : 0,
                3 : 0
            },
            'MostPlayedHand' : 0,
            
            'WinningHands' : {
                1 : 0,
                2 : 0,
                3 : 0
            },
            'MostWinsHand' : 0
        }
        
        for item in self.challenges:
            if item['State'] in [1, 2, 3]: # Challenge is complete
                
                challenge_results['TotalChallenges'] += 1
                
                challenge_results['PlayedHands'][item['ChallengerHand']] += 1
                challenge_results['PlayedHands'][item['ChallengedHand']] += 1
                
                # Challenger win                
                if item['State'] == 1:
                    challenge_results['WinningHands'][item['ChallengerHand']] += 1
                    
                    if item['Wager'] > challenge_results['BiggestChallengeWin']:
                        challenge_results['BiggestChallengeWin'] = item['Wager']
                        challenge_results['BiggestChallengeWinner'] = item['ChallengerDiscordId']
                        challenge_results['BiggestChallengeLoser'] = item['ChallengedDiscordId']
                        
                    # Updates wins and losses
                    if item['ChallengerDiscordId'] in challenge_results['TotalWins']:
                        challenge_results['TotalWins'][item['ChallengerDiscordId']] += 1
                    else:
                        challenge_results['TotalWins'][item['ChallengerDiscordId']] = 1
                        
                    if item['ChallengedDiscordId'] in challenge_results['TotalLosses']:
                        challenge_results['TotalLosses'][item['ChallengedDiscordId']] += 1
                    else:
                        challenge_results['TotalLosses'][item['ChallengedDiscordId']] = 1
                    
                # Challenged win
                if item['State'] == 2:
                    challenge_results['WinningHands'][item['ChallengedHand']] += 1
                    
                    if item['Wager'] > challenge_results['BiggestChallengeWin']:
                        challenge_results['BiggestChallengeWin'] = item['Wager']
                        challenge_results['BiggestChallengeWinner'] = item['ChallengedDiscordId']
                        challenge_results['BiggestChallengeLoser'] = item['ChallengerDiscordId']
                        
                    # Updates wins and losses
                    if item['ChallengedDiscordId'] in challenge_results['TotalWins']:
                        challenge_results['TotalWins'][item['ChallengedDiscordId']] += 1
                    else:
                        challenge_results['TotalWins'][item['ChallengedDiscordId']] = 1
                        
                    if item['ChallengerDiscordId'] in challenge_results['TotalLosses']:
                        challenge_results['TotalLosses'][item['ChallengerDiscordId']] += 1
                    else:
                        challenge_results['TotalLosses'][item['ChallengerDiscordId']] = 1
                    
                # Most wins and losses
                challenge_results['MostWins'] = max(challenge_results['TotalWins'], key=challenge_results['TotalWins'].get)
                challenge_results['MostLosses'] = max(challenge_results['TotalLosses'], key=challenge_results['TotalLosses'].get)
                
                challenge_results['MostPlayedHand'] = max(challenge_results['PlayedHands'], key=challenge_results['PlayedHands'].get)
                challenge_results['MostWinsHand'] = max(challenge_results['WinningHands'], key=challenge_results['WinningHands'].get)
                        
        return challenge_results
    
    def get_roulette_results(self):
        """Returns statistics based on roulette activity."""
        roulette_results = {
            'TotalRouletteWagers' : 0,
            'BiggestRouletteWager' : 0,
            'BiggestRouletteWin' : 0,
            'BiggestRouletteLoss' : 0,
            
            'MostWagers' : {},
            'MostWins' : {},
            'MostLosses' : {}
            }
        
        #TODO: loops
        
        return roulette_results