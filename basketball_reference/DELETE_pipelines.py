import psycopg2
import logging

# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class BasketballReferencePipeline(object):

    def open_spider(self, spider):
        database = "player_stats"
        user = "postgres"
        password = "postgres"
        host = "localhost"
        port = "5432"
        self.conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        self.cursor = self.conn.cursor()

        # logging setup, write everything
        self.logger = logging.getLogger(__name__)
        handler = logging.FileHandler('player_stats.log')
        handler.setLevel(logging.DEBUG)
        format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(format)
        self.logger.addHandler(handler)

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()
        self.logger.info("Closing connection")

    def process_item(self, item, spider):

        playerid = item["player_slug"]
        for game in item["games"]:
            game["playerid"] = playerid
            columns = ", ".join(game.keys())
            values = "{}".format(", ".join("'{}'".format(str(x)) for x in game.values()))
            insert_string = "INSERT INTO player_game_logs({}) VALUES ({});".format(columns, values)

            try:
                self.cursor.execute(insert_string)
                self.conn.commit()
            except Exception as e:
                self.logger.exception("Unable to execute query: {0} for {1} with columns {2}".format(insert_string, playerid, columns))
                self.conn.rollback()
                continue

        return item