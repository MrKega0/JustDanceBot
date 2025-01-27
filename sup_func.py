import datetime
import time

def escape_text(text:str):
    escape_symbols = '.,:()#-!?='
    for i in escape_symbols:
        text = text.replace(i,f'\\{i}')
    return text

def get_day():
    return datetime.datetime.now().date().isocalendar()[2]

if __name__ == '__main__':
    get_day()