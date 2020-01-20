import json
import psycopg2
import config

conn = psycopg2.connect(database=config.DATABASE, user=config.USER, password=config.PASSWORD, host=config.HOST, port=config.PORT)
cursor = conn.cursor()

def exec(query):
    if True:
        try:
            cursor.execute(query)
            conn.commit()
        except Exception as e:
            print("Unable to execute query: {0}".format(e))
            # logger.exception("Unable to execute query: {0}".format(query))
            conn.rollback()

def delete_pids(table):
    f = open("db.log", "a")
    for pid in pids:
        try:
            query = "DELETE FROM {} where pid = '{}'".format(table, pid)
            cursor.execute(query)
            f.write("Successfully deleted {} from {}".format(pid, table))
            conn.commit()
        except Exception as e:
            conn.rollback()
            f.write(str(e))
    f.close()

def insert_to_db(insert_query):
    try:
        cursor.execute(insert_query)
        conn.commit()
    except psycopg2.IntegrityError as e:
        pgcode = e.pgcode
        f = open("db.log", "a")
        if pgcode == "23505":
            f.write("postgres_error {}: insertion skipped (duplicate)\n".format(e.pgcode))
        else:
            f.write("postgres_error:{},insert_query={}\n".format(e.pgcode, insert_query))
        conn.rollback()
        f.close()
    except Exception as e:
        f = open("db.log", "a")
        f.write("postgres_error:{},insert_query={}\n".format(e, insert_query))
        conn.rollback()
        f.close()

def insert(stat, table):
    if table in ["team_shooting_stats", "team_stats", "team_stats_per_100"]:
        insert_nested_dict(stat, table)
    elif table in ["miscellaneous_stats", "standings", "pbp"]:
        insert_list(stat, table)
    elif table == "player_info":
        # nested: stat = {"player_shooting_stats" : [], "player_info": {}...}
        for table_name in ["player_shooting_stats", "college_stats", "salaries"]:
            if table_name in stat:
                insert_list(stat[table_name], table_name)
        if "player_info" in stat:
            insert_dict(stat["player_info"], "player_info")
        if "contracts" in stat and "pid" in stat["contracts"] and "team" in stat["contracts"]:
            columns = "{},{},".format("pid","team")
            values  = "'{}','{}',".format(stat["contracts"]["pid"], stat["contracts"]["team"])
            for key in stat["contracts"].keys():
                if key not in ["pid", "team"]:
                    value = stat["contracts"][key]
                    columns += "{},".format(key)
                    if isinstance(value, str):
                        values += "'{}',".format(value)
                    else:
                        values += "{},".format(value)
            columns = columns[:-1]
            values = values[:-1]
            query = "INSERT INTO {}({}) VALUES ({});".format("contracts", columns, values)
            exec(query)
    elif table == "games":
        insert_list(stat, table)
    else:
        print("Error reading {} file".format(stat))

def insert_dict(dict, table):
    columns = ""
    values = ""
    for key in dict:
        columns += "{},".format(key)
        value = dict[key]
        if isinstance(value, str):
            if key in ["collected_date", "game_date"]:
                values += "TO_DATE('{}','YYYYMMDD'),".format(value)
            else:
                values += "'{}',".format(value)
        else:
            values += "{},".format(value)
    columns = columns[:-1]
    values = values[:-1]
    query = "INSERT INTO {}({}) VALUES ({});".format(table, columns, values)
    insert_to_db(query)

def insert_list(list, table):
    for dict in list:
        insert_dict(dict, table)

def insert_nested_dict(nested_dict, table):
    for index in nested_dict:
        insert_dict(nested_dict[index], table)