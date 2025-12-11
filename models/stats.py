import requests
import pandas as pd
import datetime as dt
from utils.helpers import fetch_months
from utils.enums import *

class UserStats:
    def __init__(self, user_id):
        self.user_id = user_id
        self.transactions = []
        self.challenges = []
        self.account = []
        
        transactions = requests.get('http://localhost:8080/api/transactions').json()
        challenges = requests.get('http://localhost:8080/api/challenges').json()
        roulettes = requests.get('http://localhost:8080/api/roulette').json()
        accounts = requests.get('http://localhost:8080/api/accounts').json()
        
        # User filtering
        account = [acc for acc in accounts if acc['DiscordId'] == self.user_id]
        self.account = pd.DataFrame(account)
        
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
            'RewardTransactionId': 'Reward',
            'BetNumber': 'BetNumberWager',
            'RolledNumber': 'RolledNumberWager',
            'BetType': 'BetTypeWager'
        })[['Id', 'Reward', 'BetNumberWager', 'RolledNumberWager', 'BetTypeWager']]
        
        # Transactions final merge
        self.transactions = (
            transactions
            .merge(roulette_wagers, on='Id', how='left')
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
            
        self.account['LastClaimDate'] = pd.to_datetime(
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
        
        # Calculate challenge statistics
        challenge_results['TotalChallenges'] = self.challenges['State'].isin([1, 2, 3]).sum()

        challenge_results['TotalChallenger'] = (
            (self.challenges['ChallengerDiscordId'] == self.user_id) &
            (self.challenges['ChallengedDiscordId'] != '0')
        ).sum()

        challenge_results['TotalChallenged'] = (
            self.challenges['ChallengedDiscordId'] == self.user_id
        ).sum()

        # Win/Loss Ratio
        challenge_wins = (
            ((self.challenges['State'] == 1) &
            (self.challenges['ChallengerDiscordId'] == self.user_id)).sum()
            +
            ((self.challenges['State'] == 2) &
            (self.challenges['ChallengedDiscordId'] == self.user_id)).sum()
        )

        challenge_losses = (
            ((self.challenges['State'] == 1) &
            (self.challenges['ChallengedDiscordId'] == self.user_id)).sum()
            +
            ((self.challenges['State'] == 2) &
            (self.challenges['ChallengerDiscordId'] == self.user_id)).sum()
        )

        challenge_results['WinLossRatio'] = round((challenge_wins / challenge_losses), 1) if challenge_losses > 0 else None

                   
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
            (self.transactions['SenderDiscordId'] == self.user_id)
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
            (self.transactions['SenderDiscordId'] == self.user_id) &
            (self.transactions['Reward'].isna())
            , 'Amount'
        ].sum()
        
        roulette_results['BiggestLoss'] = self.transactions.loc[
            (self.transactions['TransactionType'] == 4) &
            (self.transactions['SenderDiscordId'] == self.user_id) &
            (self.transactions['Reward'].isna())
            , 'Amount'
        ].max()
        
        # Win/Loss Ratio
        roulette_wins = (
            ((self.transactions['TransactionType'] == 4) &
            (self.transactions['SenderDiscordId'] == '0')).sum()
        )
        
        roulette_losses = (
            ((self.transactions['TransactionType'] == 4) &
            (self.transactions['SenderDiscordId'] == self.user_id) &
            (self.transactions['Reward'].isna())).sum()
        )

        roulette_results['WinLossRatio'] = round((roulette_wins / roulette_losses), 1) if roulette_losses > 0 else None

        # Favourite game
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
    
    # def get_l7d_balances(self):
    #     """Returns user balance in the last 7 days."""
        
    #     today = dt.date.today()
    #     start_date = today - dt.timedelta(days=7)
        
    #     # Convert to pandas Timestamps
    #     start_date_ts = pd.Timestamp(start_date).tz_localize('UTC')
    #     today_ts = pd.Timestamp(today).tz_localize('UTC')

    #     # Filter transactions for the last 7 days
    #     transactions_l7d = self.transactions.loc[
    #         (self.transactions['Date'] >= start_date_ts) &
    #         (self.transactions['Date'] <  today_ts + pd.Timedelta(days=1))
    #     ]
        
    #     current_balance = int(self.account['Balance'].iloc[0])
        
    #     # Initialise loop
    #     running_balance = current_balance
        
    #     l7d_balances = {}
        
    #     for i in range(7):
    #         # Create date row
    #         date = today - dt.timedelta(days=i)
    #         l7d_balances[date] = {'start_balance' : 0, 'end_balance' : 0}
            
    #         prev_date = date + dt.timedelta(days=1)

    #         # End balance of day
    #         if prev_date in l7d_balances:
    #             l7d_balances[date]['end_balance'] = l7d_balances[prev_date]['start_balance']
    #         else:
    #             l7d_balances[date]['end_balance'] = current_balance
                
    #         # Claim add
    #         coins_claimed = transactions_l7d.loc[
    #             (transactions_l7d['Date'].dt.date == date) &
    #             (transactions_l7d['TransactionType'].isin([0, 1])),
    #             'Amount'
    #             ].sum()
            
    #         coins_given = transactions_l7d.loc[
    #             (transactions_l7d['Date'].dt.date == date) &
    #             (transactions_l7d['TransactionType'] == 3) &
    #             (transactions_l7d['SenderDiscordId'] == self.user_id),
    #             'Amount'
    #             ].sum()
            
    #         coins_received = transactions_l7d.loc[
    #             (transactions_l7d['Date'].dt.date == date) &
    #             (transactions_l7d['TransactionType'] == 3) &
    #             (transactions_l7d['ReceiverDiscordId'] == self.user_id),
    #             'Amount'
    #             ].sum()
                        
    #         # Challenge add/decrease
    #         challenges_won = transactions_l7d.loc[
    #             (transactions_l7d['Date'].dt.date == date) &
    #             (transactions_l7d['TransactionType'] == 2) & 
    #             (transactions_l7d['ReceiverDiscordId'] == self.user_id),
    #             'Amount'
    #             ].sum()
            
    #         challenges_lost = transactions_l7d.loc[
    #             (transactions_l7d['Date'].dt.date == date) &
    #             (transactions_l7d['TransactionType'] == 2) & 
    #             (transactions_l7d['SenderDiscordId'] == self.user_id),
    #             'Amount'
    #             ].sum()
            
    #         # Roulette add/decrease
    #         roulettes_won = transactions_l7d.loc[
    #             (transactions_l7d['Date'].dt.date == date) &
    #             (transactions_l7d['TransactionType'] == 4) & 
    #             (transactions_l7d['SenderDiscordId'] == '0'),
    #             'Amount'
    #             ].sum()
            
    #         roulettes_lost = transactions_l7d.loc[
    #             (transactions_l7d['Date'].dt.date == date) &
    #             (transactions_l7d['TransactionType'] == 4) & 
    #             (transactions_l7d['SenderDiscordId'] == self.user_id) &
    #             (transactions_l7d['Reward'].isna()),
    #             'Amount'
    #             ].sum()
            
    #         # Calculate start day balance
    #         l7d_balances[date]['start_balance'] = (
    #             l7d_balances[date]['end_balance']
    #             - coins_claimed
    #             - coins_received
    #             + coins_given
    #             - challenges_won
    #             + challenges_lost
    #             - roulettes_won
    #             + roulettes_lost
    #         )
            
    #     print(l7d_balances)
    #     return l7d_balances