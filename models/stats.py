import requests
import pandas as pd
from utils.helpers import fetch_months
from utils.enums import *

class UserStats:
    def __init__(self, user_id):
        self.user_id = user_id
        self.transactions = []
        self.challenges = []
        
        transactions = requests.get('http://localhost:8080/api/transactions').json()
        challenges = requests.get('http://localhost:8080/api/challenges').json()
        roulettes = requests.get('http://localhost:8080/api/roulette').json()
        
        # User filtering
        transactions = [
            t for t in transactions if 
                (t['SenderDiscordId'] == self.user_id) or 
                (t['ReceiverDiscordId'] == self.user_id)
            ]

        challenges = [
            c for c in challenges if 
                (c['ChallengerDiscordId'] == self.user_id) or 
                (c['ChallengedDiscordId'] == self.user_id)
            ]
        
        roulettes = [
            r for r in roulettes
        ]
        
        self.challenges = pd.DataFrame(challenges)
        
        # Merge transactions & roulettes
        transactions = pd.DataFrame(transactions)
        roulettes = pd.DataFrame(roulettes).drop(columns=['Id'])
        
        # Wager merge table
        roulette_wagers = roulettes.rename(columns={
            'WageredTransactionId': 'Id',
            'BetNumber': 'BetNumberWager',
            'RolledNumber': 'RolledNumberWager',
            'BetType': 'BetTypeWager'
        })[['Id', 'BetNumberWager', 'RolledNumberWager', 'BetTypeWager']]

        # Reward merge table
        roulette_rewards = roulettes.rename(columns={
            'RewardTransactionId': 'Id',
            'BetNumber': 'BetNumberReward',
            'RolledNumber': 'RolledNumberReward',
            'BetType': 'BetTypeReward'
        })[['Id', 'BetNumberReward', 'RolledNumberReward', 'BetTypeReward']]
        
        # Transactions final merge
        self.transactions = (
            transactions
            .merge(roulette_wagers, on='Id', how='left')
            .merge(roulette_rewards, on='Id', how='left')
        )
        
        # Date filtering TODO: add start date
        if not self.transactions.empty:
            self.transactions['Date'] = pd.to_datetime(
                self.transactions['Date'],
                utc=True,
                format='ISO8601'
            ) 
        
        if not self.challenges.empty:
            self.challenges['Date'] = pd.to_datetime(
                self.challenges['Date'],
                utc=True,
                format='ISO8601'
            ) 

        return

    def get_coin_results(self):
        """Get user statistics based on coin activity."""
        if self.transactions.empty:
            return None
        
        coin_results = {} 
        
        coin_results['TotalClaims'] = (
            (self.transactions['TransactionType'] == 1)
            ).sum()
        
        coin_results['TotalClaimed'] = self.transactions.loc[
            self.transactions['TransactionType'] == 1, 'Amount'
            ].sum()
        
        coin_results['BestClaim'] = self.transactions.loc[
            self.transactions['TransactionType'] == 1, 'Amount'
            ].max()
        
        coin_results['TotalGiveAmount'] = self.transactions.loc[
            (self.transactions['TransactionType'] == 3) & 
            (self.transactions['SenderDiscordId'] == self.user_id)
            , 'Amount'
            ].sum()
        
        coin_results['TotalGivenAmount'] = self.transactions.loc[
            (self.transactions['TransactionType'] == 3) & 
            (self.transactions['ReceiverDiscordId'] == self.user_id)
            , 'Amount'
            ].sum()
        
        return coin_results

    def get_challenge_results(self):
        """Get user statistics based on challenges activity."""
        if self.challenges.loc[
            (self.challenges['State'].isin([1, 2, 3]))
            , 'Wager'
            ].sum() == 0:
            return None
        
        challenge_results = {}
        
        challenge_results['TotalChallenges'] = self.challenges['State'].isin([1, 2, 3]).sum()

        challenge_results['TotalChallenger'] = (
            self.challenges['State'].isin([1, 2, 3]) &
            (self.challenges['ChallengerDiscordId'] == self.user_id)
        ).sum()

        challenge_results['TotalChallenged'] = (
            self.challenges['State'].isin([1, 2, 3]) &
            (self.challenges['ChallengedDiscordId'] == self.user_id)
        ).sum()

                   
        # Filter hands where user is involved and challenge is completed
        challenger_hands = self.challenges.loc[
            (self.challenges['State'].isin([1, 2, 3])) &
            (self.challenges['ChallengerDiscordId'] == self.user_id),
            'ChallengerHand'
        ]

        challenged_hands = self.challenges.loc[
            (self.challenges['State'].isin([1, 2, 3])) &
            (self.challenges['ChallengedDiscordId'] == self.user_id),
            'ChallengedHand'
        ]

        # Combine and count
        all_hands = pd.concat([challenger_hands, challenged_hands]).value_counts()

        max_count = all_hands.max()
        tied_hands = all_hands[all_hands == max_count].index.tolist()

        # Check for draws
        if len(tied_hands) != 1:
            challenge_results['FavouriteHand'] = None
        
        # Winning hand
        else:
            best_hand_id = tied_hands[0]
            challenge_results['FavouriteHand'] = CHALLENGE_HANDS[best_hand_id]
                
        return challenge_results

    def get_roulette_results(self):
        """Returns user statistics based on roulette activity."""
        if self.transactions.loc[
            (self.transactions['TransactionType'] == 4) &
            (self.transactions['SenderDiscordId'] == self.user_id)
            , 'Amount'
            ].sum() == 0:
            return None
        
        roulette_results = {}
        
        roulette_results['WagerCount'] = (
            (self.transactions['TransactionType'] == 4) &
            (self.transactions['BetTypeReward'].isna())
            ).sum()
        
        roulette_results['TotalWon'] = self.transactions.loc[
            (self.transactions['TransactionType'] == 4) &
            (self.transactions['SenderDiscordId'] == '0')
            , 'Amount'
            ].sum()
        
        roulette_results['BiggestWin'] = self.transactions.loc[
            (self.transactions['TransactionType'] == 4) &
            (self.transactions['SenderDiscordId'] == '0')
            , 'Amount'
            ].max()
        
        roulette_results['TotalLost'] = self.transactions.loc[
            (self.transactions['TransactionType'] == 4) &
            (self.transactions['BetTypeReward'].isna())
            , 'Amount'
        ].sum()
        
        roulette_results['BiggestLoss'] = self.transactions.loc[
            (self.transactions['TransactionType'] == 4) &
            (self.transactions['BetTypeReward'].isna())
            , 'Amount'
        ].max()
        
        games_counts = self.transactions.loc[
            (self.transactions['TransactionType'] == 4) &
            (self.transactions['ReceiverDiscordId'] != 0)
            , 'BetTypeWager'
        ].value_counts()
        
        max_count = games_counts.max()
        tied_games = games_counts[games_counts == max_count].index.tolist()

        if len(tied_games) != 1:
            roulette_results['FavouriteGame'] = None
        else:
            roulette_results['FavouriteGame'] = f'Guess{ROULETTE_TYPES[tied_games[0]]}'
            
        return roulette_results