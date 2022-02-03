from datetime import datetime, timedelta

def get_day_month_year():
    yesterday = datetime.now() - timedelta(1)
    day, month, year = yesterday.day, yesterday.month, str(yesterday.year)

    month = str(month) if month >= 10 else "0{}".format(month)
    day = str(day) if day >= 10 else "0{}".format(day)
    return day, month, year

def get_list_of_formatted_dates(start_date, end_date):
    delta = end_date - start_date
    dates = [start_date + timedelta(days=i) for i in range(delta.days + 1)]
    formatted_dates = []
    for date in dates:
        day, month, year = date.day, date.month, str(date.year)
        month = str(month) if month >= 10 else "0{}".format(month)
        day = str(day) if day >= 10 else "0{}".format(day)
        formatted_dates.append("{0}{1}{2}".format(year, month, day))
    return formatted_dates

def format_date(date):
    day, month, year = date.day, date.month, str(date.year)
    month = str(month) if month >= 10 else "0{}".format(month)
    day = str(day) if day >= 10 else "0{}".format(day)
    return "{}{}{}".format(year, month, day)
