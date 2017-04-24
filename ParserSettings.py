# -*- coding: utf-8 -*-

import xlrd, pymysql

class Parsing:

    subjects = []
    isFound = True

    def findKeyWords(self, value, subject, row, col):
        for word in value:
            if(word.find("неделя") != -1):
                if (word.find("Четная") != -1):
                    subject["subject_type_of_week"] = 1
                elif(word.find("Нечетная") != -1):
                    subject["subject_type_of_week"] = 2
                continue
            if(word.find("Подгруппа") != -1):
                if(word.find("1") != -1):
                    subject["subject_subgroup"] = 1
                elif(word.find("2") != -1):
                    subject["subject_subgroup"] = 2
                continue

            try:
                subject_name_split = word.split(".")
                subject_name = ""
                subject_room = word.split("-")
                subject_room = subject_room[len(subject_room)-1]

                if(len(subject_name_split) == 3):
                    subject_teacher_split = subject_name_split
                    teacher_firstname = subject_teacher_split[0].split(" ")
                    subject_teacher = teacher_firstname[len(teacher_firstname)-2] + " "
                    subject_teacher += teacher_firstname[len(teacher_firstname) - 1] + "."
                    subject_teacher += subject_teacher_split[1] + "."
                    subject_name_split = subject_name_split[0].split(" ")
                else:
                    teacher_temp = ""
                    for j in range(0, len(subject_name_split)-1):
                        if(j<len(subject_name_split)-2):
                            subject_name += " " + subject_name_split[j].strip()
                        else:
                            teacher_temp = subject_name_split[j].strip()
                    subject_name_split = subject_name.split(" ")
                    subject_teacher_split = subject_name
                    subject_teacher = subject_teacher_split.split(" ")
                    subject_teacher = subject_teacher[len(subject_teacher)-2] + " "
                    subject_teacher += subject_teacher_split[len(subject_teacher_split) - 1] + "."
                    subject_teacher += teacher_temp + "."
                    subject_name = ""

                for elems in range(0, len(subject_name_split) - 2):
                    subject_name += " " + subject_name_split[elems]
            except:
                subject_room = "Белая аудитория"
                subject_name = "Название предмета засекречено (Проверьте расписание)"
                subject_teacher = "ФСБ"
                subject["error_row"] = row
                subject["error_col"] = col

            subject["subject_room"] = subject_room.strip()
            subject["subject_name"] = subject_name.strip()
            subject["subject_teacher"] = subject_teacher.strip()

            self.subjects.append(subject)

    def explode(self, value):
        return value.split("\n")

    def daysToNumber(self, day):
        case = {"Понедельник": 0, "Вторник": 1, "Среда": 2, "Четверг": 3, "Пятница": 4, "Суббота": 5}
        return case.get(day)

    def errorCheck(self):
        errors = []
        for i in self.subjects:
            if 'error_row' in i:
                #print('Parsing: error_row - %d, error_col - %d' % (i["error_row"], i["error_col"]))
                errors.append({"error_row":(i["error_row"]+1),"error_col":(i["error_col"]+1)})

        if(len(errors) > 0):
            return errors;

        return True

    def __init__(self, filePath):
        try:
            rd = xlrd.open_workbook(filePath)
        except:
            self.isFound = False
            return
        sheet = rd.sheet_by_index(0)
        day = 0
        for i in range(2, sheet.ncols):
            subject_group = sheet.cell_value(6, i).split(" ")[0]
            for j in range(7, sheet.nrows):
                value = sheet.cell_value(j, i)
                subject_day = sheet.cell_value(j, 0)
                if (len(subject_day) != 0):
                    day = subject_day
                if(len(value)==0):
                    continue
                subject_number = int(sheet.cell_value(j, 1))
                subject = dict()
                subject["subject_type_of_week"] = 0
                subject["subject_subgroup"] = 0
                subject["subject_group"] = subject_group
                subject["subject_day"] = self.daysToNumber(day)
                subject["subject_number"] = subject_number
                self.findKeyWords(self.explode(value), subject, j, i)

class SQL:
    db = 0
    def getID(self, object_name, table_name):
        if not (type(object_name) == str):
            return object_name

        cursor = self.db.cursor()
        sql = "SELECT id FROM "+table_name+" WHERE name='"+object_name+"';"
        cursor.execute(sql)
        try:
            data = cursor.fetchall()
            sql = ""
            if(len(data)==0):
                sql += "INSERT INTO "+table_name+" VALUES(NULL, '"+object_name+"');"
                cursor.execute(sql)
                self.db.commit()
                cursor.close()
                return self.getID(object_name, table_name)
            else:
                cursor.close()
                return data[0][0]
        except:
            cursor.close()

    def changeSchedule(self, subjects):
        cursor = self.db.cursor()

        sql = "DELETE FROM general_schedule WHERE ("
        groups = []
        for i in subjects:
            if not (i["subject_group"]) in groups:
                groups.append(i["subject_group"])
        for i in groups:
            sql += "group_id="+str(i) + " or "
        sql = sql[:-4]
        sql += ");"
        cursor.execute(sql)
        self.db.commit()
        sql = ""
        for i in subjects:
            sql += "INSERT INTO general_schedule VALUES(NULL, %d, %d, %d, %d, %d, %d, %d, '%s');" % (i["subject_day"], i["subject_group"], i["subject_name"], i["subject_teacher"], i["subject_number"], i["subject_type_of_week"], i["subject_subgroup"], i["subject_room"])
        cursor.execute(sql)
        self.db.commit()
        cursor.close()

    def __init__(self, subjects, db):
        self.db = db
        for i in subjects:
            i["subject_name"] = self.getID(i["subject_name"], "subjects")
            i["subject_teacher"] = self.getID(i["subject_teacher"], "teachers")
            i["subject_group"] = self.getID(i["subject_group"], "groups")
        self.changeSchedule(subjects)
