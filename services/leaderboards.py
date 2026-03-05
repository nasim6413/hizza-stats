import pandas as pd
from services.data import *

def get_top_streaks():
    accounts = get_accounts()

    # Drop Hizza account
    accounts = accounts.drop(accounts[accounts['DiscordId'] == "0"].index) 
    
    accounts = accounts.sort_values(by='Streak', ascending=False)
    
    today = pd.Timestamp.utcnow().normalize()
    accounts['days_since_claim'] = (today - accounts['LastClaimDate']).dt.days
    
    # Get total number of users with a streak
    streakers = (
        (accounts['Streak'] > 0) &
        (accounts['days_since_claim'] <= 2)
        ).sum()
    
    accounts = accounts.iloc[:5] # Retrieves top 5
    
    data = {
        'streakers' : streakers,
        'users' : [],
        'streak_num' : [],
        'claim_status' : []
    }
    
    for i, row in accounts.iterrows():
        data['users'].append(row['DiscordId'])
        data['streak_num'].append(str(row['Streak']))
        
        if row['days_since_claim'] == 0:
            data['claim_status'].append(1)
        elif row['days_since_claim'] in [1, 2]:
            data['claim_status'].append(2)
        elif row['days_since_claim'] > 2:
            data['claim_status'].append(3)
            
    return data

def get_top_challenges():
    challenges = get_challenges()
    
    # Normalise dataset
    challenges = pd.concat([
            challenges.rename(columns={
                "Id": "ChallengeId",
                "ChallengerDiscordId": "DiscordId",
                "ChallengedDiscordId": "OpponentDiscordId",
                "ChallengerHand": "Hand",
                "ChallengedHand": "OpponentHand"
            }).assign(Role="Challenger"),
            
            challenges.rename(columns={
                "Id": "ChallengeId",
                "ChallengedDiscordId": "DiscordId",
                "ChallengerDiscordId": "OpponentDiscordId",
                "ChallengedHand": "Hand",
                "ChallengerHand": "OpponentHand"
            }).assign(Role="Challenged")
        ], ignore_index=True)
    
    # Win / Loss flags
    challenges["Win"] = (
        ((challenges["Role"] == "Challenger") & (challenges["State"] == 1)) |
        ((challenges["Role"] == "Challenged") & (challenges["State"] == 2))
    )

    challenges["Loss"] = (
        ((challenges["Role"] == "Challenger") & (challenges["State"] == 2)) |
        ((challenges["Role"] == "Challenged") & (challenges["State"] == 1))
    )

    # Best hand per user (from winning rounds)
    best_hands = (
        challenges[challenges["Win"]]
        .groupby(["DiscordId", "Hand"])
        .size()
        .reset_index(name="Count")
        .sort_values(["DiscordId", "Count"], ascending=[True, False])
        .drop_duplicates("DiscordId")
        .set_index("DiscordId")["Hand"]
    )
    
    # Total coins won
    coin_won = (
        challenges[challenges["Win"]]
        .groupby("DiscordId")["Wager"]
        .sum()
    )

    # Leaderboard
    main = (
        challenges.groupby("DiscordId")
        .agg(
            Wins=("Win", "sum"),
            Losses=("Loss", "sum")
        )
        .join(best_hands.rename("BestHand"))
        .join(coin_won.rename("CoinsWon"))
        .sort_values("Wins", ascending=False)
        .head(5) #Top 5
        .reset_index()
    )

    data = {
        "users": main["DiscordId"].tolist(),
        "win_num": main["Wins"].tolist(),
        "loss_num": main["Losses"].tolist(),
        "coin_won": main["CoinsWon"].tolist(),
        "best_hand": main["BestHand"].tolist()
    }
    
    return data

def get_in_danger():
    accounts = get_accounts()

    # Drop Hizza account
    accounts = accounts.drop(accounts[accounts['DiscordId'] == "0"].index) 

    accounts = accounts.sort_values(by='Streak', ascending=False)
    
    today = pd.Timestamp.utcnow().normalize()
    accounts['days_since_claim'] = (today - accounts['LastClaimDate']).dt.days
    
    data = {
        'users' : [],
        'streak_num' : []
    }
    
    for i, row in accounts.iterrows():
        if row['days_since_claim'] in [1, 2] and row['Streak'] > 30:
            data['users'].append(row['DiscordId'])
            data['streak_num'].append(str(row['Streak']))
            
    return data