import traceback
from typing import Dict
import requests
import time
import re
import random
import pymysql
from retrying import retry

DEBUG = True
ONLY_WATCH = True

LEAGUE_DICT: Dict[int, str] = {
    1: "premier",
    2: "SerieA",
    3: "laliga",
    4: "Bundesliga",
    10: "FrenchLigue",
    231: "ChineseLeague"
}


head = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
                    AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/76.0.3809.132 Safari/537.36'
}

f = open("./data.txt", "w", encoding='utf-8')

def _result(result):
    return result is None


@retry(stop_max_attempt_number=5, wait_random_min=1000, wait_random_max=2000, retry_on_result=_result)
def request_response(web_site: str):
    rp = requests.get(web_site, headers=head, timeout=5)
    return rp


class MySQLHelper:
    conn_ = None

    @staticmethod
    def connect():
        MySQLHelper.conn_ = pymysql.connect(
            host="localhost",
            user="root",
            passwd="123456",
            db="dqd_data",
            charset="utf8"
        )
        print("MySQL Server connect successfully!")
        # cursor = MySQLHelper.get_cursor()
        # cursor.execute("SHOW TABLES;")
        # res = cursor.fetchall()
        # for tables in res:
        #     cursor.execute("truncate table " + tables[0])
        #     MySQLHelper.conn_.commit()

    @staticmethod
    def create_database():
        cursor = MySQLHelper.get_cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS dqd_data")
        MySQLHelper.conn_.commit()

    @staticmethod
    def create_team_table(table_name: str):
        cursor = MySQLHelper.get_cursor()
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
        # print(sql)
        ret = cursor.execute(sql)
        # ret == 0 means table already exists, clear the data before in table
        if ret == 0:
            cursor.execute("truncate table " + table_name)
        MySQLHelper.conn_.commit()

    @staticmethod
    def create_player_table(table_name: str):
        cursor = MySQLHelper.get_cursor()
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
        ret = cursor.execute(sql)
        if ret == 0:
            cursor.execute("truncate table " + table_name)
        MySQLHelper.conn_.commit()

    @staticmethod
    def get_cursor():
        return MySQLHelper.conn_.cursor()

    @staticmethod
    def insert_data(table_name: str, data_list: list):
        if ONLY_WATCH:
            return
        cursor = MySQLHelper.get_cursor()
        if table_name.find("player") != -1:
            sql = "INSERT INTO " + table_name + " VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            success_num = cursor.execute(sql, tuple(data_list))
            print("insert data {0} items successfully!".format(success_num))
        elif table_name.find("team") != -1:
            sql = "INSERT INTO " + table_name + " VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            success_num = cursor.execute(sql, tuple(data_list))
            print("insert data {0} items successfully!".format(success_num))
        MySQLHelper.conn_.commit()
        cursor.close()


# player or coach class
class Person:
    def __init__(self, chinese_name, english_name, club, nation, height, position,
                 age, weight, number, birthday, dominant_foot, photo_url, person_id):
        self.chinese_name_ = chinese_name
        self.english_name_ = english_name
        self.club_ = club
        self.nation_ = nation
        self.height_ = height if height != '' else 0
        self.position_ = position
        self.age_ = age if age != '' else 0
        self.weight_ = weight if weight != '' else 0
        self.number_ = number if number != '' else 0
        self.birthday_ = birthday
        self.dominant_foot_ = dominant_foot
        self.photo_url_ = photo_url
        self.person_id_ = person_id

    def to_string(self) -> str:
        return "{0}-{1}-{2}-{3}".format(self.chinese_name_, self.english_name_, self.age_, self.birthday_)

    def to_list(self) -> list:
        return [self.person_id_, self.chinese_name_, self.english_name_, self.club_,
                self.nation_, self.position_, self.age_, self.birthday_, self.number_, self.weight_, self.height_]


