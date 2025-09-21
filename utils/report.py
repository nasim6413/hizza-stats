import requests
from datetime import datetime
from dateutil.parser import isoparse
from utils.helpers import fetch_months
from utils.enums import *

class HizzaReport:
    def __init__(self, timeframe):
        self.timeframe = timeframe
        self.transactions = []
        self.challenges = []
        
        self.coin_results = {
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
        
        self.challenge_results = {
            'TotalChallenges' : 0,
            'BiggestChallengeWin' : 0,
            'BiggestChallengeWinner' : '',
            'BiggestChallengeLoser' : '',
            
            'MostPlayedHand' : {
                1 : 0,
                2 : 0,
                3 : 0
            },
            
            'MostWinsHand' : {
                1 : 0,
                2 : 0,
                3 : 0
            }
        }
            
        self.roulette_results = {
            'TotalRouletteWagers' : 0,
            'BiggestRouletteWager' : 0,
            'BiggestRouletteWin' : 0,
            'BiggestRouletteLoss' : 0
            }
        
        self.get_hizza_stats()
        
        self.get_coin_results()
        self.get_challenge_results()
        
    def get_hizza_stats(self):
        """Requests data and filters based on timeframe parameter."""
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
            
        return
    
    def get_coin_results(self):
        
        for item in self.transactions:
            # Claims
            if item['TransactionType'] == 1:
                self.coin_results['TotalClaims'] += 1
                self.coin_results['TotalClaimed'] += item['Amount']
                
                if item['ReceiverDiscordId'] not in self.coin_results['TotalClaimers']:
                    self.coin_results['TotalClaimers'].append(item['ReceiverDiscordId'])
                
                if item['Amount'] > self.coin_results['BiggestClaim']:
                    self.coin_results['BiggestClaim'] = item['Amount']
                    self.coin_results['BiggestClaimer'] = item['ReceiverDiscordId']
                 
            # Initial
            if item['TransactionType'] == 0:
                self.coin_results['InitialClaims'] += 1
                
            # Give
            if item['TransactionType'] == 3:
                self.coin_results['TotalCoinGives'] += 1
                self.coin_results['TotalCoinGiven'] += item['Amount']
                
                if item['Amount'] > self.coin_results['BiggestCoinGive']:
                    self.coin_results['BiggestCoinGive'] = item['Amount']
                    self.coin_results['BiggestCoinGiver'] = item['SenderDiscordId']
                    self.coin_results['BiggestCoinReceiver'] = item['ReceiverDiscordId']
                    
        return
    
    def get_challenge_results(self):
        
        for item in self.challenges:
            if item['State'] in [1, 2, 3]: # Challenge is complete
                
                self.challenge_results['TotalChallenges'] += 1
                
                self.challenge_results['MostPlayedHand'][item['ChallengerHand']] += 1
                self.challenge_results['MostPlayedHand'][item['ChallengedHand']] += 1
                
                # Challenger win                
                if item['State'] == 1:
                    self.challenge_results['MostWinsHand'][item['ChallengerHand']] += 1
                    
                    if item['Wager'] > self.challenge_results['BiggestChallengeWin']:
                        self.challenge_results['BiggestChallengeWin'] = item['Wager']
                        self.challenge_results['BiggestChallengeWinner'] = item['ChallengerDiscordId']
                        self.challenge_results['BiggestChallengeLoser'] = item['ChallengedDiscordId']
                    
                # Challenged win
                if item['State'] == 2:
                    self.challenge_results['MostWinsHand'][item['ChallengedHand']] += 1
                    
                    if item['Wager'] > self.challenge_results['BiggestChallengeWin']:
                        self.challenge_results['BiggestChallengeWin'] = item['Wager']
                        self.challenge_results['BiggestChallengeWinner'] = item['ChallengedDiscordId']
                        self.challenge_results['BiggestChallengeLoser'] = item['ChallengerDiscordId']
                
        return