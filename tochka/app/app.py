from flask import Flask, request, jsonify
import  sqlite3, time, threading
from multiprocessing import Process
app = Flask(__name__)
_Uuid = 0
_FIO = 1
_balance = 2
_hold = 3
_status = 4
database = "db_clients.sqlite"



@app.route('/api/ping')
def ping():
    return get_json(200, True, "", "Server is stable."), 200


@app.route('/api/add')
def add():

    args = request.get_json()
    if not args or not "Uuid" in args or not "value" in args:
        return get_json_wrong_args()
    conn, cursor = get_db()
    person = find_person(args['Uuid'], cursor)
    if not person:
        return get_json_not_person(args["Uuid"])
    if person[_status] <= 0:
        return get_json_close_status(args["Uuid"])
    cursor.execute('update clients set Баланс={0} where Uuid="{1}"'.format(person[_balance] + args["value"], args["Uuid"]))
    person = find_person(args['Uuid'], cursor)
    conn.commit()

    return get_json(200, True, {"Uuid": person[_Uuid], "Balance": person[_balance]}, "Successful."), 200

@app.route('/api/status')
def status():
    args = request.get_json()
    if not args or not "Uuid" in args :
        return get_json_wrong_args()
    cursor = get_db()[1]
    person = find_person(args['Uuid'], cursor)
    if not person:
        return get_json_not_person(args["Uuid"])

    return get_json(200, True, {"Balance": person[_balance], "Hold": person[_hold],
                                "Status": "Open" if person[_status] > 0 else "Close"},
                    "Successful"), 200

@app.route('/api/substract')
def substract():
    args = request.get_json()
    if not args or not "Uuid" in args or not "substraction" in args:
        return get_json_wrong_args()
    conn, cursor = get_db()
    person = find_person(args['Uuid'], cursor)
    if not person:
        return get_json_not_person(args["Uuid"])

    if person[_status] <= 0:
        return get_json_close_status(args["Uuid"])

    result = person[_balance] - person[_hold] - args["substraction"]
    if result < 0:
        return get_json(200, False, {"Uuid": person[_Uuid], "Balance": person[_balance]}, "substraction is impossible")

    if not person:
        return get_json_not_person(args["Uuid"])
    cursor.execute(
        'update clients set Холд={0} where Uuid="{1}"'.format(person[_hold] + args["substraction"], args["Uuid"]))
    conn.commit()

    return get_json(200, True, {"Uuid": person[_Uuid], "Hold": person[_hold]}, "substraction is complete."), 200

def get_db():
    conn = sqlite3.connect(database)
    return  conn, conn.cursor()

def find_person(Uuid, cursor):
    person = cursor.execute('select * from clients where Uuid="{}"'.format(Uuid)).fetchall()
    if person:
        return person[0]

def get_json(status, result, addition, description):
    return  jsonify({"status": status, "result": result, "addition": addition, "description": description})

def get_json_not_person(Uuid):
    return get_json(404, False, "Uuid: {}".format(Uuid), "Person not founded.")

def get_json_wrong_args():
    return get_json(400, False, "", "Wrong arguments.")

def get_json_close_status(Uuid):
    return get_json(400, False, "Uuid: {}".format(Uuid), "Status is close.")

def update():
    while True:
        time.sleep(15)
        print("update")
        conn, cursor = get_db()
        persons = cursor.execute('select * from clients')
        for person in persons:
            cursor.execute(
                'update clients set Баланс={0} where Uuid="{1}"'.format(person[_balance] - person[_hold], person[_Uuid]))
            cursor.execute(
                'update clients set Холд={0} where Uuid="{1}"'.format(0, person[_Uuid]))
        conn.commit()


if __name__ == '__main__':
    print("start")
    p = Process(target=update, args=tuple())
    p.start()
    app.run('0.0.0.0', debug=True, use_reloader=False)
    p.join()