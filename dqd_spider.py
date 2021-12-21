import traceback
from typing import Dict
import requests
import time
import re
import random
import pymysql
import threading
import logging
from retrying import retry
from dbutils.pooled_db import PooledDB

from regex import REGEX_PERSON, REGEX_RANK, REGEX_RANK_TEAM, REGEX_TEAM
import db_config as cfg

DEBUG = True
ONLY_WATCH = False
SLEEP_TIME = 0.5    # second
logging.getLogger().setLevel(logging.INFO)

LEAGUE_MAP: Dict[int, str] = {
    1: "premier",
    2: "SerieA",
    3: "laliga",
    4: "Bundesliga",
    10: "FrenchLigue",
    # 231: "ChineseLeague"
}


head = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
                    AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/76.0.3809.132 Safari/537.36'
}

# f = open("./data.txt", "w", encoding='utf-8')


def _result(result):
    return result is None


@retry(stop_max_attempt_number=5, wait_random_min=1000, wait_random_max=2000, retry_on_result=_result)
def request_response(web_site: str):
    rp = requests.get(web_site, headers=head, timeout=5)
    return rp


class MySQLHelper:
   
    __pool = None

    def __init__(self) -> None:
        self._conn = MySQLHelper.__getconn()

    def get_cursor(self):
        return self._conn.cursor()

    @staticmethod
    def __getconn():
        if MySQLHelper.__pool is None:
            """
            :param mincached:连接池中空闲连接的初始数量
            :param maxcached:连接池中空闲连接的最大数量
            :param maxshared:共享连接的最大数量
            :param maxconnections:创建连接池的最大数量
            :param blocking:超过最大连接数量时候的表现，为True等待连接数量下降，为false直接报错处理
            :param maxusage:单个连接的最大重复使用次数
            :param setsession:optional list of SQL commands that may serve to prepare
                the session, e.g. ["set datestyle to ...", "set time zone ..."]
            :param reset:how connections should be reset when returned to the pool
                (False or None to rollback transcations started with begin(),
                True to always issue a rollback for safety's sake)
            :param host:数据库ip地址
            :param port:数据库端口
            :param db:库名
            :param user:用户名
            :param passwd:密码
            :param charset:字符编码
            """
            pool = PooledDB(
                creator=cfg.DB_CREATOR,
                mincached=cfg.DB_MIN_CACHED,
                maxcached=cfg.DB_MAX_CACHED,
                host=cfg.DB_HOST,
                port=cfg.DB_PORT,
                user=cfg.DB_USER,
                passwd=cfg.DB_PASSWORD,
                db=cfg.DB_DBNAME,
            )
            MySQLHelper.__pool = pool
        return MySQLHelper.__pool.connection()

    def create_database(self):
        cursor = self.get_cursor()
        try:
            cursor.execute("CREATE DATABASE IF NOT EXISTS dqd_data")
            self._conn.commit()
        except Exception as e:
            self._conn.rollback()
            logging.error("Mysql Error: ", e)
        finally:
            cursor.close()
            self._conn.close()

    def create_rank_table(self, table_name: str):
        cursor = self.get_cursor()
        sql = "CREATE TABLE IF NOT EXISTS {0} (" \
              "rank_num INT," \
              "team varchar(50)," \
              "game_num INT," \
              "win INT," \
              "draw INT," \
              "lose INT," \
              "win_goal INT," \
              "lose_goal INT," \
              "diff_goal INT," \
              "score INT" \
              ")".format(table_name)
        logging.info(sql)
        ret = cursor.execute(sql)
        if ret == 0:
            cursor.execute("TRUNCATE TABLE " + table_name)
        self._conn.commit()

    def create_team_table(self, table_name: str):
        cursor = self.get_cursor()
        sql = "CREATE TABLE IF NOT EXISTS {0} (" \
              "id INT," \
              "ch_name varchar(50)," \
              "en_name varchar(50)," \
              "country varchar(50)," \
              "city varchar(50)," \
              "stadium varchar(50)," \
              "max_fans INT," \
              "birth_year INT," \
              "address varchar(50)" \
              ")".format(table_name)
        logging.info(sql)
        ret = cursor.execute(sql)
        # ret == 0 means table already exists, clear the data which in table before
        if ret == 0:
            cursor.execute("TRUNCATE TABLE " + table_name)
        self._conn.commit()

    def create_player_table(self, table_name: str):
        cursor = self.get_cursor()
        sql = "CREATE TABLE IF NOT EXISTS {0} (" \
              "id INT," \
              "ch_name varchar(25)," \
              "en_name varchar(25)," \
              "club varchar(25)," \
              "nation varchar(25)," \
              "position varchar(25)," \
              "age INT," \
              "birthday DATE," \
              "number INT," \
              "weight INT," \
              "height INT" \
              ")".format(table_name)
        logging.info(sql)
        ret = cursor.execute(sql)
        if ret == 0:
            cursor.execute("TRUNCATE TABLE " + table_name)
        self._conn.commit()

    def insert_data(self, table_name: str, data_list: list):
        if ONLY_WATCH:
            return

        sql = ""
        if table_name.find("player") != -1:
            sql = "INSERT INTO {tb} VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(tb=table_name)
        elif table_name.find("team") != -1:
            sql = "INSERT INTO {tb} VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(tb=table_name)
        elif table_name.find("rank") != -1:
            sql = "INSERT INTO {tb} VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(tb=table_name)

        cursor = self.get_cursor()
        try:
            ret = cursor.execute(sql, tuple(data_list))
            self._conn.commit()
            logging.info("insert data {0} items successfully!".format(ret))
        except Exception as e:
            self._conn.rollback()
            logging.error("Mysql Error: ", e)
        finally:
            cursor.close()
            # self._conn.close()

    def close_conn(self):
        self._conn.close()


