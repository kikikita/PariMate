import datetime


pari_start = datetime.datetime.now().strftime("%d/%m/%y")
pari_end = (datetime.datetime.now() + datetime.timedelta(days=7))\
    .strftime("%d/%m/%y")

print(f'Начало: {pari_start} {pari_end}')
