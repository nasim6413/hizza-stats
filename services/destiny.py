from datetime import datetime, timedelta

def get_destiny(date = False):
    if not date:
        date = datetime.now()
    
    seed = date.day + date.month - 1

    if (seed % 3 == 0) or (seed % 5 == 0): # big destiny
        return 3
    
    if (seed % 17) == 0: # insane destiny
        return 5
    
    if (seed % 4 == 0) or (seed % 7 == 0) : # somewhat destiny
        return 2
    
    if (seed % 2 == 1):  # very big destiny
        return 4
    
    else: # small destiny
        return 1

def next_insane_destiny():
    today = datetime.now()
    current = today

    while True:
        if (current.day + current.month - 1) % 17 == 0:
            delta = current - today
            days_left = delta.days
            
            data = {
                'day' : current.day,
                'month' : current.strftime("%b"),
                'year' : current.year,
                'days_left' : days_left
            }
            return data

        current += timedelta(days=1)
        
def tomorrow_destiny():
    return get_destiny(datetime.now() + timedelta(days=1))
