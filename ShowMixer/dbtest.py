def db_to_int( db ):
    db_f = float( db )
    if db < -60:
        value = (db + 90) / 480
    elif db < -30:
        value = (db + 70) / 160
    elif db < -10:
        value = (db + 50) / 80
    elif db <= 10:
        value = (db + 30) / 40
    return value * 1023


db_val_list = [10, 5, 0, -5, -10, -20, -30, -40, -50, -60]
for val in db_val_list:
    print(db_to_int(val))