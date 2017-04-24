# -*- coding: utf-8 -*-

import ParserSettings as sets

"""
subject_group - Название группы
subject_number - Номер пары
subject_day - День недели
subject_name - Название пары
subject_teacher - ФИО Преподавателя
subject_room - Кабинет
subject_subgroup - Подгруппа (0 - Все)
"""

def parse(db, filepath):
    prsng = sets.Parsing(filepath)
    if not (prsng.isFound):
        return False
    else:
        sets.SQL(prsng.subjects, db)
        errors = prsng.errorCheck()

        if (errors != True):
            return errors
        return True;