# football club team class
class Team:
    def __init__(self, logo_url, chinese_name, english_name, birth_year, country,
                 city, stadium, max_fans, telephone, email, address, team_id, league_id):
        self.logo_url_ = logo_url
        self.chinese_name_ = chinese_name
        self.english_name_ = english_name
        self.birth_year_ = birth_year if birth_year != '' else 0
        self.country_ = country
        self.city_ = city
        self.stadium_ = stadium
        self.max_fans_ = max_fans if max_fans != '' else 0
        self.telephone_ = telephone
        self.email_ = email
        self.address_ = address
        self.persons_ = []
        # team id in dqd
        self.id_ = team_id
        # league id where this team in, look LEAGUE_DICT
        self.league_id_ = league_id

    def get_team_info(self):
        web_site = "https://www.dongqiudi.com/team/" + self.id_ + ".html"
        response = request_response(web_site)
        html_code = response.text
        person_id_list = re.findall('person_id:"(.*?)"', html_code)
        for person_id in person_id_list:
            person_url = "https://www.dongqiudi.com/player/" + person_id + ".html"
            person_html_code = request_response(person_url).text
            re_str = '<div class="player-info" data-v-.*?>' \
                     '<div class="info-left" data-v-.*?>' \
                     '<p class="china-name" data-v-.*?>(.*?)<img .*? data-v-.*?></p> ' \
                     '<p class="en-name" data-v-.*?>(.*?)</p> ' \
                     '<div class="detail-info" data-v-.*?>' \
                     '<ul data-v-.*?>' \
                     '<li data-v-.*?><span data-v-.*?>俱乐部：</span>(.*?)</li> ' \
                     '<li data-v-.*?><span data-v-.*?>国   籍：</span>(.*?)</li> ' \
                     '<li data-v-.*?><span data-v-.*?>身   高：</span>(.*?)CM</li>' \
                     '</ul> ' \
                     '<ul class="second-ul" data-v-.*?>' \
                     '<li data-v-.*?><span data-v-.*?>位   置：</span>(.*?)</li> ' \
                     '<li data-v-.*?><span data-v-.*?>年   龄：</span>(.*?)岁</li> ' \
                     '<li data-v-.*?><span data-v-.*?>体   重：</span>(.*?)KG</li>' \
                     '</ul> ' \
                     '<ul data-v-.*?>' \
                     '<li data-v-.*?><span data-v-.*?>号   码：</span>(.*?)号</li> ' \
                     '<li data-v-.*?><span data-v-.*?>生   日：</span>(.*?)</li> ' \
                     '<li data-v-.*?><span data-v-.*?>惯用脚：</span>(.*?)</li>' \
                     '</ul>' \
                     '</div>' \
                     '</div> ' \
                     '<img src="(.*?)" alt class="player-photo" data-v-.*?>' \
                     '</div>'
            person_info_list = re.findall(re_str, person_html_code)
            if len(person_info_list) == 0 or len(person_info_list[0]) < 12:
                return
            person_obj = Person(person_info_list[0][0],
                                person_info_list[0][1],
                                person_info_list[0][2],
                                person_info_list[0][3],
                                person_info_list[0][4],
                                person_info_list[0][5],
                                person_info_list[0][6],
                                person_info_list[0][7],
                                person_info_list[0][8],
                                person_info_list[0][9],
                                person_info_list[0][10],
                                person_info_list[0][11],
                                person_id)
            MySQLHelper.insert_data(LEAGUE_DICT[self.league_id_] + "_player", person_obj.to_list())
            self.persons_.append(person_obj)
            print(person_obj.to_string())
            f.write(person_obj.to_string() + '\n')
            time.sleep(1)

    def to_string(self) -> str:
        return "{0}-{1}-{2}-{3}".format(self.chinese_name_, self.english_name_, self.city_, self.stadium_)

    def to_list(self) -> list:
        return [self.id_, self.chinese_name_, self.english_name_, self.country_, self.city_,
                self.stadium_, self.max_fans_, self.birth_year_, self.address_]


class League:
    def __init__(self, league_id: int):
        self.id_ = league_id
        self.team_list_ = []

    def request_team_data(self):
        # create the mysql table if it not exists, if already exists, clear the data before
        table_name = LEAGUE_DICT[self.id_] + "_team"
        MySQLHelper.create_team_table(table_name)
        MySQLHelper.create_player_table(LEAGUE_DICT[self.id_] + "_player")

        web_site = "https://www.dongqiudi.com/data/" + str(self.id_)
        response = request_response(web_site)
        html_code = response.text
        team_id_list = re.findall('team_id:"(.*?)"', html_code)
        if DEBUG:
            print(team_id_list)
        for team_id in team_id_list:
            team_web_site = "https://www.dongqiudi.com/team/" + team_id + ".html"
            if DEBUG:
                print(team_web_site)
            team_html_code = request_response(team_web_site).text
            re_str = '<div class="team-info" data-v-.*?>' \
                     '<img src="(.*?)" alt class="team-logo" data-v-.*?> ' \
                     '<div class="info-con" data-v-.*?>' \
                     '<p class="team-name" data-v-.*?>(.*?)<img src=.*? alt data-v-.*?></p> ' \
                     '<p class="en-name" data-v-.*?>(.*?)</p> ' \
                     '<p data-v-.*?>' \
                     '<span class="wid\d+" data-v-.*?><b data-v-.*?>成   立：</b>(.*?)</span>' \
                     '<span class="wid\d+" data-v-.*?><b data-v-.*?>国   家：</b>(.*?)</span>' \
                     '<span class="wid\d+" data-v-.*?><b data-v-.*?>城   市：</b>(.*?)</span>' \
                     '</p> ' \
                     '<p data-v-.*?>' \
                     '<span class="wid\d+" data-v-.*?><b data-v-.*?>主   场：</b>(.*?)</span>' \
                     '<span class="wid\d+" data-v-.*?><b data-v-.*?>容   纳：</b>(.*?)人</span>' \
                     '</p> ' \
                     '<p data-v-.*?>' \
                     '<span class="wid\d+" data-v-.*?><b data-v-.*?>电   话：</b>(.*?)</span>' \
                     '<span class="wid\d+" data-v-.*?><b data-v-.*?>邮   箱：</b>(.*?)</span>' \
                     '</p> ' \
                     '<p class="address" data-v-.*?><b data-v-.*?>地   址：</b>(.*?)' \
                     '</p>' \
                     '</div>' \
                     '</div>'
            team_info_list = re.findall(re_str, team_html_code)
            if len(team_info_list) == 0 or len(team_info_list[0]) < 11:
                return
            team_obj = Team(team_info_list[0][0],
                            team_info_list[0][1],
                            team_info_list[0][2],
                            team_info_list[0][3][0:4],
                            team_info_list[0][4],
                            team_info_list[0][5],
                            team_info_list[0][6],
                            team_info_list[0][7],
                            team_info_list[0][8],
                            team_info_list[0][9],
                            team_info_list[0][10],
                            team_id, self.id_)
            print(team_obj.to_string())
            MySQLHelper.insert_data(table_name, team_obj.to_list())
            f.write(team_obj.to_string() + '\n')

            team_obj.get_team_info()
            self.team_list_.append(team_obj)
            time.sleep(1)


if __name__ == "__main__":
    MySQLHelper.connect()
    for key, value in LEAGUE_DICT.items():
        league = League(key)
        league.request_team_data()
    MySQLHelper.conn_.close()
    f.close()
