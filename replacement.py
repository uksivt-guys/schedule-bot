# -*- coding: utf-8 -*-
import datetime

from sqldata import db

class STATES:
    SELECT_COURSE = 0
    SELECT_GROUP = 1
    SELECT_DAY = 2
    SELECT_SUBJECT = 3
    SELECT_REPLACE = 4
    SELECT_SUBGROUP = 5
    SELECT_ROOM = 6
    RETURN = 10
    END = 9
    UPDATED = 11

class Change:
    day = 0
    subject = 0
    teacher = 0
    number = 0
    group_type = 0
    room = 0
    group = 0
    def __init__(self, day, subject, teacher, number, group_type, room, group):
        self.day = day
        self.subject = subject
        self.teacher = teacher
        self.number = number
        self.group_type = group_type
        self.room = room
        self.group = group

class Replacement:
    db = 0
    course = 0
    group = 0
    day = 0
    number = 0
    replace = 0
    subgroup = 0
    room = 0
    teacher = 0
    all_replacements = []
    state = STATES.SELECT_COURSE

    def cursor(self):
        return self.db.cursor()

    def getText(self):
        if(self.state==STATES.SELECT_COURSE):
            return "Выберете курс"
        if(self.state==STATES.SELECT_GROUP):
            return "Выберете группу"
        elif(self.state==STATES.SELECT_DAY):
            return "Выберете день недели"
        elif(self.state==STATES.SELECT_SUBJECT):
            return "Выберете предмет"
        elif(self.state==STATES.SELECT_REPLACE):
            return "Выберете заменяемый предмет"
        elif(self.state==STATES.SELECT_SUBGROUP):
            return "Выберете подгруппу"
        elif (self.state == STATES.SELECT_ROOM):
            return "Введите аудиторию"
        elif (self.state == STATES.UPDATED):
            return "Расписание обновлено!"

    def action(self, key, value):
        if(key==STATES.SELECT_COURSE):
            self.state = STATES.SELECT_GROUP
            self.course = value
        if(key==STATES.SELECT_GROUP):
            self.state = STATES.SELECT_DAY
            self.group = value
        if(key==STATES.SELECT_DAY):
            self.state = STATES.SELECT_SUBJECT
            self.day = value
        if(key==STATES.SELECT_SUBJECT):
            self.state = STATES.SELECT_REPLACE
            self.number = value
        if(key==STATES.SELECT_REPLACE):
            self.replace = value
            self.teacher = self.getTeacher()
            if not (self.replace==0):
                if(self.isSubgroups()):
                    self.state = STATES.SELECT_SUBGROUP
                else:
                    self.state = STATES.SELECT_ROOM
        if(key==STATES.SELECT_SUBGROUP):
            self.subgroup = value
            self.state = STATES.SELECT_ROOM
        if(key==STATES.END):
            self.checkForDublicates()
            for i in self.all_replacements:
                self.addReplacement(i)
            self.all_replacements = []
            self.state = STATES.UPDATED
        if(key==STATES.RETURN):
            self.state -= 1
            if (self.replace!=0):
                if not (self.isSubgroups()):
                    self.state -= 1

        return self.state

    def checkForDublicates(self):
        new_array = []
        for i in range(0, len(self.all_replacements)):
            for j in range((i+1), len(self.all_replacements)):
                if(self.all_replacements[i].day.weekday() == self.all_replacements[j].day.weekday()):
                    if(self.all_replacements[i].number==self.all_replacements[j].number):
                        new_array.append(self.all_replacements[j])
        if(len(self.all_replacements) > 1):
            self.all_replacements = new_array

    def getDate(self, day):
        weekday = datetime.datetime.today().weekday()
        days = 0
        day = self.getWeekDay(day)
        while not (weekday == day):
            days += 1
            if(weekday == 6):
                weekday = -1
            weekday += 1
        return (datetime.datetime.today() + datetime.timedelta(days=days)).date()

    def addReplacement(self, repl):
        cursor = self.cursor()
        cursor.execute("select * from replacements where day='%s' and lesson_number=%d;" % (repl.day, repl.number) )
        data = cursor.fetchall()
        #print(cursor.rowcount)
        if (len(data) == 0):
            cursor.execute("insert into replacements values(null, '%s', %d, %d, %d, %d, '%s', %d);" % (repl.day, repl.subject, repl.teacher, repl.number, repl.group_type, repl.room, repl.group))
        else:
            cursor.execute("update replacements set subject_id=%d, teacher_id=%d, group_type=%d, room='%s', group_id=%d where day='%s' and lesson_number=%d;" % (repl.subject, repl.teacher, repl.group_type, repl.room, repl.group, repl.day, repl.number) )
        self.db.commit()
        cursor.close()

    def setRoom(self, room):
        self.room = room
        self.state = STATES.SELECT_SUBJECT
        c = Change(self.getDate(self.day), self.replace, self.teacher, self.number, self.subgroup, self.room, self.getGroup())
        self.all_replacements.append(c)
        self.replace = 0
        self.subgroup = 0
        self.room = 0
        self.teacher = 0

    def is_typing_room(self):
        return self.state==STATES.SELECT_ROOM

    def getWeekDay(self, day):
        if(day=="Понедельник"):
            day = 0
        elif(day=="Вторник"):
            day = 1
        elif(day=="Среда"):
            day = 2
        elif(day=="Четверг"):
            day = 3
        elif(day=="Пятница"):
            day = 4
        elif(day=="Суббота"):
            day = 5
        return day

    def getTeacher(self):
        if (self.replace == 0):
            self.teacher = 0
            self.setRoom(0)
            return 0
        cursor = self.cursor()
        cursor.execute("select teacher_id from general_schedule where subject_id=%d and group_id=%d;" % (self.replace, self.getGroup()))
        data = cursor.fetchall()[0][0]
        cursor.close()
        return data

    def isSubgroups(self):
        if (self.replace == 0):
            return False
        cursor = self.cursor()
        cursor.execute("select group_type from general_schedule where subject_id=%d" % (self.replace))
        data = cursor.fetchall()
        for i in data:
            if(i[0]==1):
                cursor.close()
                return True
        cursor.close()
        return False

    def getGroup(self):
        cursor = self.cursor()
        cursor.execute("select id from groups where name='%s';"%(self.group))
        data = cursor.fetchall()
        cursor.close()
        return data[0][0]

    def getAllSubjects(self):
        cursor = self.cursor()
        cursor.execute("select subject_id from general_schedule where group_id=%d" % (self.getGroup()))
        data = cursor.fetchall()
        subjects = dict()
        for i in data:
            cursor.execute("select name from subjects where id=%d" % (i[0]))
            subject = cursor.fetchall()[0][0]
            subjects[i[0]] = subject
        subjects[0] = "-"
        cursor.close()
        return subjects

    def getSubject(self, id):
        cursor = self.cursor()
        cursor.execute("select name from subjects where id=%d" % (id))
        name = cursor.fetchall()[0][0]
        return name

    def getChanges(self, names):
        cursor = self.cursor()
        cursor.execute("select subject_id, lesson_number from replacements where day='%s' and group_id=%s;" % (self.getDate(self.day), self.getGroup()))
        data = cursor.fetchall()


        for replacement_item in range(0, len(data)):
            lesson_number = data[replacement_item][1]
            lesson_subject = data[replacement_item][0]
            if lesson_number in names:
                names[lesson_number] = self.getSubject(lesson_subject) + " (" \
                                                 + names[lesson_number] + ")"
            else:
                names[lesson_number] = self.getSubject(lesson_subject) + " ( — )"
        cursor.close()

    def getSubjectsNames(self):
        cursor = self.cursor()
        cursor.execute("select subject_id, lesson_number from general_schedule where weekday=%d and group_id=%d;" % (self.getWeekDay(self.day), self.getGroup()))
        data = cursor.fetchall()
        names = dict()
        for i in range(0, len(data)):
            names[data[i][1]] = self.getSubject(data[i][0])
        self.getChanges(names)
        cursor.close()
        return names

    def getGroupsNames(self):
        cursor = self.cursor()
        cursor.execute("select name from groups where left(name, 1)='%d';" % (self.course))
        data = cursor.fetchall()
        cursor.close()
        return data

    def __init__(self):
        self.db = db