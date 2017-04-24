import sqldata, pymysql
from session import Users, AntiCrash

database = 0

def isAdmin(id):
    return Users[id].isAdmin

def remAdmin(db, id):
    cursor = db.cursor()
    cursor.execute("delete from admins where chat_id="+str(id))
    db.commit()
    cursor.close()
    Users[id].isAdmin = False


def newAdmin(db, id):
    cursor = db.cursor()
    cursor.execute("select chat_id from admins where chat_id="+str(id))
    count = len(cursor.fetchall())
    if (count==0):
        cursor.execute("insert into admins values("+str(id)+", 0);")
        Users[id].isAdmin = True
        db.commit()
        cursor.close()
        return True
    cursor.close()
    return False

def init(db):
    cursor = db.cursor()
    cursor.execute("SELECT chat_id FROM admins;")
    for (chat_id) in cursor:
        AntiCrash(chat_id[0])
        Users[chat_id[0]].isAdmin = True
    cursor.close()
