from datetime import datetime, timedelta

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