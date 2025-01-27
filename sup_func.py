import datetime
import time

def escape_text(text:str):
    escape_symbols = '.,:()#-!?='
    for i in escape_symbols:
        text = text.replace(i,f'\\{i}')
    return text

def get_day():
    return datetime.datetime.now().date().isocalendar()[2]

def day_to_date(day_of_week: int):
    # Текущая дата
    today = datetime.date.today()
    # Номер дня недели (понедельник = 1, воскресенье = 7)
    current_weekday = today.isoweekday()
    # Смещение для получения желаемой даты
    delta = day_of_week - current_weekday
    # Вычисляем дату
    desired_date = today + datetime.timedelta(days=delta)
    sql_date = desired_date.strftime("%Y-%m-%d")
    return sql_date

if __name__ == '__main__':
    print(get_day())

    