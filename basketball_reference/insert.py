import psycopg2

database = "player_stats"
user = "postgres"
password = "postgres"
host = "localhost"
port = "5432"
conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
cursor = conn.cursor()

# game["playerid"] = playerid
# columns = ", ".join(game.keys())
# values = "{}".format(", ".join("'{}'".format(str(x)) for x in game.values()))
# insert_string = "INSERT INTO player_game_logs({}) VALUES ({});".format(columns, values)

try:
    cursor.execute(insert_string)
    conn.commit()
except Exception as e:
    logger.exception("Unable to execute query: {0} for {1} with columns {2}".format(insert_string, playerid, columns))
    conn.rollback()
    continue