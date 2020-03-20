import  sqlite3, time

_Uuid = 0
_FIO = 1
_balance = 2
_hold = 3
_status = 4
database = "db_clients.sqlite"

def get_db():
    conn = sqlite3.connect(database)
    return  conn, conn.cursor()

def update():
    conn, cursor = get_db()
    persons = cursor.execute('select * from clients')
    for person in persons:
        cursor.execute(
            'update clients set Баланс={0} where Uuid="{1}"'.format(person[_balance] - person[_hold], person[_Uuid]))
        cursor.execute(
            'update clients set Холд={0} where Uuid="{1}"'.format(0, person[_Uuid]))
    conn.commit()

if __name__ == '__main__':
    while True:
        print("*")
        time.sleep(10)

        update()