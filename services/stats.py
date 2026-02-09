import pandas as pd
from utils.enums import *
from services.data import *

def get_coin_results(user_id):
    """Get user statistics based on coin activity."""
    
    transactions = get_transactions(user_id)
    
    # Getting coin results
    coin_results = {} 
    
    coin_results['TotalClaims'] = (
        (transactions['TransactionType'] == 1)
        ).sum()
    
    coin_results['TotalClaimed'] = transactions.loc[
        transactions['TransactionType'] == 1, 'Amount'
        ].sum()
    
    coin_results['AverageClaim'] = round(transactions.loc[
        transactions['TransactionType'] == 1, 'Amount'
        ].mean())
    
    coin_results['BestClaim'] = transactions.loc[
        transactions['TransactionType'] == 1, 'Amount'
        ].max()
    
    coin_results['TotalGiveAmount'] = transactions.loc[
        (transactions['TransactionType'] == 3) & 
        (transactions['SenderDiscordId'] == user_id)
        , 'Amount'
        ].sum()
    
    coin_results['TotalGivenAmount'] = transactions.loc[
        (transactions['TransactionType'] == 3) & 
        (transactions['ReceiverDiscordId'] == user_id)
        , 'Amount'
        ].sum()
    
    return coin_results

def get_challenge_results(user_id):
    """Get user statistics based on challenges activity."""
    
    # Import data and converting to pd
    challenges = get_challenges(user_id)
    
    challenge_results = {}
    
    # Calculate challenge statistics
    challenge_results['TotalChallenges'] = challenges['State'].isin([1, 2, 3]).sum()

    challenge_results['TotalChallenger'] = (
        (challenges['ChallengerDiscordId'] == user_id) &
        (challenges['ChallengedDiscordId'] != '0')
    ).sum()

    challenge_results['TotalChallenged'] = (
        challenges['ChallengedDiscordId'] == user_id
    ).sum()

    # Win/Loss Ratio
    challenge_wins = (
        ((challenges['State'] == 1) &
        (challenges['ChallengerDiscordId'] == user_id)).sum()
        +
        ((challenges['State'] == 2) &
        (challenges['ChallengedDiscordId'] == user_id)).sum()
    )

    challenge_losses = (
        ((challenges['State'] == 1) &
        (challenges['ChallengedDiscordId'] == user_id)).sum()
        +
        ((challenges['State'] == 2) &
        (challenges['ChallengerDiscordId'] == user_id)).sum()
    )

    challenge_results['WinLossRatio'] = round((challenge_wins / challenge_losses), 1) if challenge_losses > 0 else None

                
    # Filter hands where user is involved and challenge is completed
    challenger_hands = challenges.loc[
        (challenges['State'].isin([1, 2, 3])) &
        (challenges['ChallengerDiscordId'] == user_id),
        'ChallengerHand'
    ]

    challenged_hands = challenges.loc[
        (challenges['State'].isin([1, 2, 3])) &
        (challenges['ChallengedDiscordId'] == user_id),
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

def get_roulette_results(user_id):
    """Returns user statistics based on roulette activity."""
    
    transactions = get_roulettes(user_id)

    roulette_results = {}

    roulette_results['WagerCount'] = (
        (transactions['TransactionType'] == 4) &
        (transactions['SenderDiscordId'] == user_id)
        ).sum()

    roulette_biggest_reward_id = transactions.loc[
        (transactions['TransactionType'] == 4) &
        (transactions['SenderDiscordId'] == '0')
        , 'Id'
        ].max()
    
    roulette_results['BiggestWin'] = transactions.loc[
        (transactions['TransactionType'] == 4) &
        (transactions['SenderDiscordId'] == '0')
        , 'Amount'
        ].max()

    roulette_results['TotalLost'] = transactions.loc[
        (transactions['TransactionType'] == 4) &
        (transactions['SenderDiscordId'] == user_id) &
        (transactions['Reward'].isna())
        , 'Amount'
    ].sum()

    roulette_results['BiggestLoss'] = transactions.loc[
        (transactions['TransactionType'] == 4) &
        (transactions['SenderDiscordId'] == user_id) &
        (transactions['Reward'].isna())
        , 'Amount'
    ].max()
    
    # Total won = total received by Hizza - total wagered
    roulette_results['TotalWon'] = transactions.loc[
        (transactions['TransactionType'] == 4) &
        (transactions['SenderDiscordId'] == '0')
        , 'Amount'
        ].sum() - transactions.loc[
            (transactions['TransactionType'] == 4) &
            (transactions['SenderDiscordId'] == user_id) &
            (transactions['Reward'].notna())
            , 'Amount'
        ].sum()

    # Win/Loss Ratio
    roulette_wins = (
        ((transactions['TransactionType'] == 4) &
        (transactions['SenderDiscordId'] == '0')).sum()
    )

    roulette_losses = (
        ((transactions['TransactionType'] == 4) &
        (transactions['SenderDiscordId'] == user_id) &
        (transactions['Reward'].isna())).sum()
    )

    roulette_results['WinLossRatio'] = round((roulette_wins / roulette_losses), 1) if roulette_losses > 0 else None

    # Favourite game
    games_counts = transactions.loc[
        (transactions['TransactionType'] == 4) &
        (transactions['ReceiverDiscordId'] != 0)
        , 'BetTypeWager'
    ].value_counts()

    max_count = games_counts.max()
    tied_games = games_counts[games_counts == max_count].index.tolist()

    if len(tied_games) != 1:
        roulette_results['FavouriteGame'] = None
    else:
        roulette_results['FavouriteGame'] = f'Guess{ROULETTE_TYPES[tied_games[0]]}'
        
    return roulette_results