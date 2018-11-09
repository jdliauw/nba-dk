# import ast
# import psycopg2
import sqlalchemy
import pandas as pd

def main():
    conn = None

    # sqlalchemy
    try:
        url = 'postgresql://postgres:postgres@127.0.0.1:5432/player_stats'

        # create the engine
        # engine: manages connection pool and dbapi (low level python api for database, ex: psycopg2 for postgres)
        conn = sqlalchemy.create_engine(url, client_encoding='utf8')
        meta = sqlalchemy.MetaData(bind=conn,reflect=True)
        results = meta.tables['player_game_logs']
        clause = results.select().where(results.c.playerid == 'tatumja01')
        # for row in conn.execute(clause):
            # print(row)
        df = pd.read_sql(clause, conn)

    except:
        pass

    # psycopg2
    # try:
    #     conn = psycopg2.connect(database="player_stats", user="postgres", password="postgres", host="localhost", port="5432")
    #     cursor = conn.cursor()
    #     cursor.execute("select * from player_game_logs where playerid = 'tatumja01';")
    #     data = cursor.fetchall()
    #     print(data)
    #     f = open("tatum.txt", "w")
    #     f.write(str(data))
    #     f.close()
    #     conn.close()
    # except:
    #     pass

    # alternative read
    # f = open("tatum.txt", "r")
    # data = f.read()
    # f.close()
    # data = ast.literal_eval(data)


if __name__ == "__main__":
    main()
