import requests
from enums import *

class UserStats:
    def __init__(self, user_id):
        self.user_id = user_id
        self.transactions = False
        self.challenges = False
        
        self.coin_results = {
            'TotalClaims' : 0,
            'BiggestClaim' : 0,
            'TotalGives' : 0,
            'TotalGiveAmount' : 0,
            'TotalGiven' : 0,
            'TotalGivenAmount' : 0,
            'BiggestGive' : 0,
            'BiggestGiveTo' : '',
            'BiggestGiven' : 0,
            'BiggestGivenFrom' : 0
            }
        
        self.challenge_results = {
            'TotalChallenges' : 0,
            'TotalChallenger' : 0,
            'TotalChallenged' : 0,
            'FavouriteHand' : 0,
            'FavouriteHands' : {
                1 : 0,
                2 : 0,
                3 : 0
                }
            }
        
        self.roulette_results = {
            'WagerCount' : 0,
            'BiggestWin' : 0,
            'BiggestLoss' : 0
            }

        self.get_user_stats()
        
        self.get_coin_results()
        self.get_challenge_results()
        self.get_roulette_results()
                
    def get_user_stats(self):
        transactions = requests.get('http://localhost:8080/api/transactions').json()
        challenges = requests.get('http://localhost:8080/api/challenges').json()
        
        self.transactions = [
            t for t in transactions if 
                (t['SenderDiscordId'] == self.user_id) or 
                (t['ReceiverDiscordId'] == self.user_id)
            ]

        self.challenges = [
            c for c in challenges if 
                (c['ChallengerDiscordId'] == self.user_id) or 
                (c['ChallengedDiscordId'] == self.user_id)
            ]
        
        return

    def get_coin_results(self):       
        for item in self.transactions:
            
            if item['TransactionType'] == 1:
                # Adds up total claims
                self.coin_results['TotalClaims'] += 1
                
                # Changes biggest claim if larger than current
                if item['Amount'] > self.coin_results['BiggestClaim']:
                    self.coin_results['BiggestClaim'] = item['Amount']
        
            if item['TransactionType'] == 3:
                
                # Coin gives
                if item['SenderDiscordId'] == self.user_id:
                    self.coin_results['TotalGives'] += 1
                    self.coin_results['TotalGiveAmount'] += item['Amount']
                    
                    if item['Amount'] > self.coin_results['BiggestGive']:
                        self.coin_results['BiggestGive'] = item['Amount']
                        self.coin_results['BiggestGiveTo'] = item['ReceiverDiscordId']
                    
                # Coin receives
                if item['ReceiverDiscordId'] == self.user_id:
                    self.coin_results['TotalGiven'] += 1
                    self.coin_results['TotalGivenAmount'] += item['Amount']
                    
                    if item['Amount'] > self.coin_results['BiggestGiven']:
                        self.coin_results['BiggestGiven'] = item['Amount']
                        self.coin_results['BiggestGivenFrom'] = item['SenderDiscordId']
                
        return

    def get_challenge_results(self):       
        for item in self.challenges:
            if item['State'] in [1, 2, 3]: # Completed challenges
                self.challenge_results['TotalChallenges'] += 1
                
                if item['ChallengerDiscordId'] == self.user_id:
                    self.challenge_results['TotalChallenger'] += 1
                    
                    # Append hands
                    self.challenge_results['FavouriteHands'][item['ChallengerHand']] += 1
                    
                elif item['ChallengedDiscordId'] == self.user_id:
                    self.challenge_results['TotalChallenged'] += 1
                    
                    # Append hands
                    self.challenge_results['FavouriteHands'][item['ChallengedHand']] += 1
        
        # Finding favourite hand
        self.challenge_results['FavouriteHand'] = max(self.challenge_results['FavouriteHands'], key=self.challenge_results['FavouriteHands'].get)
        self.challenge_results['FavouriteHand'] = CHALLENGE_HANDS[self.challenge_results['FavouriteHand']]
                
        return

    def get_roulette_results(self):
        previous_wager = 0 # Flag for tracking losses
        
        for item in self.transactions:
            if item['TransactionType'] == 4:
                
                # Either a wager or a loss
                if item['SenderDiscordId'] == self.user_id: 
                    
                    # Checks if previous wager was a loss
                    if previous_wager > self.roulette_results['BiggestLoss']:
                        self.roulette_results['BiggestLoss'] = previous_wager
                    
                    # Updates previous_wager to current wager
                    previous_wager = item['Amount']
                    
                    # Updates wager count
                    self.roulette_results['WagerCount'] += 1
                    
                if item['ReceiverDiscordId'] == self.user_id:   
                                
                    # Sets new biggest win
                    if item['Amount'] > self.roulette_results['BiggestWin']:
                        self.roulette_results['BiggestWin'] = item['Amount']
                    
                    # Update flag
                    previous_wager = 0
                    
        return