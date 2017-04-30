# -*- coding: utf-8 -*-

import pymysql
from keys import KeysDB

def init(host, user, pswd, db):
    return pymysql.connect(host, user, pswd, db, charset="utf8")

db = init(KeysDB.HOST, KeysDB.USER, KeysDB.PASSWORD, KeysDB.DATABASE)