# player or coach class
class Person:
    def __init__(self, infos: list, person_id):
        self.chinese_name_ = infos[0]
        self.english_name_ = infos[1]
        self.club_ = infos[2]
        self.nation_ = infos[3]
        self.height_ = infos[4] if infos[4] != '' else 0
        self.position_ = infos[5]
        self.age_ = infos[6] if infos[6] != '' else 0
        self.weight_ = infos[7] if infos[7] != '' else 0
        self.number_ = infos[8] if infos[8] != '' else 0
        self.birthday_ = infos[9]
        self.dominant_foot_ = infos[10]
        self.photo_url_ = infos[11]
        self.person_id_ = person_id

    def to_string(self) -> str:
        return "{0}-{1}-{2}-{3}".format(self.chinese_name_, self.english_name_, self.age_, self.birthday_)

    def to_list(self) -> list:
        return [self.person_id_, self.chinese_name_, self.english_name_, self.club_,
                self.nation_, self.position_, self.age_, self.birthday_, self.number_, self.weight_, self.height_]


# football club team class
class Team:
    def __init__(self, infos: list, team_id, league_id) -> None:
        self.logo_url_ = infos[0]
        self.chinese_name_ = infos[1]
        self.english_name_ = infos[2]
        self.birth_year_ = infos[3] if infos[3] != '' else 0
        self.country_ = infos[4]
        self.city_ = infos[5]
        self.stadium_ = infos[6]
        self.max_fans_ = infos[7] if infos[7] != '' else 0
        self.telephone_ = infos[8]
        self.email_ = infos[9]
        self.address_ = infos[10]
        self.persons_ = []
        # team id in dqd
        self.id_ = team_id
        # league id where this team in, look LEAGUE_MAP
        self.league_id_ = league_id

        self.mysqlclient_ = MySQLHelper()

    def request_player_data(self):
        web_site = "https://www.dongqiudi.com/team/" + self.id_ + ".html"
        response = request_response(web_site)
        html_code = response.text
        person_id_list = re.findall('person_id:"(.*?)"', html_code)
        for person_id in person_id_list:
            person_url = "https://www.dongqiudi.com/player/" + person_id + ".html"
            person_html_code = request_response(person_url).text
            person_info_list = re.findall(REGEX_PERSON, person_html_code)
            if len(person_info_list) == 0 or len(person_info_list[0]) < 12:
                return
            person_obj = Person(person_info_list[0], person_id)

            self.mysqlclient_.insert_data(LEAGUE_MAP[self.league_id_] + "_player", person_obj.to_list())
            self.persons_.append(person_obj)
            logging.info(person_obj.to_string())
            # f.write(person_obj.to_string() + '\n')
            time.sleep(SLEEP_TIME)

    def to_string(self) -> str:
        return "{0}-{1}-{2}-{3}".format(self.chinese_name_, self.english_name_, self.city_, self.stadium_)

    def to_list(self) -> list:
        return [self.id_, self.chinese_name_, self.english_name_, self.country_, self.city_,
                self.stadium_, self.max_fans_, self.birth_year_, self.address_]


