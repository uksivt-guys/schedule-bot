# -*- coding: utf-8 -*-

from sqldata import db

def sendGroupMessage(bot, send_msg, group):
    cursor = db.cursor()
    cursor.execute("select chat_id from subscribe_group where group_id=%d;" % (group) )
    ids = cursor.fetchall()
    for i in ids:
        try:
            bot.send_message(i[0], send_msg)
        except:
            pass
    cursor.close()

def getGroups():
    cursor = db.cursor()
    cursor.execute("select group_id from general_schedule")
    data = cursor.fetchall()
    groups = dict()
    for i in data:
        cursor.execute("select name from groups where id=%d;" % (i[0]) )
        name = cursor.fetchall()
        groups[i[0]] = name[0][0]

    cursor.close()
    return groups