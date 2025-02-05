import os

if os.getenv('DEBUG') == 'True':
    id_admin = [
        
        
    ]
else:
    id_admin = list(map(int, os.getenv('ADMINS_IDS').split(',')))


days = ['Понедельник','Вторник','Среда','Четверг','Пятница','Суббота','Воскресенье']