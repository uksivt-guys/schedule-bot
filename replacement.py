# -*- coding: utf-8 -*-

import datetime

class Replacement:
    group = 0
    db = 0
    number = 0
    subgroup = 0
    subjects = 0
    teacher = 0
    replace_subject = 0
    room = False
    all_subjects = []
    replacements_subjects = dict()

    def getGroup(self, group):
        sql = "select id from groups where name='%s';" % (group)
        cursor = self.db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        if(len(data)>0):
            id = data[0][0]
        else:
            id = False
        cursor.close()
        return id

    def send_to(self, id, bot):
        cursor = self.db.cursor()
        test = datetime.datetime.now()
        test = test.replace(day=test.day+1)
        if(test.weekday()==6):
            test.replace(day=test.day+1)
        test = test.strftime('%Y-%m-%d')
        text = "Расписание на %s:\r\n" % (test)
        subjects = []
        for i in range(0, 7):
            try:
                name = self.replacements_subjects[i][3]
                teacher = self.replacements_subjects[i][0]
                room = self.replacements_subjects[i][1]
                subgroup = self.replacements_subjects[i][2]
                sql = "select name from teachers where id=%d" % (teacher)
                cursor.execute(sql)
                data = cursor.fetchall()
                try:
                    teacher = data[0][0]
                except:
                    teacher = "0"
                sql = "select name from subjects where id=%d" % (name)
                cursor.execute(sql)
                data = cursor.fetchall()
                name = data[0][0]
                if(subgroup == 0):
                    subgroup = ""
                elif(subgroup == 1):
                    subgroup = "Подгруппа №1"
                else:
                    subgroup = "Подгруппа №2"
                text += "%d. %s - %s (%s) %s\r\n" % (i, name, teacher, room, subgroup)
            except:
                try:
                    name = self.subjects[i]
                    teacher = ""
                    day_of_week = datetime.datetime.now().weekday() + 1
                    if (day_of_week > 5):
                        day_of_week = 0
                    sql = "select teacher_id, room, group_type from general_schedule where (lesson_number=%d and group_id=%d and weekday=%d) order by lesson_number asc;" % (i, self.group, day_of_week)
                    cursor.execute(sql)
                    data = cursor.fetchall()
                    room = data[0][1]
                    subgroup = data[0][2]
                    teacher = data[0][0]
                    sql = "select name from teachers where (id=%d)" % (teacher)
                    cursor.execute(sql)
                    data = cursor.fetchall()
                    teacher = data[0][0]
                    if (subgroup == 0):
                        subgroup = ""
                    elif (subgroup == 1):
                        subgroup = "1 подгруппа"
                    else:
                        subgroup = "2 подгруппа"
                    text += "%d. %s - %s (%s) %s\r\n" % (i, name, teacher, room, subgroup)
                except:
                    text += "%d. Нет пары\r\n" % (i)

        try:
            bot.send_message(id, text)
        except:
            pass
        cursor.close()

    def PublishReplacements(self, bot):
        cursor = self.db.cursor()
        sql = "select chat_id from subscribe_group where (group_id=%d);" % (self.group)
        cursor.execute(sql)
        data = cursor.fetchall()

        for i in data:
            self.send_to(i[0], bot)
        cursor.close()

    def getReplacements(self):
        test = datetime.datetime.now()
        test = test.replace(day=test.day + 1)
        if (test.weekday() == 6):
            test.replace(day=test.day + 1)
        test = test.strftime('%Y-%m-%d')
        cursor = self.db.cursor()
        sql = "select lesson_number, subject_id from replacements where (day='%s' and group_id=%d) order by 'lesson_number' asc;" % (
        test, self.group)
        cursor.execute(sql)
        data = cursor.fetchall()
        if (len(data) > 0):
            for i in data:
                sql = "select name from subjects where id=%d" % (i[1])
                cursor.execute(sql)
                data2 = cursor.fetchall()
                self.subjects[int(i[0])] = data2[0][0]
            cursor.close()
            return self.subjects
        else:
            cursor.close()
            return False

    def getSchedule(self):
        day_of_week = datetime.datetime.now().weekday()+1
        if(day_of_week>5):
            day_of_week=0
        cursor = self.db.cursor()
        sql = "select lesson_number, subject_id from general_schedule where (weekday=%d and group_id=%d) order by 'lesson_number' asc;" % (day_of_week, self.group)
        cursor.execute(sql)
        data = cursor.fetchall()
        self.subjects = dict()
        if(len(data)>0):
            for i in data:
                sql = "select name from subjects where id=%d" % (i[1])
                cursor.execute(sql)
                data2 = cursor.fetchall()
                self.subjects[int(i[0])] = data2[0][0]
            for i in range(0, 7):
                if i in self.subjects:
                    continue
                else:
                    self.subjects[i] = "Нет пары"
            cursor.close()
            self.getReplacements()
            return self.subjects
        else:
            cursor.close()
            return False

    def getSubjects(self):
        cursor = self.db.cursor()
        sql = "select subject_id from general_schedule where (group_id=%d);" % (self.group)
        cursor.execute(sql)
        data = cursor.fetchall()
        if len(data) > 0:
            for i in data:
                sql = "select id, name from subjects where id=%d;" % (i[0])
                cursor.execute(sql)
                data2 = cursor.fetchall()
                self.all_subjects.append({'0':data2[0][0], '1':data2[0][1]})
        cursor.close()
        return self.all_subjects

    def getTeacher(self):
        cursor = self.db.cursor()
        sql = "select teacher_id from general_schedule where (group_id=%d and subject_id=%d and group_type=%d) limit 1;" % (self.group, self.replace_subject, self.subgroup)
        cursor.execute(sql)
        data = cursor.fetchall()
        if(len(data) == 0):
            sql = "select teacher_id from general_schedule where (group_id=%d and subject_id=%d) limit 1;" % (self.group, self.replace_subject)
            cursor.execute(sql)
            data = cursor.fetchall()
            if(len(data)==0):
                return False
        cursor.close()
        for i in data:
            self.teacher = i[0]
            return self.teacher

    def intoBase(self):
        cursor = self.db.cursor()
        test = datetime.datetime.now()
        test = test.replace(day=test.day+1)
        if(test.weekday()==6):
            test.replace(day=test.day+1)
        test = test.strftime('%Y-%m-%d')
        sql = "insert into replacements values(null, '%s', %d, %d, %d, %d, '%s', %d);" % (test, self.replace_subject, self.teacher, int(self.number), self.subgroup, self.room, self.group)
        cursor.execute(sql)
        self.db.commit()
        self.replacements_subjects[int(self.number)] = [self.teacher, self.room, self.subgroup, self.replace_subject]
        cursor.close()

    def __init__(self, db, group):
        self.db = db
        self.group = self.getGroup(group)