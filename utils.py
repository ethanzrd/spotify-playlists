import datetime as dt


def generate_date(date):
    year, month, day = date.split('-')
    months = [(str(i) if len(str(i)) > 1 else f'0{i}', dt.date(2008, i, 1).strftime('%B')) for i in range(1, 13)]
    current_month = [listed_month for listed_month in months if month == listed_month[0]][0][1]
    return f'{current_month} {day}, {year}'