class Rank:
    def __init__(self, infos: list, rank) -> None:
        self.rank_num_ = rank
        self.chinese_name_ = infos[0]
        self.game_num_ = infos[1] if infos[1] != '' else 0
        self.win_ = infos[2] if infos[2] != '' else 0
        self.draw_ = infos[3] if infos[3] != '' else 0
        self.lose_ = infos[4] if infos[4] != '' else 0
        self.win_goal_ = infos[5] if infos[5] != '' else 0
        self.lose_goal_ = infos[6] if infos[6] != '' else 0
        self.diff_goal_ = infos[7] if infos[7] != '' else 0
        self.score_ = infos[8] if infos[8] != '' else 0

    def to_string(self) -> str:
        return "{0}-{1}-{2}".format(self.rank_num_, self.chinese_name_, self.score_)

    def to_list(self) -> list:
        return [self.rank_num_, self.chinese_name_, self.game_num_, self.win_, self.draw_,
                self.lose_, self.win_goal_, self.lose_goal_, self.diff_goal_, self.score_]


class League:
    def __init__(self, league_id: int) -> None:
        self.id_ = league_id
        self.teams_ = []
        self.rank_ = []
        self.mysqlclient_ = MySQLHelper()

    def request_team_data(self):
        # create the mysql table if it not exists, if already exists, clear the data before
        table_name = LEAGUE_MAP[self.id_] + "_team"
        self.mysqlclient_.create_team_table(table_name)
        self.mysqlclient_.create_player_table(LEAGUE_MAP[self.id_] + "_player")

        web_site = "https://www.dongqiudi.com/data/" + str(self.id_)
        response = request_response(web_site)
        html_code = response.text
        team_id_list = re.findall('team_id:"(.*?)"', html_code)
        for team_id in team_id_list:
            team_web_site = "https://www.dongqiudi.com/team/" + team_id + ".html"
            team_html_code = request_response(team_web_site).text
            team_info_list = re.findall(REGEX_TEAM, team_html_code)
            if len(team_info_list) == 0 or len(team_info_list[0]) < 11:
                print('team info error: ', team_info_list)
                return
            team_obj = Team(team_info_list[0], team_id, self.id_)
            logging.info(team_obj.to_string())
            self.mysqlclient_.insert_data(table_name, team_obj.to_list())
            # f.write(team_obj.to_string() + '\n')

            team_obj.request_player_data()
            self.teams_.append(team_obj)
            time.sleep(SLEEP_TIME)
        # self.mysqlclient_.close_conn()

    def request_rank_data(self):
        # create the mysql table if it not exists, if already exists, clear the data before
        table_name = LEAGUE_MAP[self.id_] + "_rank"
        self.mysqlclient_.create_rank_table(table_name)

        web_site = "https://www.dongqiudi.com/data/" + str(self.id_)
        response = request_response(web_site)
        html_code = response.text
        rank_html = re.findall(REGEX_RANK, html_code)
        if len(rank_html) == 0:
            print('rank info error: html code is empty')
            return
        else:
            rank_html = rank_html[0]

        rank_num = 1
        while True:
            rank_re = REGEX_RANK_TEAM.format(rank=rank_num)
            infos = re.findall(rank_re, rank_html)
            if len(infos) == 0:
                break
            else:
                rank_obj = Rank(infos[0], rank_num)
                print(rank_obj.to_string())
                self.mysqlclient_.insert_data(table_name, rank_obj.to_list())
            rank_num += 1


class LeagueThread(threading.Thread):
    def __init__(self, league: League):
        super().__init__()
        self.obj = league

    def run(self) -> None:
        self.obj.request_team_data()
        self.obj.request_rank_data()


class TeamThread(threading.Thread):
    def __init__(self, team: Team):
        super().__init__()
        self.obj = team

    def run(self) -> None:
        self.obj.request_player_data()


if __name__ == "__main__":
    start_time = time.time()
    thread_list = []
    for key, value in LEAGUE_MAP.items():
        league = League(key)
        t = LeagueThread(league)
        thread_list.append(t)
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()
    end_time = time.time()
    print('running time: ', end_time - start_time)
