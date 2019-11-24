import json
import psycopg2
import config

conn = psycopg2.connect(database=config.DATABASE, user=config.USER, password=config.PASSWORD, host=config.HOST, port=config.PORT)
cursor = conn.cursor()

def exec(query):
    print("{}".format(query))
    if True:
        try:
            cursor.execute(query)
            conn.commit()
            print("Success")
        except Exception as e:
            print("Unable to execute query: {0}".format(e))
            # logger.exception("Unable to execute query: {0}".format(query))
            conn.rollback()

def delete_pids(self, table):
    f = open("db.log", "a")
    for pid in pids:
        try:
            query = "DELETE FROM {} where pid = '{}'".format(table, pid)
            self.cursor.execute(query)
            f.write("Successfully deleted {} from {}".format(pid, table))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            f.write(str(e))
    f.close()

def insert_to_db(self, insert_query):
    try:
        self.cursor.execute(insert_query)
        self.conn.commit()
    except psycopg2.IntegrityError as e:
        pgcode = e.pgcode
        f = open("db.log", "a")
        if pgcode == "23505":
            f.write("postgres_error {}: insertion skipped (duplicate)\n".format(e.pgcode))
        else:
            f.write("postgres_error:{},insert_query={}\n".format(e.pgcode, insert_query))
        self.conn.rollback()
        f.close()
    except Exception as e:
        f = open("db.log", "a")
        f.write("postgres_error:{},insert_query={}\n".format(e, insert_query))
        self.conn.rollback()
        f.close()

def insert(self, stat, table):
    if table in ["team_shooting_stats", "team_stats", "team_stats_per_100"]:
        self.insert_nested_dict(stat, table)
    elif table in ["misc_stats", "standings", "pbp"]:
        self.insert_list(stat, table)
    elif table == "player_info":

        # this needs to be first as it the child tables have pid as a foreign key
        if "player_info" in stat:
            self.insert_dict(stat["player_info"], "player_info")
        # nested: stat = {"player_shooting_stats" : [], "player_info": {}...}
        for table_name in ["player_shooting_stats", "college_stats", "salaries"]:
            if table_name in stat:
                self.insert_list(stat[table_name], table_name)
        # if "player_info" in stat:
        #     self.insert_dict(stat["player_info"], "player_info")
        if "contracts" in stat and "pid" in stat["contracts"] and "team" in stat["contracts"]:
            columns, values = "", ""
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
            self.insert_dict(stat["contracts"], "contracts") # here
    elif table == "games":
        self.insert_list(stat, table)
    else:
        values += "{},".format(value)
    columns = columns[:-1]
    values = values[:-1]
    query = "INSERT INTO {}({}) VALUES ({});".format(table, columns, values)
    exec(query)

def insert_dict(self, dict, table):
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
    self.insert_to_db(query)

def insert_list(self, list, table):
    for dict in list:
        self.insert_dict(dict, table)

def insert_nested_dict(self, nested_dict, table):
    for index in nested_dict:
        self.insert_dict(nested_dict[index], table)

def insert(self, stat, table):
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
        elif "contracts" in stat and "pid" in stat["contracts"] and "team" in stat["contracts"]:
            columns, values = "", ""
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

"""
    def insert_jsons(self, stat):
        if stat in ["team_shooting_stats", "team_stats", "team_stats_per_100"]:
            if "per" in stat:
                f = open("./jsons/team_stats_per.json", "r")
            elif "team" in stat:
                f = open("./jsons/team_stats.json", "r")
            elif "shooting" in stat:
                f = open("./jsons/shooting_stats.json", "r")
            else:
                print("Error parsing {}".format(stat))
                return
            table = stat
            stats = json.loads(f.read())
            count = 0
            stat_dict = {}
            for s in stats:
                if count == 3:
                    break
                stat_dict[s] = stats[s]
                count += 1
            self.insert_nested_dict(stat_dict, table)
        elif any(k in stat for k in ["misc", "stand", "box", "pbp"]):
            if "misc" in stat:
                f = open("./jsons/miscellaneous_stats.json", "r")
                table = "miscellaneous_stats"
            elif "stand" in stat:
                f = open("./jsons/standings.json", "r")
                table = "standings"
            elif "box" in stat:
                f = open("./jsons/box_score.json", "r")
                table = "box_score"
            elif "pbp" in stat:
                f = open("./jsons/pbp.json", "r")
                table = "pbp"
            stats = json.loads(f.read())
            stats = stats[:3]
            self.insert_list(stats, table)
        elif "info" in stat:
            f = open("./jsons/player_stats.json", "r")
            stats = json.loads(f.read())
            for table in ["game_logs", "player_shooting_stats", "college_stats", "salaries"]:
                if table in stats:
                    self.insert_list(stats[table], table)
            if "player_info" in stats:
                self.insert_dict(stats["player_info"], "player_info")
            elif "contracts" in stats and "pid" in stats["contracts"] and "team" in stats["contracts"]:
                columns, values = "", ""
                for key in stats["contracts"].keys():
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
                print("{}\n".format(query))
        else:
            print("Error parsing {}".format(stat))
            return
        table = stat
        stats = json.loads(f.read())
        count = 0
        stat_dict = {}
        for s in stats:
            if count == 3:
                break
            stat_dict[s] = stats[s]
            count += 1
        insert_nested_dict(stat_dict, table)
    elif any(k in stat for k in ["misc", "stand", "box", "pbp"]):
        if "misc" in stat:
            f = open("./jsons/miscellaneous_stats.json", "r")
            table = "miscellaneous_stats"
        elif "stand" in stat:
            f = open("./jsons/standings.json", "r")
            table = "standings"
        elif "box" in stat:
            f = open("./jsons/box_score.json", "r")
            table = "box_score"
        elif "pbp" in stat:
            f = open("./jsons/pbp.json", "r")
            table = "pbp"
        stats = json.loads(f.read())
        stats = stats[:3]
        insert_list(stats, table)
    elif "info" in stat:
        f = open("./jsons/player_stats.json", "r")
        stats = json.loads(f.read())
        for table in ["game_logs", "player_shooting_stats", "college_stats", "salaries"]:
            if table in stats:
                insert_list(stats[table], table)
        if "player_info" in stats:
            insert_dict(stats["player_info"], "player_info")
        elif "contracts" in stats and "pid" in stats["contracts"] and "team" in stats["contracts"]:
            columns, values = "", ""
            for key in stats["contracts"].keys():
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
    else:
        print("Error reading {} file".format(stat))
"""