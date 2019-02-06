import json
# import psycopg2

# database = "player_stats"
# user = "postgres"
# password = "postgres"
# host = "localhost"
# port = "5432"
# conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
# cursor = conn.cursor()

# game["playerid"] = playerid
# columns = ", ".join(game.keys())
# values = "{}".format(", ".join("'{}'".format(str(x)) for x in game.values()))
# insert_string = "INSERT INTO player_game_logs({}) VALUES ({});".format(columns, values)

# try:
#     cursor.execute(insert_string)
#     conn.commit()
# except Exception as e:
#     logger.exception("Unable to execute query: {0} for {1} with columns {2}".format(insert_string, playerid, columns))
#     conn.rollback()
#     continue

def insert_dict(dict, table):
    columns = ""
    values = ""
    for key in dict:
        columns += "{},".format(key)
        value = dict[key]
        if isinstance(value, str):
            if key == "collected_date":
                values += "TO_DATE('{}','YYYYMMDD'),".format(value)
            else:
                values += "'{}',".format(value)
        else:
            values += "{},".format(value)
    columns = columns[:-1]
    values = values[:-1]
    query = "INSERT INTO {}({}) VALUES ({});".format(table, columns, values)
    print("{}\n".format(query))

def insert_list(list, table):
    for dict in list:
        insert_dict(dict, table)

def insert_nested_dict(nested_dict, table):
    for index in nested_dict:
        insert_dict(nested_dict[index], table)

# AUXILIARY FUNCTIONS
def get_shooting():
    f = open("./shooting_stats.json", "r")
    ss = json.loads(f.read())
    count = 0
    shooting = {}
    for s in ss:
        if count == 3:
            break
        shooting[s] = ss[s]
        count += 1
    return shooting

def get_standings():
    f = open("./standings.json", "r")
    standings = json.loads(f.read())
    standings = standings[:3]
    return standings

def get_misc():
    f = open("./miscellaneous_stats.json", "r")
    misc = json.loads(f.read())
    misc = misc[:3]
    return misc