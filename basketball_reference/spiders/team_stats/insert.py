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

def get():
    stats = []
    # these are lists
    # "miscellaneous_stats", "standings" 
    stat_keys = ["shooting_stats", "team_stats_per", "team_stats"]
    for stat_key in stat_keys:
        f = open("./{}.json".format(stat_key), "r")
        stat = json.loads(f.read())
        f.close()
        stats.append(stat)
    return stats

def list_compose(stats):
    columns, values = "", ""
    for stat in stats:
        for k in stat:
            columns += "{},".format(k)
            if k == "game_date":
                values += "todate({}, 'YYYYMMDD'),".format(stat[k])
            else:
                if isinstance(stat[k], str):
                    values += "'{}',".format(stat[k])
                else:
                    values += str(stat[k]) + ','

    columns = columns[:-1]
    values = values[:-1]

    return columns, values

def nested_dict_compose(player):
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