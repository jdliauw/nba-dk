import json
import psycopg2

"""
database = "player_stats"
user = "postgres"
password = "postgres"
host = "localhost"
port = "5432"
conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
cursor = conn.cursor()

f = open("./spiders/box_score/BOS_CLE_box_score.json", "r")
players = json.load(f)

for player in players:
    columns, values = compose(player)

    insert_string = "INSERT INTO player_game_logs({}) VALUES ({});".format(columns, values)

    try:
        cursor.execute(insert_string)
        conn.commit()
    except Exception as e:
        print("Unable to execute query: {}".format(insert_string))
        conn.rollback()
        continue
"""

def compose(player):
    columns, values = "", ""
    for k in player:
        columns += "{},".format(k)
        if k == "game_date":
            values += "todate({}, 'YYYYMMDD'),".format(player[k])
        else:
            if isinstance(player[k], str):
                values += "'{}',".format(player[k])
            else:
                values += str(player[k]) + ','

    columns = columns[:-1]
    values = values[:-1]

    return columns, values